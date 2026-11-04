"""Weekly full catalogue plus immutable, ordered patches (signed manifest schema 4).

No network, git or credentials here; callers publish assets before promoting the pointer.
"""
import base64
import gzip
import hashlib
import json
import io
import re

WEEK = 7 * 24 * 60 * 60 * 1000
MAX_DELTAS = 256


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def digest(rows):
    return hashlib.sha256(canonical(sorted(rows, key=lambda r: r['media']['id']))).hexdigest()


def keyed(rows):
    result = {}
    for row in rows:
        identity = row['media']['id']
        if not isinstance(identity, str) or not identity.strip() or identity in result:
            raise ValueError('Invalid/duplicate programme ID')
        result[identity] = row
    if not 1 <= len(result) <= 500000:
        raise ValueError('Invalid catalogue count')
    return result


def read_part(folder, part):
    if not re.fullmatch(r'catalogue-\d{13}-(?:full|delta)-\d{3}\.json\.gz', part['file']):
        raise ValueError('Invalid catalogue path')
    if not 1 <= part['bytes'] <= 4 * 1024 * 1024 or not 1 <= part['uncompressedBytes'] <= 16 * 1024 * 1024:
        raise ValueError('Invalid catalogue size')
    if (folder / part['file']).stat().st_size != part['bytes']:
        raise ValueError('Catalogue size mismatch')
    data = (folder / part['file']).read_bytes()
    if len(data) != part['bytes'] or hashlib.sha256(data).hexdigest() != part['sha256']:
        raise ValueError('Catalogue checksum mismatch')
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
        raw = stream.read(16 * 1024 * 1024 + 1)
    if len(raw) != part['uncompressedBytes'] or len(raw) > 16 * 1024 * 1024:
        raise ValueError('Invalid expanded catalogue')
    return json.loads(raw)


def materialize(folder, manifest):
    """Reconstruct and verify the current published state, including deletions."""
    if manifest['schema'] != 4:
        raise ValueError('Invalid catalogue schema')
    base = manifest['base']
    rows = []
    for part in base['parts']:
        content = read_part(folder, part)
        if content['schema'] != 1 or content['timestamp'] != 0 or len(content['entries']) != part['count']:
            raise ValueError('Invalid full part')
        rows.extend(content['entries'])
    state = keyed(rows)
    stamp = base['timestamp']
    fingerprint = digest(list(state.values()))
    if len(state) != base['count'] or fingerprint != base['contentSha256']:
        raise ValueError('Invalid full catalogue')
    for delta in manifest['deltas']:
        if delta['fromTimestamp'] != stamp or delta['fromSha256'] != fingerprint or delta['timestamp'] <= stamp:
            raise ValueError('Broken catalogue chain')
        seen = set(); upserts = deletes = 0
        for part in delta['parts']:
            patch = read_part(folder, part)
            if any(patch[k] != v for k, v in [('schema', 4), ('baseTimestamp', base['timestamp']), ('fromTimestamp', stamp), ('timestamp', delta['timestamp'])]):
                raise ValueError('Invalid patch version')
            if len(patch['entries']) + len(patch['removed']) != part['count']:
                raise ValueError('Invalid patch count')
            for row in patch['entries']:
                identity = row['media']['id']
                if identity in seen: raise ValueError('Duplicate operation')
                seen.add(identity); state[identity] = row; upserts += 1
            for identity in patch['removed']:
                if identity in seen or identity not in state: raise ValueError('Invalid deletion')
                seen.add(identity); del state[identity]; deletes += 1
        fingerprint = digest(list(state.values())); stamp = delta['timestamp']
        if (upserts, deletes, len(state), fingerprint) != (delta['upsertCount'], delta['deleteCount'], delta['count'], delta['contentSha256']):
            raise ValueError('Invalid patch result')
    if (stamp, len(state), fingerprint) != (manifest['timestamp'], manifest['count'], manifest['contentSha256']):
        raise ValueError('Invalid catalogue head')
    return [state[k] for k in sorted(state)]


def write_parts(folder, stamp, kind, entries, removed=(), header=None):
    """Bounded parts; each programme operation stays in exactly one part."""
    batches = []; current = []; size = 0
    operations = [(True, row) for row in entries] + [(False, identity) for identity in removed]
    for operation in operations:
        n = len(canonical(operation[1])) + 1
        if current and size + n > 3 * 1024 * 1024:
            batches.append(current); current = []; size = 0
        current.append(operation); size += n
    if current: batches.append(current)
    if not 1 <= len(batches) <= 128: raise ValueError('Too many catalogue parts')
    parts = []
    for i, batch in enumerate(batches):
        body = dict(header or {'schema': 1, 'timestamp': 0})
        body['entries'] = [row for is_row, row in batch if is_row]
        if kind == 'delta': body['removed'] = [row for is_row, row in batch if not is_row]
        raw = canonical(body); data = gzip.compress(raw, mtime=0)
        if len(raw) > 16 * 1024 * 1024 or len(data) > 4 * 1024 * 1024:
            raise ValueError('Catalogue part too large')
        name = f'catalogue-{stamp}-{kind}-{i:03d}.json.gz'
        path = folder / name
        if path.exists() and path.read_bytes() != data: raise ValueError('Immutable asset collision')
        path.write_bytes(data)
        parts.append(dict(file=name, bytes=len(data), uncompressedBytes=len(raw), count=len(batch), sha256=hashlib.sha256(data).hexdigest()))
    return parts


def build(folder, rows, stamp, old=None):
    """Return (manifest, new asset names, full rollover); None means no publication."""
    state = keyed(rows); rows = [state[k] for k in sorted(state)]
    fingerprint = digest(rows)
    previous = keyed(materialize(folder, old)) if old else {}
    rollover = not old or stamp - old['base']['timestamp'] >= WEEK or len(old['deltas']) >= MAX_DELTAS
    if old and old['contentSha256'] == fingerprint and not rollover: return None
    if old: stamp = max(stamp, old['timestamp'] + 1)
    if rollover:
        parts = write_parts(folder, stamp, 'full', rows)
        base = dict(schema=3, timestamp=stamp, count=len(rows), contentSha256=fingerprint, bytes=sum(p['bytes'] for p in parts), parts=parts)
        deltas = []
    else:
        changed = [row for k, row in state.items() if k not in previous or canonical(row) != canonical(previous[k])]
        removed = sorted(previous.keys() - state.keys())
        header = dict(schema=4, timestamp=stamp, fromTimestamp=old['timestamp'], baseTimestamp=old['base']['timestamp'])
        parts = write_parts(folder, stamp, 'delta', changed, removed, header)
        delta = dict(timestamp=stamp, fromTimestamp=old['timestamp'], fromSha256=old['contentSha256'], contentSha256=fingerprint, count=len(rows), upsertCount=len(changed), deleteCount=len(removed), bytes=sum(p['bytes'] for p in parts), parts=parts)
        base = old['base']; deltas = old['deltas'] + [delta]
    manifest = dict(schema=4, timestamp=stamp, count=len(rows), contentSha256=fingerprint, base=base, deltas=deltas)
    # Keep the signed envelope below existing client bounds; compact early if needed.
    if len(canonical(manifest)) > 480000:
        return build(folder, rows, stamp, None)
    return manifest, [p['file'] for p in parts], rollover


def envelope(manifest, sign):
    payload = canonical(manifest)
    return json.dumps(dict(payload=base64.b64encode(payload).decode(), signature=base64.b64encode(sign(payload)).decode()), separators=(',', ':')) + '\n'
