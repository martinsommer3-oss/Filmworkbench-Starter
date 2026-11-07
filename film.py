"""Portable, approval-gated scene recipes. Python standard library; ComfyUI + FFmpeg."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import subprocess
import time
import uuid
import hashlib
import re
from fractions import Fraction
from contextlib import contextmanager
import render_example as runner

ROOT = Path(__file__).resolve().parent
CASES = ('K1','K2','K3','K4','K6','K7','K8','K9','MARKET')
load = runner.load
digest = runner.digest
confined = runner.confined

def write(path, value):
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    tmp.replace(path)

@contextmanager
def lock(project):
    path = project/'.film.lock'
    with path.open('x') as f:
        f.write('One controller at a time. Remove only after confirming its process has stopped.')
    try: yield
    finally: path.unlink()

def spec(case):
    if case not in CASES: raise ValueError('Unknown recipe')
    if case == 'MARKET':
        return {'parts':[{'id':f'MARKET_G{i}'} for i in range(1,5)]}
    return load(ROOT/f'recipes/{case}_assembly.json')

def ordered(case):
    inventory = load(ROOT/'graphs/inventory.json')
    result, visiting = [], set()
    def visit(name):
        if name in result: return
        if name in visiting: raise ValueError('Dependency cycle')
        visiting.add(name)
        for d in inventory[name]['dependencies']:
            if len(d['producers']) != 1: raise ValueError('Unresolved producer')
            visit(d['producers'][0]['graph'])
        visiting.remove(name)
        result.append(name)
    for p in spec(case)['parts']:
        visit(p.get('audio_id',p['id'])+'_S1')
        visit(p['id']+'_S2')
    return result

def init(project, cases):
    project.mkdir(parents=True, exist_ok=False)
    plan={'version':'0.1.1','id':uuid.uuid4().hex[:12], 'review_mode':'guided',
          'limits':{'max_takes_per_stage':3,'max_render_stages':sum(len(ordered(c)) for c in cases)*2},'scenes':[]}
    for index,case in enumerate(cases):
        sid=f'{index+1:02d}_{case}'
        scene={'id':sid,'recipe':case,'assets':{},'prompts':{},'seeds':{},
               'intent':'Describe the scene goal and required starting state here.',
               'assembly':spec(case)}
        for name in ordered(case):
            g=load(ROOT/f'graphs/{name}.api.json')
            for b in load(ROOT/f'graphs/{name}.bindings.json').values():
                asset=b['asset']
                if asset not in scene['assets']:
                    src=confined(ROOT,asset)
                    if digest(src)!=b['sha256']: raise ValueError('Bundled asset hash mismatch')
                    rel=f'{sid}/{asset}'
                    target=confined(project,rel); target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(src,target);scene['assets'][asset]=rel
            for node,n in g.items():
                if n['class_type']=='MiniMaxH3ReferenceToVideo':
                    rel=f'{sid}/prompts/{name}.txt'
                    target=confined(project,rel);target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_text(n['inputs']['prompt'],encoding='utf-8')
                    scene['prompts'][name]=rel
                if n['class_type']=='RandomNoise':scene['seeds'][name]=n['inputs']['noise_seed']
        prelap=scene['assembly'].get('prelap')
        if prelap and prelap['asset'] not in scene['assets']:
            asset=prelap['asset'];rel=f'{sid}/{asset}'
            confined(project,rel).parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(confined(ROOT,asset),confined(project,rel));scene['assets'][asset]=rel
        plan['scenes'].append(scene)
    write(project/'film.json',plan)
    write(project/'state.json',{'jobs':{},'reviews':[]})
    return plan

def jobs(plan):
    ids=[s['id'] for s in plan['scenes']]
    if not ids or len(set(ids))!=len(ids):raise ValueError('A film needs unique scene identifiers')
    return [(scene,name,f"{scene['id']}/{name}") for scene in plan['scenes'] for name in ordered(scene['recipe'])]

def adapt_stage_joins(graph):
    """Use public AV joining for the supported mask-free archived stage inputs."""
    for node in graph.values():
        if node['class_type']!='H3StageLatent':continue
        inputs=node['inputs'];source=inputs['first_stage']
        if graph[source[0]]['class_type']!='MiniMaxH3MotionContextLoadLatent':
            raise ValueError('Stage join is not a mask-free file loader')
        separate=next(k for k,v in graph.items() if v['class_type']=='LTXVSeparateAVLatent' and v['inputs']['av_latent']==source)
        node['class_type']='LTXVConcatAVLatent'
        node['inputs']={'video_latent':inputs['video_latent'],'audio_latent':[separate,1]}
    return graph

def compile_graph(project, plan, scene, name, state, attempt, model_map=None):
    for value in (plan['id'],scene['id'],name,attempt):
        if not re.fullmatch(r'[A-Za-z0-9_-]+',value):raise ValueError('Invalid project, scene or take identifier')
    g=load(ROOT/f'graphs/{name}.api.json')
    bindings=load(ROOT/f'graphs/{name}.bindings.json')
    prefix=f"filmworkbench_v011/{plan['id']}/{scene['id']}/{name}/{attempt}"
    staged={}
    for node,b in bindings.items():
        src=confined(project,scene['assets'][b['asset']])
        # The content hash prevents accidental reuse after a user changes a reference.
        target=f"filmworkbench_v011/{plan['id']}/inputs/{digest(src)}{src.suffix.lower()}"
        field='image' if g[node]['class_type']=='LoadImage' else 'audio'
        g[node]['inputs'][field]=target;staged[target]=src
    deps=load(ROOT/'graphs/inventory.json')[name]['dependencies']
    for d in deps:
        if len(d['producers'])!=1: raise ValueError('Ambiguous latent producer')
        p=d['producers'][0];key=f"{scene['id']}/{p['graph']}"
        parent=state['jobs'].get(key,{})
        if parent.get('status')!='accepted': raise ValueError(f'Approve predecessor first: {key}')
        relative=parent['latents'][p['node']]
        g[d['node']]['inputs'].update(latent_path=relative,folder='output')
    adapt_stage_joins(g)
    for node,n in g.items():
        kind=n['class_type'];inputs=n['inputs']
        if kind in ('SaveVideo','MiniMaxH3MotionContextSaveLatent'):
            inputs['filename_prefix']=f'{prefix}/{node}/clip'
        elif kind=='MiniMaxH3ReferenceToVideo':
            inputs['prompt']=confined(project,scene['prompts'][name]).read_text(encoding='utf-8')
        elif kind=='RandomNoise': inputs['noise_seed']=int(scene['seeds'][name])
    runner.apply_model_map({name:g},model_map or {})
    for node,n in g.items():
        for v in n['inputs'].values():
            if isinstance(v,list) and len(v)==2 and isinstance(v[0],str) and v[0] not in g:
                raise ValueError(f'Broken link {name}:{node}')
    return g,staged

def fingerprint(project,scene,name):
    binding=load(ROOT/f'graphs/{name}.bindings.json')
    content={'graph':digest(ROOT/f'graphs/{name}.api.json'),
             'prompt':digest(confined(project,scene['prompts'][name])),
             'seed':scene['seeds'][name],
             'assets':{b['asset']:digest(confined(project,scene['assets'][b['asset']])) for b in binding.values()}}
    return hashlib.sha256(json.dumps(content,sort_keys=True).encode()).hexdigest()

def unchanged(project,plan,state):
    for scene,name,key in jobs(plan):
        old=state['jobs'].get(key)
        if old and old['fingerprint']!=fingerprint(project,scene,name):
            raise ValueError(f'Inputs changed after render: {key}. Use retry --job {key} to invalidate descendants.')

def node_file(history,node,root,extension):
    values=[]
    def walk(v):
        if isinstance(v,dict):
            if str(v.get('filename','')).endswith(extension):
                rel=(Path(v.get('subfolder',''))/v['filename']).as_posix()
                if confined(root/'output',rel).is_file():values.append(rel)
            for x in v.values():walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    walk(history.get('outputs',{}).get(node,{}))
    if len(set(values))!=1:raise RuntimeError(f'Missing or ambiguous output {node} {extension}')
    return values[0]

def collect(history,g,root):
    latents={k:node_file(history,k,root,'.safetensors') for k,n in g.items() if n['class_type']=='MiniMaxH3MotionContextSaveLatent'}
    primary='s1_save' if 's1_save' in g else '31'
    return node_file(history,primary,root,'.mp4'),latents

def review_preview(project,scene,name,state,record):
    video=Path(record['comfy_root'])/'output'/record['video']
    if name.endswith('_S2'):
        deps=load(ROOT/'graphs/inventory.json')[name]['dependencies']
        source=next(d['producers'][0]['graph'] for d in deps if d['node']=='ld_s1')
        audio=state['jobs'][f"{scene['id']}/{source}"]
        target=confined(project,record['work'])/'review_S2_S1audio.mp4'
        if not target.exists():
            ffmpeg(['-i',video,'-i',Path(audio['comfy_root'])/'output'/audio['video'],
                    '-map','0:v:0','-map','1:a:0','-c','copy',target])
        video=target
    record['review_video']=str(video)
    return video

def next_job(project,plan,state,args):
    unchanged(project,plan,state)
    for scene,name,key in jobs(plan):
        old=state['jobs'].get(key)
        if old and old['status']=='accepted':continue
        if old:raise ValueError(f'{key} is {old["status"]}. Inspect, accept, retry or recover it first.')
        counts=state.setdefault('attempts',{})
        limits=plan.get('limits',{'max_takes_per_stage':3,'max_render_stages':len(jobs(plan))*2})
        if counts.get(key,0)>=limits['max_takes_per_stage'] or sum(counts.values())>=limits['max_render_stages']:
            raise ValueError('Render budget exhausted. Report unfinished work; do not silently raise the budget.')
        root=args.comfy_root.resolve()
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise ValueError('FFmpeg and ffprobe must be on PATH')
        if not (root/'input').is_dir() or not (root/'output').is_dir():raise ValueError('Invalid ComfyUI root')
        attempt=uuid.uuid4().hex[:8]
        g,staged=compile_graph(project,plan,scene,name,state,attempt,runner.read_model_map(args.model_map))
        for node in g.values():
            if node['class_type'] in ('SaveVideo','MiniMaxH3MotionContextSaveLatent'):
                confined(root/'output',node['inputs']['filename_prefix'])
        issues=runner.check_backend({name:g},runner.api(args.server,'/object_info'))
        if issues:raise ValueError('\n'.join(issues))
        queue=runner.api(args.server,'/queue')
        if queue.get('queue_running') or queue.get('queue_pending'):raise ValueError('Backend busy; nothing submitted')
        for rel,src in staged.items():
            target=confined(root/'input',rel);target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():shutil.copyfile(src,target)
            if digest(src)!=digest(target):raise ValueError('Input staging hash mismatch')
        work=project/'runs'/scene['id']/name/attempt;work.mkdir(parents=True)
        record={'status':'submitted','fingerprint':fingerprint(project,scene,name),'work':str(work.relative_to(project)),
                'comfy_root':str(root),'server':args.server,'started':time.time()}
        state['jobs'][key]=record;write(project/'state.json',state)
        counts[key]=counts.get(key,0)+1;write(project/'state.json',state)
        try:
            history=runner.execute(args.server,g,work,'render',args.timeout)
            record['video'],record['latents']=collect(history,g,root)
            review_preview(project,scene,name,state,record)
            record.update(status='review',seconds=time.time()-record['started'])
        except Exception:
            # Persist submitted state: even a client timeout must not cause duplicate work.
            write(project/'state.json',state);raise
        write(project/'state.json',state)
        print(json.dumps({'job':key,'status':'review','video':record['review_video']}))
        return
    print('All stages accepted. Run assemble.')

def check(project,plan,args):
    state={'jobs':{}};graphs={}
    for scene,name,key in jobs(plan):
        g,_=compile_graph(project,plan,scene,name,state,'preflight',runner.read_model_map(args.model_map))
        graphs[key]=g
        lat={k:f"filmworkbench_v011/{plan['id']}/{scene['id']}/{name}/preflight/{k}/clip_{n['inputs']['clip_index']:05d}.safetensors"
             for k,n in g.items() if n['class_type']=='MiniMaxH3MotionContextSaveLatent'}
        state['jobs'][key]={'status':'accepted','latents':lat}
    issues=runner.check_backend(graphs,runner.api(args.server,'/object_info')) if args.online else []
    print(json.dumps({'graphs':len(graphs),'issues':issues,'gpu_render_test':False},indent=2))
    if issues:raise ValueError('Backend preflight failed')
    return graphs

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))

def review_material(project,plan,state,key):
    item=state['jobs'][key]
    if item.get('status') not in ('review','accepted'):raise ValueError('Render must complete first')
    scene,name,_=next(x for x in jobs(plan) if x[2]==key)
    video=review_preview(project,scene,name,state,item)
    folder=confined(project,item['work'])/'review'
    if folder.exists():raise ValueError(f'Review material already exists: {folder}')
    folder.mkdir()
    ffmpeg(['-i',video,'-vf','fps=1,scale=768:-2',folder/'frame_%03d.jpg'])
    ffmpeg(['-i',video,'-frames:v','1','-vf','scale=768:-2',folder/'start.jpg'])
    stream=next(s for s in probe(video)['streams'] if s['codec_type']=='video')
    last=int(stream['nb_frames'])-1
    ffmpeg(['-i',video,'-vf',f'select=eq(n\\,{last}),scale=768:-2','-frames:v','1',folder/'end.jpg'])
    ffmpeg(['-i',video,'-vn','-c:a','pcm_s16le',folder/'audio.wav'])
    dimensions=('action','identity','continuity','motion','audio','story')
    report={'job':key,'fingerprint':item['fingerprint'],'video_sha256':digest(video),
            'decision':'pending','reviewer':'','checks':{x:{'status':'unknown','evidence':''} for x in dimensions},
            'observed_end_state':'','limitations':[], 'material':{'video':str(video),'frames':'frame_*.jpg','first_frame':'start.jpg','last_frame':'end.jpg','audio':'audio.wav'},
            'note':'Frames are samples. Do not claim full motion or speech review from stills. Unknown checks must remain disclosed.'}
    write(folder/'assessment.json',report)
    write(project/'state.json',state)
    print(folder/'assessment.json')
    return folder/'assessment.json'

def agent_accept(project,plan,state,key,path):
    if plan.get('review_mode')!='autonomous':raise ValueError('Agent acceptance requires an explicitly commissioned autonomous project')
    item=state['jobs'].get(key,{})
    if item.get('status')!='review':raise ValueError('Only completed stages can be reviewed')
    report=load(path)
    if report.get('job')!=key or report.get('fingerprint')!=item['fingerprint']:raise ValueError('Review belongs to a different take')
    scene,name,_=next(x for x in jobs(plan) if x[2]==key)
    video=review_preview(project,scene,name,state,item)
    if report.get('video_sha256')!=digest(video):raise ValueError('Reviewed video changed')
    if report.get('decision')!='accept' or not report.get('reviewer') or not report.get('observed_end_state'):
        raise ValueError('Decision, reviewer and observed end state are required')
    for dimension in ('action','identity','continuity','motion','audio','story'):
        check=report.get('checks',{}).get(dimension,{})
        status=check.get('status')
        if status not in ('pass','warning','not_applicable','unknown') or not check.get('evidence'):
            raise ValueError(f'Missing evidence or failed check: {dimension}')
        if dimension in ('action','identity','continuity','story') and status=='unknown':
            raise ValueError(f'Cannot accept unreviewed core requirement: {dimension}')
        if status in ('unknown','warning') and not report.get('limitations'):
            raise ValueError('Disclose incomplete checks and known limitations')
    item.update(status='accepted',assessment=copy.deepcopy(report),note='Agent-reviewed autonomous take; see recorded limitations.')
    state['reviews'].append(copy.deepcopy(report));write(project/'state.json',state)

def ffmpeg(args):
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-n',*map(str,args)],check=True)

def concat_media(files,target,credit=False):
    inputs=[];filters=[];labels=[];shape=None
    for i,path in enumerate(files):
        stream=next(s for s in probe(path)['streams'] if s['codec_type']=='video')
        signature=(stream['width'],stream['height'],stream['avg_frame_rate'])
        if shape is not None and shape!=signature:raise ValueError('Scene sizes/frame rates differ')
        shape=signature
        duration=int(stream['nb_frames'])/float(Fraction(stream['avg_frame_rate']))
        inputs+=['-i',path]
        filters += [f'[{i}:v]setpts=PTS-STARTPTS[v{i}]',
                    f'[{i}:a]asetpts=PTS-STARTPTS,apad,atrim=duration={duration}[a{i}]']
        labels.append(f'[v{i}][a{i}]')
    filters.append(''.join(labels)+f'concat=n={len(files)}:v=1:a=1[v][a]')
    video='[v]'
    if credit:
        filters.append("[v]drawtext=text='MiniMax H3':fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5:x=(w-tw)/2:y=h-th-24[credited]")
        video='[credited]'
    ffmpeg([*inputs,'-filter_complex',';'.join(filters),'-map',video,'-map','[a]',
            '-c:v','libx264','-crf','18','-preset','fast','-c:a','aac','-movflags','+faststart',target])

def assemble(project,plan,state):
    unchanged(project,plan,state)
    if any(state['jobs'].get(key,{}).get('status')!='accepted' for _,_,key in jobs(plan)):
        raise ValueError('Accept all stages before assembly')
    out=project/'exports'/uuid.uuid4().hex[:8];out.mkdir(parents=True)
    scenes=[]
    for scene in plan['scenes']:
        parts=[]
        for index,part in enumerate(scene['assembly']['parts']):
            v=state['jobs'][f"{scene['id']}/{part['id']}_S2"]
            a=state['jobs'][f"{scene['id']}/{part.get('audio_id',part['id'])}_S1"]
            video=Path(v['comfy_root'])/'output'/v['video'];audio=Path(a['comfy_root'])/'output'/a['video']
            vs=next(s for s in probe(video)['streams'] if s['codec_type']=='video')
            ats=next(s for s in probe(audio)['streams'] if s['codec_type']=='video')
            if vs.get('nb_frames')!=ats.get('nb_frames'):raise ValueError('S1/S2 frame count mismatch')
            target=out/f"{scene['id']}_{index}.mp4"
            ffmpeg(['-i',video,'-i',audio,'-map','0:v:0','-map','1:a:0','-c','copy',target]);parts.append(target)
        joined=out/f"{scene['id']}_joined.mp4"
        concat_media(parts,joined)
        prelap=scene['assembly'].get('prelap')
        if prelap:
            start=float(prelap['start_s']);length=float(prelap['end_s'])-start
            if start<0 or length<=0:raise ValueError('Invalid prelap interval')
            asset=confined(project,scene['assets'][prelap['asset']]);mixed=out/f"{scene['id']}_prelap.mp4"
            filters=f"[1:a]atrim=duration={length},asetpts=PTS-STARTPTS,adelay={round(start*1000)}:all=1[p];[0:a][p]amix=inputs=2:duration=first:normalize=0[a]"
            ffmpeg(['-i',joined,'-i',asset,'-filter_complex',filters,'-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac',mixed]);joined=mixed
        scenes.append(joined)
    final=out/'film.mp4'
    concat_media(scenes,final,credit=True)
    write(out/'provenance.json',{'plan':plan,'jobs':state['jobs'],'sha256':digest(final),'probe':probe(final)})
    print(final)
    return final

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['init','check','status','next','review','accept','retry','recover','assemble'])
    p.add_argument('project',type=Path)
    p.add_argument('--recipes',nargs='+',choices=CASES,default=['K1'])
    p.add_argument('--server',default='http://127.0.0.1:8188')
    p.add_argument('--comfy-root',type=Path)
    p.add_argument('--model-map',type=Path)
    p.add_argument('--online',action='store_true')
    p.add_argument('--mode',choices=['guided','autonomous'],default='guided')
    p.add_argument('--max-takes',type=int,default=3)
    p.add_argument('--max-renders',type=int)
    p.add_argument('--assessment',type=Path)
    p.add_argument('--job');p.add_argument('--note');p.add_argument('--timeout',type=float,default=3600)
    args=p.parse_args();args.server=__import__('doctor').local_server(args.server)
    project=args.project.resolve()
    if args.command=='init':
        if args.max_takes<1 or (args.max_renders is not None and args.max_renders<1):p.error('Budgets must be positive')
        plan=init(project,args.recipes);plan['review_mode']=args.mode
        plan['limits']['max_takes_per_stage']=args.max_takes
        if args.max_renders is not None:plan['limits']['max_render_stages']=args.max_renders
        write(project/'film.json',plan);print(project/'film.json');return
    plan=load(project/'film.json');state=load(project/'state.json')
    if args.command=='check':check(project,plan,args);return
    if args.command=='status':
        print(json.dumps([{'job':key,'status':state['jobs'].get(key,{}).get('status','pending')} for _,_,key in jobs(plan)],indent=2));return
    with lock(project):
        # Read mutable state after acquiring the lock, not before another controller finishes.
        plan=load(project/'film.json');state=load(project/'state.json')
        if args.command=='next':
            if not args.comfy_root:p.error('--comfy-root required')
            next_job(project,plan,state,args)
        elif args.command=='assemble':assemble(project,plan,state)
        elif args.command=='review':review_material(project,plan,state,args.job)
        elif args.command=='accept':
            unchanged(project,plan,state)
            if args.assessment:
                agent_accept(project,plan,state,args.job,args.assessment);return
            if plan.get('review_mode')=='autonomous':raise ValueError('Autonomous acceptance requires --assessment; a note alone is insufficient')
            if not args.note:p.error('--note records what the user accepted')
            item=state['jobs'].get(args.job,{})
            if item.get('status')!='review':raise ValueError('Only a completed reviewed stage can be accepted')
            item.update(status='accepted',note=args.note)
            state['reviews'].append({'job':args.job,'note':args.note,'time':time.time()});write(project/'state.json',state)
        elif args.command=='retry':
            keys=[k for _,_,k in jobs(plan)]
            if args.job not in keys:raise ValueError('Unknown job')
            queue=runner.api(args.server,'/queue')
            if queue.get('queue_running') or queue.get('queue_pending'):raise ValueError('Wait for backend idle before retry')
            # Conservative invalidation also catches dependencies outside the immediate chain.
            history=project/'history';history.mkdir(exist_ok=True)
            write(history/(uuid.uuid4().hex+'.json'),state)
            for key in keys[keys.index(args.job):]:state['jobs'].pop(key,None)
            write(project/'state.json',state)
        elif args.command=='recover':
            item=state['jobs'].get(args.job,{})
            if item.get('status')!='submitted':raise ValueError('Job is not awaiting recovery')
            work=confined(project,item['work']);submission=load(work/'render.submission.json')
            h=runner.api(item['server'],'/history/'+submission['prompt_id']).get(submission['prompt_id'])
            if not h or not h.get('status',{}).get('completed') or h['status'].get('status_str')=='error':
                raise ValueError('No successful completed history; inspect backend before retrying')
            item['video'],item['latents']=collect(h,load(work/'render.submitted.json'),Path(item['comfy_root']))
            scene,name,_=next(x for x in jobs(plan) if x[2]==args.job)
            review_preview(project,scene,name,state,item)
            write(work/'render.history.json',h);item['status']='review';write(project/'state.json',state)

if __name__=='__main__':main()
