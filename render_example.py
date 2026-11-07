"""Filmworkbench v0.1 dialogue starter. Standard library only; no implicit render."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def confined(root, relative):
    root = root.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'Path leaves its root: {relative}')
    return path

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def prepare(run_id):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', run_id):
        raise ValueError('Invalid run identifier')
    example = load(ROOT / 'examples/dialogue/example.json')
    for relative, expected in example['assets'].items():
        if digest(confined(ROOT, relative)) != expected:
            raise ValueError(f'Reference hash mismatch: {relative}')
    graphs = {}
    for stage, relative in example['graphs'].items():
        raw = confined(ROOT, relative).read_text(encoding='utf-8')
        graph = json.loads(raw.replace('__RUN_PREFIX__', f'filmworkbench_v01/{run_id}'))
        for node in graph.values():
            if node['class_type'] == 'LoadImage':
                asset = node['inputs']['image']
                if asset not in example['assets']:
                    raise ValueError(f'Unbound image: {asset}')
                node['inputs']['image'] = f'filmworkbench_v01/{run_id}/{asset}'
            for value in node['inputs'].values():
                if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                    if value[0] not in graph:
                        raise ValueError(f'Missing upstream node: {value[0]}')
        graphs[stage] = graph
    return example, graphs

def read_model_map(path):
    if path is None: return {}
    mapping=load(path)
    known={m['name'] for m in load(ROOT/'docs/model_sources.json')['models']}
    if not isinstance(mapping,dict): raise ValueError('Model map must be a JSON object')
    for name,value in mapping.items():
        if name not in known or not isinstance(value,str) or not value:
            raise ValueError('Model map must map known filenames to nonempty relative paths')
        if value.startswith(('/',"\\")) or ':' in value or '..' in value.replace("\\",'/').split('/'):
            raise ValueError('Model paths must stay inside their model category')
    return mapping


def apply_model_map(graphs,mapping):
    from doctor import MODEL_FIELDS
    for graph in graphs.values():
        for node in graph.values():
            for key,value in node['inputs'].items():
                if key in MODEL_FIELDS and isinstance(value,str) and value in mapping:
                    node['inputs'][key]=mapping[value]


def api(base, path, data=None):
    payload = None if data is None else json.dumps(data).encode()
    request = urllib.request.Request(base + path, data=payload, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def check_backend(graphs, info):
    from doctor import compare
    return [json.dumps(issue, ensure_ascii=False) for issue in compare(graphs, info)]

def video_output(history, comfy_root):
    found = []
    def walk(value):
        if isinstance(value, dict):
            if str(value.get('filename','')).lower().endswith('.mp4') and value.get('type','output') == 'output':
                relative = str(Path(value.get('subfolder','')) / value['filename'])
                p = confined(comfy_root / 'output', relative)
                if p.is_file(): found.append(p)
            for item in value.values(): walk(item)
        elif isinstance(value,list):
            for item in value: walk(item)
    walk(history.get('outputs', {}))
    unique = list(dict.fromkeys(found))
    if len(unique) != 1:
        raise RuntimeError(f'Expected one saved video, found {len(unique)}; inspect saved history')
    return unique[0]

def execute(base, graph, work, stage, timeout):
    queue = api(base, '/queue')
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise RuntimeError('ComfyUI is busy; no render submitted. Do not run another producer concurrently.')
    (work / f'{stage}.submitted.json').write_text(json.dumps(graph, indent=2), encoding='utf-8')
    result = api(base, '/prompt', {'prompt':graph,'client_id':str(uuid.uuid4())})
    if result.get('node_errors') or not result.get('prompt_id'):
        raise RuntimeError(f'Graph rejected: {result}')
    prompt_id = result['prompt_id']
    (work / f'{stage}.submission.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f'{stage} queued: {prompt_id}', flush=True)
    started = time.monotonic()
    while time.monotonic() - started < timeout:
        history = api(base, '/history/' + urllib.parse.quote(prompt_id))
        if prompt_id in history:
            item = history[prompt_id]
            (work / f'{stage}.history.json').write_text(json.dumps(item, indent=2), encoding='utf-8')
            if item.get('status',{}).get('status_str') == 'error':
                raise RuntimeError(f'{stage} failed; inspect saved history')
            if not item.get('status',{}).get('completed',False):
                raise RuntimeError(f'{stage} history is not a confirmed successful completion')
            return item
        time.sleep(3)
    raise TimeoutError(f'{stage} wait expired. The server job may still be running; it was NOT cancelled. Do not resubmit blindly.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read installed node/model availability, without rendering')
    parser.add_argument('--run', action='store_true', help='Explicitly run S1, then S2 and copy S1 audio under S2')
    parser.add_argument('--server', default='http://127.0.0.1:8188')
    parser.add_argument('--comfy-root', type=Path, help='Local ComfyUI directory containing input/ and output/')
    parser.add_argument('--model-map', type=Path, help='Explicit canonical filename to backend-relative model path JSON')
    parser.add_argument('--timeout', type=float, default=3600)
    args = parser.parse_args()
    from doctor import local_server
    base = local_server(args.server)
    run_id = uuid.uuid4().hex[:12]
    example, graphs = prepare(run_id)
    apply_model_map(graphs, read_model_map(args.model_map))
    print('Local references and graph links verified. Example: first K1 dialogue clip, S1 + S2.')
    if not args.check and not args.run:
        print('No backend contacted. Use --check for node/model availability; --run explicitly starts generation.')
        return
    base = args.server.rstrip('/')
    issues = check_backend(graphs, api(base, '/object_info'))
    if issues:
        raise RuntimeError('\n'.join(issues))
    print('Backend node and model-name check passed. This is not a fresh-install render test.')
    if not args.run: return
    if not args.comfy_root or not (args.comfy_root / 'input').is_dir() or not (args.comfy_root / 'output').is_dir():
        parser.error('--run requires the existing local --comfy-root with input/ and output/')
    if not shutil.which('ffmpeg'): parser.error('ffmpeg must be on PATH for final audio assembly')
    queue = api(base, '/queue')
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise RuntimeError('ComfyUI is busy; nothing copied or submitted')
    work = ROOT / 'runs' / run_id
    work.mkdir(parents=True, exist_ok=False)
    for relative in example['assets']:
        target = confined(args.comfy_root / 'input', f'filmworkbench_v01/{run_id}/{relative}')
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream: stream.write(confined(ROOT,relative).read_bytes())
    outputs = {}
    for stage in ['S1','S2']:
        started = time.monotonic()
        history = execute(base, graphs[stage], work, stage, args.timeout)
        (work / f'{stage}.timing.json').write_text(json.dumps({'wall_seconds':time.monotonic()-started}),encoding='utf-8')
        outputs[stage] = video_output(history, args.comfy_root)
    final = work / 'dialogue_S2_S1audio.mp4'
    command = ['ffmpeg','-hide_banner','-nostdin','-n','-i',str(outputs['S2']),'-i',str(outputs['S1']),
               '-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(final)]
    subprocess.run(command, check=True)
    provenance={'inputs':{key:{'path':str(value),'sha256':digest(value)} for key,value in outputs.items()},
                'output_sha256':digest(final),'ffmpeg':command,'audio_policy':'S1 audio copied under S2 video',
                'release':'0.1.0 candidate','notice':'Add a visible MiniMax H3 credit before sharing this new render.'}
    (work/'provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    print(f'Generated candidate: {final}\nReview it before accepting it; no automatic quality approval was made.')

if __name__ == '__main__':
    main()
