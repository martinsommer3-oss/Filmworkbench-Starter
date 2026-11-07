"""CPU-only failure-path and package-contract tests. No backend or GPU required."""
import copy
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import doctor
import render_example as r

class StarterTests(unittest.TestCase):
    def test_real_assets_and_links(self):
        example,graphs=r.prepare('test_contract')
        self.assertEqual(set(graphs),{'S1','S2'})
        self.assertGreater(len(example['assets']),0)

    def test_reject_path_escape(self):
        with self.assertRaises(ValueError): r.confined(r.ROOT,'../outside.txt')

    def test_reject_run_id_escape(self):
        with self.assertRaises(ValueError): r.prepare('../outside')

    def test_hash_failure_blocks_preparation(self):
        with patch.object(r,'digest',return_value='incorrect'):
            with self.assertRaisesRegex(ValueError,'hash mismatch'): r.prepare('test')

    def test_local_only(self):
        for address in ['https://127.0.0.1:8188','http://example.com','http://localhost@evil.com','http://localhost:8188/?key=secret']:
            with self.assertRaises(ValueError): doctor.local_server(address)
        self.assertEqual(doctor.local_server('http://localhost:8188/'),'http://localhost:8188')

    def test_missing_node_has_source(self):
        graph={'1':{'class_type':'H3StageLatent','inputs':{}}}
        issues=doctor.compare({'S2':graph},{})
        self.assertEqual(issues[0]['type'],'missing_node')
        self.assertIn('obvpm-timeline',issues[0]['source'])

    def test_model_subdirectory_not_silently_changed(self):
        graph={'1':{'class_type':'UNETLoader','inputs':{'unet_name':'exact.safetensors'}}}
        original=copy.deepcopy(graph)
        info={'UNETLoader':{'input':{'required':{'unet_name':[['subdir/exact.safetensors']]}}}}
        self.assertEqual(doctor.compare({'S1':graph},info)[0]['type'],'model_path_mismatch')
        self.assertEqual(graph,original)

    def test_incompatible_setting(self):
        graph={'1':{'class_type':'Setting','inputs':{'mode':'old'}}}
        info={'Setting':{'input':{'required':{'mode':[['new']]}}}}
        self.assertEqual(doctor.compare({'S1':graph},info)[0]['type'],'unsupported_setting')

    def test_busy_backend_never_submits(self):
        with patch.object(r,'api',return_value={'queue_running':[1]}) as api:
            with self.assertRaisesRegex(RuntimeError,'busy'):
                r.execute('http://localhost:8188',{},Path('.'),'S1',1)
            self.assertEqual(api.call_count,1)
            self.assertEqual(api.call_args.args[1],'/queue')

    def test_failed_render_is_not_success(self):
        responses=[{}, {'prompt_id':'test'}, {'test':{'status':{'status_str':'error','completed':True}}}]
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(r,'api',side_effect=responses):
                with self.assertRaisesRegex(RuntimeError,'S1 failed'):
                    r.execute('http://localhost:8188',{},Path(directory),'S1',10)

    def test_all_reference_hashes(self):
        for name,item in r.load(r.ROOT/'assets/manifest.json').items():
            self.assertEqual(r.digest(r.confined(r.ROOT,name)),item['sha256'],name)

    def test_all_parent_latents_have_producers(self):
        inventory=r.load(r.ROOT/'graphs/inventory.json')
        for name,entry in inventory.items():
            for dep in entry['dependencies']: self.assertTrue(dep['producers'],name)

if __name__=='__main__': unittest.main()
