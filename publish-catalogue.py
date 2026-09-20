"""Publish immutable catalogue assets without changing the latest app release."""
import base64,hashlib,json,os,pathlib,urllib.request,urllib.parse,urllib.error
folder=pathlib.Path('catalogue');envelope=json.loads((folder/'latest.json').read_text());spec=json.loads(base64.b64decode(envelope['payload']))
file=folder/spec['file'];assert file.name==spec['file'] and file.name.startswith('catalogue-')
assert file.stat().st_size==spec['bytes'] and hashlib.sha256(file.read_bytes()).hexdigest()==spec['sha256']
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
 if release is None:release=api('/releases','POST',{'tag_name':tag,'name':'节目列表 '+str(spec['timestamp']),'body':'节目列表数据更新，客户端自动检查。不是 App 安装包。\n\n官网：https://tuaotv.com/catalogue/latest.json','draft':True,'prerelease':True,'make_latest':'false'})
assets={a['name']:a for a in api('/releases/'+str(release['id'])+'/assets')}
for asset in [file,folder/'latest.json']:
 if asset.name in assets:
  assert assets[asset.name]['digest']=='sha256:'+hashlib.sha256(asset.read_bytes()).hexdigest();continue
 api(release['upload_url'].split('{')[0]+'?name='+urllib.parse.quote(asset.name),'POST',file=asset)
api('/releases/'+str(release['id']),'PATCH',{'draft':False,'prerelease':True,'make_latest':'false'})
print('Published',tag)
