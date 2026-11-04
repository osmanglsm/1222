import importlib.util,unittest
from pathlib import Path
class TestEpisode(unittest.TestCase):
 def test_script_has_ten_lines(self):
  import json
  data=json.loads(Path("content/13kat_episode01.json").read_text(encoding="utf8"))
  self.assertEqual(len(data["lines"]),10)
 def test_scene_renderer(self):
  spec=importlib.util.spec_from_file_location("ep","scripts/episode_pipeline.py")
  m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  im=m.paint(3,0,"Kapı aralandı.")
  self.assertEqual(im.size,(540,960))
if __name__=="__main__":unittest.main()
