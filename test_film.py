"""Complete recipe compilation, approvals and changed-input regression tests (CPU)."""
import argparse
import json
from pathlib import Path
import tempfile
import unittest
import shutil
import sys
from unittest.mock import patch
import film

class FilmTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.p=Path(self.tmp.name)/'a project ä'
        self.plan=film.init(self.p,list(film.CASES))
    def tearDown(self):self.tmp.cleanup()
    def args(self):return argparse.Namespace(model_map=None,online=False,server='http://localhost:8188')
    def test_all_recipes_compile_with_closed_dependencies(self):
        graphs=film.check(self.p,self.plan,self.args())
        self.assertEqual(len(graphs),46)
        for key,g in graphs.items():
            for n in g.values():
                self.assertNotEqual(n['class_type'],'H3StageLatent')
                if n['class_type']=='MiniMaxH3MotionContextLoadLatent':
                    self.assertTrue(n['inputs']['latent_path'].startswith('filmworkbench_v011/'))
                for v in n['inputs'].values():
                    if isinstance(v,str):self.assertNotIn('${COMFY_ROOT}',v)
        self.assertEqual(len(self.plan['scenes']),9)
    def test_first_stage_needs_no_prior_latent(self):
        scene=self.plan['scenes'][0];name=film.ordered('K1')[0]
        g,assets=film.compile_graph(self.p,self.plan,scene,name,{'jobs':{}},'take')
        self.assertEqual(len(assets),5)
    def test_doctor_all_checks_public_adapted_nodes(self):
        import doctor,io,contextlib
        def inspect(graphs,info):
            self.assertEqual(len(graphs),44)
            kinds={n['class_type'] for g in graphs.values() for n in g.values()}
            self.assertNotIn('H3StageLatent',kinds)
            self.assertIn('LTXVConcatAVLatent',kinds)
            self.assertIn('H3ClownKeyframe',kinds)
            return []
        with patch.object(sys,'argv',['doctor.py','--all','--online']),patch.object(doctor.runner,'api',return_value={}),patch.object(doctor,'compare',side_effect=inspect) as compare,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(doctor.main(),0)
            compare.assert_called_once()
    def test_continuation_requires_accepted_parent(self):
        scene=self.plan['scenes'][1]
        for status in ['review','submitted']:
            with self.assertRaisesRegex(ValueError,'Approve predecessor'):
                film.compile_graph(self.p,self.plan,scene,'K2_B2_S1',{'jobs':{'02_K2/K1_A1_S1':{'status':status}}},'take')
    def test_changed_image_invalidates_accepted_output(self):
        scene=self.plan['scenes'][0];name='K1_A1_S1'
        state={'jobs':{'01_K1/'+name:{'status':'accepted','fingerprint':film.fingerprint(self.p,scene,name)}}}
        image=next(iter(scene['assets'].values()));path=self.p/image
        path.write_bytes(path.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'Inputs changed'):film.unchanged(self.p,self.plan,state)
    def test_changed_prompt_invalidates_accepted_output(self):
        scene=self.plan['scenes'][0];name='K1_A1_S1'
        state={'jobs':{'01_K1/'+name:{'fingerprint':film.fingerprint(self.p,scene,name)}}}
        (self.p/scene['prompts'][name]).write_text('new action')
        with self.assertRaisesRegex(ValueError,'Inputs changed'):film.unchanged(self.p,self.plan,state)
    def test_unrendered_prompt_can_be_edited(self):
        scene=self.plan['scenes'][0];name='K1_A1_S1'
        (self.p/scene['prompts'][name]).write_text('new action')
        film.unchanged(self.p,self.plan,{'jobs':{}})
        g,_=film.compile_graph(self.p,self.plan,scene,name,{'jobs':{}},'take')
        self.assertEqual(g['40']['inputs']['prompt'],'new action')
    def test_no_assembly_before_acceptance(self):
        with self.assertRaisesRegex(ValueError,'Accept all'):film.assemble(self.p,self.plan,{'jobs':{}})
    def test_lock_prevents_second_controller(self):
        with film.lock(self.p):
            with self.assertRaises(FileExistsError):
                with film.lock(self.p):pass
    def test_no_external_asset_path(self):
        s=self.plan['scenes'][0];s['assets'][next(iter(s['assets']))]='../../private.png'
        with self.assertRaisesRegex(ValueError,'leaves its root'):
            film.compile_graph(self.p,self.plan,s,'K1_A1_S1',{'jobs':{}},'take')
    def test_original_sources_not_modified(self):
        src=film.ROOT/'graphs/K1_A1_S2.api.json';before=film.digest(src)
        film.check(self.p,self.plan,self.args())
        self.assertEqual(film.digest(src),before)
        self.assertEqual(film.load(src)['22']['class_type'],'H3StageLatent')
    def test_market_uses_distinct_s1_s2_parents(self):
        g=film.check(self.p,self.plan,self.args())['09_MARKET/MARKET_G3_S2']
        self.assertIn('MARKET_G2_S2/',g['ld2']['inputs']['latent_path'])
        self.assertIn('MARKET_G3_S1/',g['ld_s1']['inputs']['latent_path'])
    def test_attempts_have_different_output_paths(self):
        s=self.plan['scenes'][0]
        a,_=film.compile_graph(self.p,self.plan,s,'K1_A1_S1',{'jobs':{}},'take1')
        b,_=film.compile_graph(self.p,self.plan,s,'K1_A1_S1',{'jobs':{}},'take2')
        self.assertNotEqual(a['lat_s1']['inputs']['filename_prefix'],b['lat_s1']['inputs']['filename_prefix'])
    def test_timeout_preserves_submission_and_blocks_duplicate(self):
        args=self.args();args.comfy_root=self.p/'backend';args.timeout=1
        (args.comfy_root/'input').mkdir(parents=True);(args.comfy_root/'output').mkdir()
        state={'jobs':{},'reviews':[]}
        with patch.object(film.runner,'api',return_value={}),patch.object(film.runner,'check_backend',return_value=[]),patch.object(film.runner,'execute',side_effect=TimeoutError):
            with self.assertRaises(TimeoutError):film.next_job(self.p,self.plan,state,args)
        saved=film.load(self.p/'state.json');self.assertEqual(saved['jobs']['01_K1/K1_A1_S1']['status'],'submitted')
        with patch.object(film.runner,'execute') as execute:
            with self.assertRaisesRegex(ValueError,'submitted'):film.next_job(self.p,self.plan,saved,args)
            execute.assert_not_called()
    def test_retry_invalidates_all_descendants_and_preserves_history(self):
        state={'jobs':{k:{'status':'accepted'} for _,_,k in film.jobs(self.plan)},'reviews':[]}
        film.write(self.p/'state.json',state)
        with patch.object(sys,'argv',['film.py','retry',str(self.p),'--job','02_K2/K2_B2_S1']),patch.object(film.runner,'api',return_value={}):film.main()
        saved=film.load(self.p/'state.json')
        self.assertIn('01_K1/K1_A1_S1',saved['jobs'])
        self.assertNotIn('02_K2/K2_B2_S1',saved['jobs'])
        self.assertNotIn('09_MARKET/MARKET_G4_S2',saved['jobs'])
        self.assertEqual(len(list((self.p/'history').glob('*.json'))),1)
    def test_accept_requires_completed_review_and_user_note(self):
        with patch.object(sys,'argv',['film.py','accept',str(self.p),'--job','01_K1/K1_A1_S1','--note','approved']):
            with self.assertRaisesRegex(ValueError,'completed reviewed'):film.main()
    def autonomous_fixture(self):
        self.plan['review_mode']='autonomous'
        root=self.p/'backend';(root/'output').mkdir(parents=True)
        video=root/'output/test.mp4';video.write_bytes(b'unit test only')
        key='01_K1/K1_A1_S1';scene=self.plan['scenes'][0]
        item={'status':'review','fingerprint':film.fingerprint(self.p,scene,'K1_A1_S1'),
              'video':'test.mp4','comfy_root':str(root),'work':'runs/test'}
        state={'jobs':{key:item},'reviews':[]}
        report={'job':key,'fingerprint':item['fingerprint'],'video_sha256':film.digest(video),'decision':'accept',
                'reviewer':'test fixture','observed_end_state':'test state',
                'checks':{k:{'status':'pass','evidence':'test observation'} for k in ('action','identity','continuity','motion','audio','story')},'limitations':[]}
        path=self.p/'assessment.json';film.write(path,report)
        return key,state,report,path
    def test_agent_acceptance_requires_explicit_autonomous_mode(self):
        key,state,report,path=self.autonomous_fixture();self.plan['review_mode']='guided'
        with self.assertRaisesRegex(ValueError,'explicitly commissioned'):film.agent_accept(self.p,self.plan,state,key,path)
    def test_agent_acceptance_rejects_stale_take(self):
        key,state,report,path=self.autonomous_fixture();report['video_sha256']='old';film.write(path,report)
        with self.assertRaisesRegex(ValueError,'video changed'):film.agent_accept(self.p,self.plan,state,key,path)
    def test_agent_acceptance_rejects_failed_or_missing_review(self):
        key,state,report,path=self.autonomous_fixture();report['checks']['action']['status']='fail';film.write(path,report)
        with self.assertRaisesRegex(ValueError,'failed check'):film.agent_accept(self.p,self.plan,state,key,path)
        report['checks']['action']['status']='unknown';film.write(path,report)
        with self.assertRaisesRegex(ValueError,'unreviewed core'):film.agent_accept(self.p,self.plan,state,key,path)
    def test_partial_audio_review_must_be_disclosed(self):
        key,state,report,path=self.autonomous_fixture();report['checks']['audio']['status']='unknown';film.write(path,report)
        with self.assertRaisesRegex(ValueError,'Disclose'):film.agent_accept(self.p,self.plan,state,key,path)
        report['limitations']=['Speech meaning was not verified.'];film.write(path,report)
        film.agent_accept(self.p,self.plan,state,key,path)
        self.assertEqual(state['jobs'][key]['assessment']['limitations'],report['limitations'])
    def test_autonomous_budget_cannot_reset_on_retry(self):
        state={'jobs':{},'attempts':{'01_K1/K1_A1_S1':3},'reviews':[]}
        with self.assertRaisesRegex(ValueError,'budget exhausted'):film.next_job(self.p,self.plan,state,self.args())
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
    def test_concat_has_exact_frames_and_audio_duration(self):
        src=self.p/'fixture.mp4';out=self.p/'joined.mp4'
        film.ffmpeg(['-f','lavfi','-i','color=c=blue:s=160x96:r=24:d=1','-f','lavfi','-i','sine=frequency=220:sample_rate=48000:duration=1','-c:v','libx264','-c:a','aac','-shortest',src])
        film.concat_media([src,src,src],out,credit=True)
        info=film.probe(out)
        self.assertEqual(next(s for s in info['streams'] if s['codec_type']=='video')['nb_frames'],'72')
        self.assertAlmostEqual(float(next(s for s in info['streams'] if s['codec_type']=='audio')['duration']),3,places=2)
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
    def test_review_material_contains_exact_first_and_last_frames(self):
        root=self.p/'backend';(root/'output').mkdir(parents=True);src=root/'output/fixture.mp4'
        film.ffmpeg(['-f','lavfi','-i',"nullsrc=s=160x96:r=24:d=2,geq=lum='if(lt(N,24),0,255)':cb=128:cr=128",'-f','lavfi','-i','sine=frequency=220:sample_rate=48000:duration=2','-c:v','libx264','-c:a','aac','-shortest',src])
        scene=self.plan['scenes'][0];key='01_K1/K1_A1_S1'
        item={'status':'review','fingerprint':film.fingerprint(self.p,scene,'K1_A1_S1'),'comfy_root':str(root),'video':'fixture.mp4','work':'runs/material'}
        (self.p/item['work']).mkdir(parents=True)
        state={'jobs':{key:item},'reviews':[]}
        report=film.review_material(self.p,self.plan,state,key)
        means=[]
        for name in ['start.jpg','end.jpg']:
            pixel=film.subprocess.check_output(['ffmpeg','-v','error','-i',str(report.parent/name),'-vf','scale=1:1,format=gray','-f','rawvideo','-'])
            means.append(pixel[0])
        self.assertLess(means[0],15);self.assertGreater(means[1],240)

if __name__=='__main__':unittest.main()
