#!/usr/bin/env python3
"""Validate and synchronize local conference paper data without external packages."""
import argparse, json, pathlib, re, sys
from urllib.parse import urlparse
ROOT = pathlib.Path(__file__).resolve().parent
COLLECTION_FIELDS = {'conference','year','name','scope','source_url','papers'}
PAPER_FIELDS = {'id','title','title_zh','authors','abstract','abstract_zh','topics','kind','track','links','abstract_source','search_extra'}
STRING_FIELDS = PAPER_FIELDS - {'topics','links'}

def clean(value):
    if isinstance(value, str): return value.strip()
    if isinstance(value, list): return [clean(x) for x in value]
    if isinstance(value, dict): return {k:clean(v) for k,v in value.items()}
    return value

def validate(data):
    errors=[]
    def fail(path, message): errors.append(f'{path}: {message}')
    def url(value):
        try:
            u=urlparse(value)
            return u.scheme in ('http','https') and bool(u.netloc) and not any(c.isspace() for c in value)
        except (ValueError,TypeError): return False
    if not isinstance(data,dict) or set(data)!={'schema_version','collections'}:
        return ['根对象必须包含且仅包含 schema_version 和 collections。']
    if type(data['schema_version']) is not int or data['schema_version']!=1: fail('schema_version','必须为整数 1')
    if not isinstance(data['collections'],list): return errors+['collections 必须为数组。']
    keys=set()
    for ci,c in enumerate(data['collections']):
        cp=f'collections[{ci}]'
        if not isinstance(c,dict) or set(c)!=COLLECTION_FIELDS: fail(cp,'会议字段不完整或存在额外字段'); continue
        if not isinstance(c['conference'],str) or not re.fullmatch(r'[A-Z][A-Z0-9-]*',c['conference']): fail(cp+'.conference','应使用大写会议缩写')
        if type(c['year']) is not int or not 1900<=c['year']<=2100: fail(cp+'.year','应为 1900–2100 的整数')
        if not isinstance(c['name'],str) or not c['name']: fail(cp+'.name','应为非空字符串')
        if not isinstance(c['scope'],str): fail(cp+'.scope','应为字符串')
        if not isinstance(c['source_url'],str) or not url(c['source_url']): fail(cp+'.source_url','应为 HTTP(S) 链接')
        if not isinstance(c['papers'],list): fail(cp+'.papers','应为数组');continue
        if isinstance(c['conference'],str) and type(c['year']) is int:
            key=(c['conference'],c['year'])
            if key in keys: fail(cp,'会议和年份组合重复')
            keys.add(key)
        ids=set()
        for pi,p in enumerate(c['papers']):
            pp=f'{cp}.papers[{pi}]'
            if not isinstance(p,dict) or set(p)!=PAPER_FIELDS: fail(pp,'论文字段不完整或存在额外字段');continue
            for k in STRING_FIELDS:
                if not isinstance(p[k],str): fail(pp+'.'+k,'应为字符串，缺失时用空字符串')
            if isinstance(p['id'],str):
                if not p['id']: fail(pp+'.id','不能为空')
                elif p['id'] in ids: fail(pp+'.id','同一会议和年份内不能重复')
                ids.add(p['id'])
            if not isinstance(p['topics'],list) or not all(isinstance(x,str) and x for x in p['topics']): fail(pp+'.topics','应为非空字符串组成的数组；无主题用空数组')
            elif len(set(p['topics']))!=len(p['topics']): fail(pp+'.topics','主题不能重复')
            if not isinstance(p['links'],list): fail(pp+'.links','应为数组');continue
            for li,link in enumerate(p['links']):
                lp=f'{pp}.links[{li}]'
                if not isinstance(link,dict) or set(link)!={'label','url'}: fail(lp,'必须且只能包含 label 和 url');continue
                if not isinstance(link['label'],str) or not link['label']: fail(lp+'.label','应为非空字符串')
                if not isinstance(link['url'],str) or not url(link['url']): fail(lp+'.url','应为 HTTP(S) 链接')
    return errors

def main():
    parser=argparse.ArgumentParser(description='校验各会议年份的数据文件，或更新离线网页。')
    parser.add_argument('--sync',action='store_true',help='规范首尾空白并更新网页与离线数据资源')
    args=parser.parse_args()
    try:
        data_dir=ROOT/'data'; page_path=ROOT/'index.html'; asset_dir=ROOT/'assets'
        files=sorted(data_dir.glob('*.json'),key=lambda p:({'WWW':0,'ICDE':1,'CVPR':2}.get(p.stem.rsplit('-',1)[0],3),p.name))
        if not files: raise ValueError('data 目录中没有会议数据文件。')
        collections=[]; originals=[]
        for path in files:
            if not re.fullmatch(r'[A-Z][A-Z0-9-]*-[0-9]{4}\.json',path.name): raise ValueError(f'文件名不符合 会议缩写-年份.json：{path.name}')
            original=json.loads(path.read_text(encoding='utf-8-sig')); normalized=clean(original);errors=validate(normalized)
            if errors: raise ValueError(path.name+'：'+'；'.join(errors[:10]))
            if len(normalized['collections'])!=1: raise ValueError(path.name+' 必须且只能包含一个会议年份。')
            c=normalized['collections'][0]
            if path.name!=f"{c['conference']}-{c['year']}.json": raise ValueError(path.name+' 与其中的会议和年份不一致。')
            collections.append(c);originals.append((path,original,normalized))
        errors=validate({'schema_version':1,'collections':collections})
        if errors: raise ValueError('；'.join(errors[:10]))
        page=page_path.read_text(encoding='utf8');matches=list(re.finditer(r'(<script id="data" type="application/json">)(.*?)(</script>)',page,re.S))
        if len(matches)!=1: raise ValueError('网页中必须有唯一的数据区块。')
        match=matches[0];embedded=json.loads(match.group(2))
        manifest={'schema_version':1,'collections':[{k:v for k,v in c.items() if k!='papers'} for c in collections]}
        outputs={f"{c['conference']}-{c['year']}.js":'globalThis.paperCollections = globalThis.paperCollections || {};\nglobalThis.paperCollections['+json.dumps(f"{c['conference']}-{c['year']}")+'] = '+json.dumps(c,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n' for c in collections}
        if args.sync:
            asset_dir.mkdir(exist_ok=True)
            for name,content in outputs.items(): (asset_dir/name).write_text(content,encoding='utf8')
            payload=json.dumps(manifest,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
            page_path.write_text(page[:match.start(2)]+payload+page[match.end(2):],encoding='utf8')
            for path,_,normalized in originals:path.write_text(json.dumps(normalized,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            print('校验通过，已更新网页及各会议的离线数据资源。')
        else:
            for path,original,normalized in originals:
                if original!=normalized: raise ValueError(path.name+' 存在首尾空白，请运行 --sync。')
            if embedded!=manifest: raise ValueError('网页会议目录与数据文件不一致，请运行 --sync。')
            for name,content in outputs.items():
                if not (asset_dir/name).is_file() or (asset_dir/name).read_text(encoding='utf8')!=content: raise ValueError('离线数据资源与数据文件不一致，请运行 --sync：'+name)
            print('校验通过，网页目录与各会议数据文件一致。')
        for c in collections:print(f"{c['conference']} {c['year']}: {len(c['papers'])} 篇")
        return 0
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        print(f'处理失败：{exc}',file=sys.stderr);return 1
if __name__=='__main__': sys.exit(main())
