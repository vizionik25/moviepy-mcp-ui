import unittest
import sys
import os
from unittest.mock import MagicMock
from pathlib import Path

# Clean sys.modules to ensure fresh mocks
for mod in ["src.server", "fastmcp", "moviepy"]:
    if mod in sys.modules:
        del sys.modules[mod]

# Mock dependencies
sys.modules["fastmcp"] = MagicMock()
sys.modules["moviepy"] = MagicMock()
sys.modules["moviepy.video.tools.drawing"] = MagicMock()
sys.modules["moviepy.video.tools.cuts"] = MagicMock()
sys.modules["moviepy.video.io.ffmpeg_tools"] = MagicMock()
sys.modules["moviepy.video.tools.subtitles"] = MagicMock()
sys.modules["moviepy.video.tools.credits"] = MagicMock()
sys.modules["moviepy.audio.tools.cuts"] = MagicMock()
sys.modules["moviepy.config"] = MagicMock()
sys.modules["mcp_ui.core"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["numexpr"] = MagicMock()
sys.modules["custom_fx"] = MagicMock()
sys.modules["pydantic"] = MagicMock()

class MockFastMCP:
    def __init__(self, name):
        pass
    def tool(self, func):
        return func
    def prompt(self, func):
        return func
    def run(self, transport):
        pass

sys.modules["fastmcp"].FastMCP = MockFastMCP

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import src.server as server

class TestSecurityFix(unittest.TestCase):
    def setUp(self):
        self.source_file = "output/dummy_source.mp4"
        os.makedirs("output", exist_ok=True)
        with open(self.source_file, "w") as f:
            f.write("dummy")
        # Ensure OUTPUT_DIR is set up correctly in server
        server.OUTPUT_DIR = Path("output").resolve()

    def test_tools_ffmpeg_extract_subclip_block_write_to_src(self):
        """Test that writing to src/ is blocked."""
        target = "src/vulnerable.txt"
        with self.assertRaises(ValueError) as cm:
            server.tools_ffmpeg_extract_subclip(self.source_file, 0, 1, targetname=target)
        self.assertIn("Write access to path", str(cm.exception))

    def test_tools_ffmpeg_extract_subclip_allow_write_to_output(self):
        """Test that writing to output/ is allowed."""
        target = "output/safe.mp4"
        server.tools_ffmpeg_extract_subclip(self.source_file, 0, 1, targetname=target)

    def test_tools_ffmpeg_extract_subclip_default_target(self):
        """Test default target generation is safe."""
        server.tools_ffmpeg_extract_subclip(self.source_file, 0, 1)

if __name__ == '__main__':
    unittest.main()
