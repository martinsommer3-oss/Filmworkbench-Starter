"""Plan, download explicitly, or verify the exact recipe weights. No GPU use."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import render_example as r


def entries(all_models=False):
    return [m for m in r.load(r.ROOT/'docs/model_sources.json')['models'] if all_models or m['starter']]


def valid_file(path, model):
    return path.is_file() and path.stat().st_size == model['bytes'] and r.digest(path) == model['sha256']


def download_command(model, staging, hf='hf'):
    return [hf,'download',model['repo_id'],model['remote_path'],'--revision',model['revision'],'--local-dir',str(staging)]


def target_for(root, model, mapping, model_roots=None):
    # Mapping values are loader-relative paths inside this model category.
    category_root=(model_roots or {}).get(model['folder'],root/'models'/model['folder'])
    return r.confined(category_root,mapping.get(model['name'],model['name']))


def install(model, target, staging, hf):
    if target.exists():
        if not valid_file(target,model):
            raise ValueError(f'Existing file differs; preserved without overwrite: {target}')
        return 'already verified'
    staging.mkdir(parents=True,exist_ok=True)
    subprocess.run(download_command(model,staging,hf),check=True)
    source=r.confined(staging,model['remote_path'])
    if not valid_file(source,model):
        raise ValueError(f'Download size or SHA-256 mismatch: {model["id"]}; not installed')
    target.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation also prevents races from overwriting an existing weight.
    # Interrupted copies are retained and rejected by the next verification.
    with source.open('rb') as src, target.open('xb') as dst:
        shutil.copyfileobj(src,dst,8*1024*1024)
    if not valid_file(target,model):
        raise ValueError(f'Installed copy verification failed: {target}; file retained for inspection')
    return 'downloaded and verified'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group()
    group.add_argument('--download',action='store_true',help='Explicitly download and install (52.6 GB for starter)')
    group.add_argument('--verify',action='store_true',help='Read full installed weights and check SHA-256; no network')
    p.add_argument('--all',action='store_true',help='Also include Turbo-8 for continuation cases')
    p.add_argument('--comfy-root',type=Path,required=True)
    p.add_argument('--model-map',type=Path,help='JSON mapping canonical filenames to loader-relative paths')
    p.add_argument('--model-root',action='append',default=[],metavar='CATEGORY=PATH',help='Explicit external model category directory; repeat as needed')
    p.add_argument('--cache',type=Path,help='Staging download directory; retained for resumable HF downloads')
    args=p.parse_args()
    if not (args.comfy_root/'models').is_dir(): p.error('--comfy-root must contain an existing models directory')
    mapping=r.read_model_map(args.model_map)
    selected=entries(args.all)
    model_roots={}
    categories={m['folder'] for m in entries(True)}
    for item in args.model_root:
        category,sep,path=item.partition('=')
        if not sep or category not in categories or not Path(path).is_dir():
            p.error('--model-root requires a known category and an existing directory')
        model_roots[category]=Path(path)
    cache=args.cache or args.comfy_root/'.filmworkbench-downloads'
    hf=shutil.which('hf')
    if args.download and not hf: p.error('Install Hugging Face CLI first: python -m pip install -U huggingface_hub')
    failed=False
    for model in selected:
        target=target_for(args.comfy_root,model,mapping,model_roots)
        stage=r.confined(cache,model['id'])
        item={'id':model['id'],'file':model['name'],'bytes':model['bytes'],'target':str(target),'source':model['source']}
        try:
            if args.verify:
                item['status']='verified' if valid_file(target,model) else 'missing or hash/size mismatch'
                failed |= item['status']!='verified'
            elif args.download: item['status']=install(model,target,stage,hf)
            else:
                item['status']='plan only; nothing downloaded'
                item['command_argv']=download_command(model,stage)
            print(json.dumps(item,ensure_ascii=False),flush=True)
        except (OSError,ValueError,subprocess.CalledProcessError) as exc:
            # Do not echo subprocess environments, credentials or authentication output.
            print(json.dumps({'id':model['id'],'status':'failed','reason':str(exc)},ensure_ascii=False),flush=True)
            failed=True
            break
    return 2 if failed else 0

if __name__=='__main__': raise SystemExit(main())
