import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('render',Path(__file__).resolve().parents[1]/'scripts/render.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
class RenderTests(unittest.TestCase):
    def test_invalid_content(self):
        for data in [{'scenes':[]},{'scenes':[{'heading':'a'}]},{'scenes':[{'heading':'a','narration':'b','kind':'unknown'}]}]:
            with self.assertRaises(ValueError): r.validate_content(data)
    def test_time_rollover(self):
        self.assertEqual(r.subtitle_time(59.9996),'00:01:00,000')
    def test_animation_changes_pixels(self):
        scene={'heading':'VOYAGER','narration':'Deneme','kind':'space'}
        self.assertNotEqual(r.frame(scene,0,0,1).tobytes(),r.frame(scene,.5,0,1).tobytes())
if __name__=='__main__': unittest.main()
