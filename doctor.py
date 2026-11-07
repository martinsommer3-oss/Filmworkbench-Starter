"""Read-only local setup report. Never downloads, installs, generates or reads API keys."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import urllib.parse
import urllib.error
import render_example as runner

ROOT = Path(__file__).resolve().parent
MODEL_FIELDS = {'unet_name','clip_name','vae_name','lora_name','model_name'}
SOURCES = {
    'core':'https://github.com/Comfy-Org/ComfyUI',
    'motion':'https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context',
    'keystone':'https://github.com/roycho87/geiru_context_suite',
    'stage':'https://github.com/chanon/comfyui-obvpm-timeline',
    'upscale':'https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler',
}

def node_source(kind):
    if kind.startswith('MiniMaxH3MotionContext') or kind=='MiniMaxH3SigmasTail': key='motion'
    elif kind=='H3ClownKeyframe': key='keystone'
    elif kind=='H3StageLatent': key='stage'
    elif kind=='MinimaxH3LatentUpscaler3D': key='upscale'
    else: key='core'
    return SOURCES[key]

def local_server(value):
    p=urllib.parse.urlparse(value)
    if p.scheme!='http' or p.hostname not in {'localhost','127.0.0.1','::1'} or p.username or p.password or p.query or p.fragment or p.path not in ('','/'):
        raise ValueError('Use a local HTTP ComfyUI address with no credentials, path or query.')
    return value.rstrip('/')

def compare(graphs, info):
    sources={m['name']:m for m in runner.load(ROOT/'docs/model_sources.json')['models']}
    issues=[]; checked=set()
    for graph in graphs.values():
        for node in graph.values():
            kind=node['class_type']; inputs=node['inputs']
            if kind not in info:
                key=('node',kind)
                if key not in checked:
                    issues.append({'type':'missing_node','node':kind,'source':node_source(kind),
                                   'action':'Install or repair this node project in your ComfyUI environment, restart it, then check again. See its own dependencies.'})
                    checked.add(key)
                continue
            schema=info[kind].get('input',{})
            fields={**schema.get('required',{}),**schema.get('optional',{})}
            for field,spec in schema.get('required',{}).items():
                # Hidden inputs and nested dynamic-combo fields are supplied by the backend.
                if field not in inputs and '.' not in field:
                    key=('required',kind,field)
                    if key not in checked:
                        issues.append({'type':'missing_required_setting','node':kind,'field':field,
                                       'action':'Inspect the installed node schema; the historical graph may need an explicit migration.'})
                        checked.add(key)
            for field,value in inputs.items():
                spec=fields.get(field)
                if not spec or not isinstance(spec,list) or not spec: continue
                choices=spec[0]
                if not isinstance(choices,list) or isinstance(value,list): continue
                if field in {'image','audio','latent_path'}: continue  # Assets are staged only on explicit render.
                if value in choices: continue
                key=(kind,field,str(value))
                if key in checked: continue
                checked.add(key)
                if field in MODEL_FIELDS:
                    candidates=[v for v in choices if isinstance(v,str) and v.replace('\\','/').split('/')[-1]==str(value).replace('\\','/').split('/')[-1]]
                    issues.append({'type':'model_path_mismatch' if candidates else 'missing_model',
                        'node':kind,'field':field,'required':value,'matching_filenames':candidates,
                        'action':'Select the matching relative model path explicitly; matching filenames do not prove matching weights.' if candidates else
                        'See docs/MODELS.md. Run setup_models.py --comfy-root YOUR_COMFY_PATH to plan, then add --download explicitly. No automatic model substitution.',
                        'source':sources.get(str(value).replace('\\','/').split('/')[-1],{}).get('source'),
                        'target_folder':sources.get(str(value).replace('\\','/').split('/')[-1],{}).get('folder')})
                else:
                    issues.append({'type':'unsupported_setting','node':kind,'field':field,'value':value,
                                   'allowed':choices,'action':'Check the installed node version; do not silently replace this setting.'})
    return issues

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--online',action='store_true',help='Read /object_info from a local ComfyUI server')
    p.add_argument('--all',action='store_true',help='Check every case using the public stage-join adapter, not only the starter')
    p.add_argument('--server',default='http://127.0.0.1:8188')
    p.add_argument('--model-map',type=Path,help='Explicit loader-relative model paths')
    p.add_argument('--report',type=Path,help='Write this report locally; it contains no machine paths or environment variables')
    args=p.parse_args()
    base=local_server(args.server)
    example,graphs=runner.prepare('preflight')
    if args.all:
        from film import adapt_stage_joins
        graphs={f.name:adapt_stage_joins(runner.load(f)) for f in (ROOT/'graphs').glob('*.api.json')}
    runner.apply_model_map(graphs,runner.read_model_map(args.model_map))
    assets=runner.load(ROOT/'assets/manifest.json')
    broken=[relative for relative,item in assets.items() if not runner.confined(ROOT,relative).is_file() or runner.digest(runner.confined(ROOT,relative))!=item['sha256']]
    requirements=sorted({str(v) for g in graphs.values() for n in g.values() for k,v in n['inputs'].items() if k in MODEL_FIELDS})
    report={'scope':'all case graphs with public stage-join adaptation' if args.all else 'standalone dialogue starter',
            'python_supported':sys.version_info >= (3,11),'ffmpeg_on_path':bool(shutil.which('ffmpeg')),
            'reference_files_checked':len(assets),'bad_references':broken,'graphs_checked':len(graphs),
            'required_models':requirements,'backend':'not checked (use --online)', 'issues':[],
            'image_generation':{'recommended':'GPT Image through a supported agent/service; capability is not inferred from API keys.',
                'fallback':'Krea 2 locally, with its own model/node setup; no automatic substitution.',
                'starter_requires_generator':False,'reason':'All example input images are included. A fresh image generator is only needed for new scenes.',
                'new_projects':'Keep a coherent image family. A fallback may require rebuilding and reviewing the reference set.'},
            'limits':['Model filenames are not cryptographic weight verification.',
                      'GPU memory suitability and CUDA execution require a real render test.',
                      'Exact model sources are documented; fresh-machine GPU installation remains untested.']}
    if args.online:
        try:
            report['issues']=compare(graphs,runner.api(base,'/object_info'))
            report['backend']='checked'
        except (urllib.error.URLError,TimeoutError,OSError,ValueError):
            report['backend']='unreachable or invalid response; start your existing ComfyUI server and check the address'
    report['ready_for_render_check']=bool(args.online and report['backend']=='checked' and not report['issues'] and not broken and report['python_supported'] and report['ffmpeg_on_path'])
    text=json.dumps(report,ensure_ascii=False,indent=2)
    if args.report:
        with args.report.open('x',encoding='utf-8') as stream: stream.write(text+'\n')
    print(text)
    return 0 if (not args.online and not broken) or report['ready_for_render_check'] else 2

if __name__=='__main__': raise SystemExit(main())
