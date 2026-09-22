"""Publish immutable catalogue assets without changing the latest app release."""
import base64,hashlib,json,os,pathlib,urllib.request,urllib.parse,urllib.error
folder=pathlib.Path('catalogue');envelope=json.loads((folder/'latest-v2.json').read_text());spec=json.loads(base64.b64decode(envelope['payload']))
import subprocess,re
payload=base64.b64decode(envelope['payload']);signature=base64.b64decode(envelope['signature'])
import tempfile
with tempfile.TemporaryDirectory() as temporary:
 p=pathlib.Path(temporary);(p/'payload').write_bytes(payload);(p/'signature').write_bytes(signature)
 subprocess.run(['openssl','dgst','-sha256','-verify','update-public.pem','-signature',str(p/'signature'),str(p/'payload')],check=True)
assert spec['schema']==2 and 1<=len(spec['parts'])<=128 and 1<=spec['count']<=500000
assert sum(x['bytes'] for x in spec['parts'])==spec['bytes']<=512*1024*1024
assert sum(x['count'] for x in spec['parts'])==spec['count']
files=[];seen=set()
for i,part in enumerate(spec['parts']):
 assert part['file']==f"catalogue-{spec['timestamp']}-{i:03d}.json" and 1<=part['bytes']<=4*1024*1024
 file=folder/part['file'];data=file.read_bytes()
 assert len(data)==part['bytes'] and hashlib.sha256(data).hexdigest()==part['sha256']
 content=json.loads(data);assert content['schema']==1 and content['timestamp']==spec['timestamp'] and len(content['entries'])==part['count']
 for row in content['entries']:
  identity=row['media']['id'];assert identity not in seen;seen.add(identity)
 files.append(file)
# The light index is optional for old releases, signed independently.
compact_manifest=folder/'latest-v3.json'
if compact_manifest.exists():
 import gzip
 env3=json.loads(compact_manifest.read_text());raw3=base64.b64decode(env3['payload'])
 with tempfile.TemporaryDirectory() as temporary:
  p=pathlib.Path(temporary);(p/'payload').write_bytes(raw3);(p/'signature').write_bytes(base64.b64decode(env3['signature']))
  subprocess.run(['openssl','dgst','-sha256','-verify','update-public.pem','-signature',str(p/'signature'),str(p/'payload')],check=True)
 index=json.loads(raw3);assert index['schema']==3 and index['timestamp']==spec['timestamp'] and index['count']==spec['count']
 assert 1<=len(index['parts'])<=128 and sum(p['bytes'] for p in index['parts'])==index['bytes']
 ids=set()
 for part in index['parts']:
  assert re.fullmatch(r'catalogue-\d{13}-index-\d{3}\.json\.gz',part['file'])
  file=folder/part['file'];data=file.read_bytes()
  assert len(data)==part['bytes']<=4*1024*1024 and hashlib.sha256(data).hexdigest()==part['sha256']
  raw=gzip.decompress(data);assert len(raw)==part['uncompressedBytes']<=16*1024*1024
  content=json.loads(raw);assert content['schema']==1 and content['timestamp']==0 and len(content['entries'])==part['count']
  for row in content['entries']:
   assert row['media']['id'] not in ids;ids.add(row['media']['id'])
  files.append(file)
 assert len(ids)==index['count']
 files.append(compact_manifest)
repo=os.environ['GH_REPOSITORY'];token=os.environ['GH_TOKEN'];tag='catalogue-'+str(spec['timestamp'])
def api(endpoint,method='GET',body=None,file=None):
 url=endpoint if endpoint.startswith('https://') else 'https://api.github.com/repos/'+repo+endpoint
 assert url.startswith(('https://api.github.com/','https://uploads.github.com/'))
 data=file.read_bytes() if file else json.dumps(body).encode() if body is not None else None
 headers={'Authorization':'Bearer '+token,'User-Agent':'TuaoTV-catalogue','Accept':'application/vnd.github+json','Content-Type':'application/octet-stream' if file else 'application/json'}
 with urllib.request.urlopen(urllib.request.Request(url,data=data,headers=headers,method=method),timeout=180) as r:return json.load(r)
try:release=api('/releases/tags/'+tag)
except urllib.error.HTTPError as e:
 if e.code!=404:raise
 release=next((r for r in api('/releases?per_page=100') if r['tag_name']==tag),None)
 if release is None:release=api('/releases','POST',{'tag_name':tag,'name':'节目列表 '+str(spec['timestamp']),'body':'节目列表数据更新，客户端自动检查。不是 App 安装包。\n\n官网：https://tuaotv.com/catalogue/latest-v2.json','draft':True,'prerelease':True,'make_latest':'false'})
assets={a['name']:a for a in api('/releases/'+str(release['id'])+'/assets')}
for asset in files+[folder/'latest-v2.json']:
 if asset.name in assets:
  assert assets[asset.name]['digest']=='sha256:'+hashlib.sha256(asset.read_bytes()).hexdigest();continue
 api(release['upload_url'].split('{')[0]+'?name='+urllib.parse.quote(asset.name),'POST',file=asset)
api('/releases/'+str(release['id']),'PATCH',{'draft':False,'prerelease':True,'make_latest':'false'})
print('Published',tag)
