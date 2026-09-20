"""Fetch known public installers, verify bytes, then publish a complete GitHub release."""
import concurrent.futures, hashlib, json, os, pathlib, time, urllib.request
from urllib.parse import quote
spec = json.loads(pathlib.Path('installers.json').read_text())
version = spec['version']
repo = os.environ['GH_REPOSITORY']
token = os.environ['GH_TOKEN']
folder = pathlib.Path('installers')
folder.mkdir(exist_ok=True)
def download(entry):
    target = folder / entry['name']
    assert target.name == entry['name']
    for attempt in range(3):
        try:
            digest = hashlib.sha256()
            with target.open('wb') as output:
                for part in entry.get('parts', [entry]):
                    assert part['url'].startswith('https://tuaotv.com/downloads/')
                    part_digest = hashlib.sha256()
                    size = 0
                    request = urllib.request.Request(part['url'], headers={'User-Agent': 'TuaoTV-release'})
                    with urllib.request.urlopen(request, timeout=90) as response:
                        while block := response.read(1024*1024):
                            size += len(block)
                            assert size <= part['bytes'], 'Oversized response'
                            part_digest.update(block); digest.update(block); output.write(block)
                    assert size == part['bytes'] and part_digest.hexdigest() == part['sha256'], 'Part checksum mismatch'
            assert target.stat().st_size == entry['bytes'] and digest.hexdigest() == entry['sha256'], 'Installer checksum mismatch'
            print('Verified', target.name, flush=True)
            return target
        except Exception:
            if attempt == 2: raise
            time.sleep(3)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    files = list(pool.map(download, spec['files']))
checks = pathlib.Path('SHA256SUMS.txt')
expected = dict(line.split('  ', 1)[::-1] for line in checks.read_text().splitlines())
for entry in spec['files']: assert expected[entry['name']] == entry['sha256']
files.append(checks)
def api(path, method='GET', body=None, binary=None):
    url = path if path.startswith('https://') else 'https://api.github.com/repos/' + repo + path
    assert url.startswith(('https://api.github.com/', 'https://uploads.github.com/'))
    headers = {'Authorization': 'Bearer ' + token, 'User-Agent': 'TuaoTV-release', 'Accept': 'application/vnd.github+json'}
    data = None
    if binary is not None:
        data = binary.read_bytes(); headers['Content-Type'] = 'application/octet-stream'
    elif body is not None:
        data = json.dumps(body).encode(); headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=180) as response:
        raw = response.read()
        return json.loads(raw) if raw else None
releases = api('/releases?per_page=100')
release = next((r for r in releases if r['tag_name'] == 'v'+version or (r['draft'] and r['name'] == '土澳TV '+version)), None)
notes = '请选择对应平台安装包，点击后由浏览器直接下载。\n\n' + '\n'.join('- '+e['name'] for e in spec['files']) + '\n\nSHA256SUMS.txt 提供校验值。此仓库仅用于安装包分发，Source code 不是应用安装包。\n\n官网：https://tuaotv.com'
if release is None:
    release = api('/releases', 'POST', {'tag_name':'v'+version, 'name':'土澳TV '+version, 'body':notes, 'draft':True, 'prerelease':False})
elif release['draft']:
    release = api('/releases/'+str(release['id']), 'PATCH', {'tag_name':'v'+version, 'name':'土澳TV '+version, 'body':notes})
existing = {a['name']:a for a in api('/releases/'+str(release['id'])+'/assets?per_page=100')}
for file in files:
    digest = 'sha256:'+hashlib.sha256(file.read_bytes()).hexdigest()
    asset = existing.get(file.name)
    if asset and asset['state'] == 'uploaded':
        assert asset['size'] == file.stat().st_size and asset.get('digest') == digest, 'Existing asset differs: '+file.name
        print('Already uploaded', file.name, flush=True)
        continue
    assert release['draft'], 'Never change an already published release'
    if asset: api('/releases/assets/'+str(asset['id']), 'DELETE')  # incomplete draft upload only
    asset = api(release['upload_url'].split('{')[0]+'?name='+quote(file.name), 'POST', binary=file)
    assert asset['state'] == 'uploaded' and asset['size'] == file.stat().st_size and asset.get('digest') == digest
    print('Uploaded', file.name, flush=True)
release = api('/releases/'+str(release['id']), 'PATCH', {'draft':False, 'prerelease':False, 'make_latest':'true'})
print('Published', release['html_url'], flush=True)
