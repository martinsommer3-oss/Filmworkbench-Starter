"""Model installation failure paths and portable starter contracts."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import render_example as r
import setup_models as m
import doctor

class SetupTests(unittest.TestCase):
    def test_manifest_covers_all_graph_weights(self):
        known={x['name'] for x in m.entries(True)}
        for p in (r.ROOT/'graphs').glob('*.api.json'):
            for n in r.load(p).values():
                for k,v in n['inputs'].items():
                    if k in doctor.MODEL_FIELDS: self.assertIn(v,known)
        for item in m.entries(True):
            self.assertEqual(len(item['revision']),40)
            self.assertEqual(len(item['sha256']),64)

    def test_starter_no_timeline_or_keystone(self):
        _,graphs=r.prepare('public_nodes')
        kinds={n['class_type'] for g in graphs.values() for n in g.values()}
        self.assertNotIn('H3StageLatent',kinds)
        self.assertNotIn('H3ClownKeyframe',kinds)
        self.assertIn('LTXVConcatAVLatent',kinds)
        self.assertTrue(graphs['S2']['21']['inputs']['enable_temporal_chunking'])
        self.assertTrue(graphs['S2']['ld_s1']['inputs']['stock_format'])

    def test_mapping_valid_and_escape_rejected(self):
        name=m.entries()[0]['name']
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'map.json'
            for value in ['../bad','C:/bad','/bad','sub/../../bad']:
                p.write_text(json.dumps({name:value}),encoding='utf-8')
                with self.assertRaises(ValueError): r.read_model_map(p)
            p.write_text(json.dumps({name:'H3/'+name}),encoding='utf-8')
            _,graphs=r.prepare('mapping')
            r.apply_model_map(graphs,r.read_model_map(p))
            self.assertEqual(graphs['S1']['1']['inputs']['unet_name'],'H3/'+name)

    def test_missing_weight_reports_download_source(self):
        item=m.entries()[0]
        graph={'1':{'class_type':'UNETLoader','inputs':{'unet_name':item['name']}}}
        info={'UNETLoader':{'input':{'required':{'unet_name':[[]]}}}}
        issue=doctor.compare({'S1':graph},info)[0]
        self.assertEqual(issue['source'],item['source'])
        self.assertEqual(issue['target_folder'],'diffusion_models')

    def test_download_and_copy_verified(self):
        data=b'test weights'; model={'id':'small','repo_id':'author/repo','revision':'a'*40,'remote_path':'nested/test.bin','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        with tempfile.TemporaryDirectory() as d:
            stage=Path(d)/'stage'; target=Path(d)/'models/test.bin'
            def fake_download(command,check):
                self.assertIn('--revision',command)
                source=stage/'nested/test.bin';source.parent.mkdir(parents=True);source.write_bytes(data)
            with patch.object(m.subprocess,'run',side_effect=fake_download):
                self.assertEqual(m.install(model,target,stage,'hf'),'downloaded and verified')
            self.assertEqual(target.read_bytes(),data)
            with patch.object(m.subprocess,'run') as download:
                self.assertEqual(m.install(model,target,stage,'hf'),'already verified');download.assert_not_called()

    def test_bad_download_never_installed(self):
        model={'id':'small','repo_id':'author/repo','revision':'a'*40,'remote_path':'bad.bin','bytes':3,'sha256':'0'*64}
        with tempfile.TemporaryDirectory() as d:
            stage=Path(d)/'stage';stage.mkdir();(stage/'bad.bin').write_bytes(b'bad');target=Path(d)/'target.bin'
            with patch.object(m.subprocess,'run'):
                with self.assertRaisesRegex(ValueError,'mismatch'):m.install(model,target,stage,'hf')
            self.assertFalse(target.exists())

    def test_existing_wrong_file_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'existing';target.write_bytes(b'keep')
            with patch.object(m.subprocess,'run') as download:
                with self.assertRaisesRegex(ValueError,'preserved'):m.install({'bytes':1},target,Path(d)/'stage','hf')
                download.assert_not_called()
            self.assertEqual(target.read_bytes(),b'keep')

    def test_target_path_confined(self):
        model=m.entries()[0]
        with self.assertRaises(ValueError):m.target_for(Path('.'),model,{model['name']:'../../../elsewhere'})

if __name__=='__main__': unittest.main()
