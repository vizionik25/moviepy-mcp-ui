import unittest
import os
import sys
from unittest.mock import MagicMock

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Mock modules
sys.modules['fastmcp'] = MagicMock()
class MockEffect:
    def __init__(self, *args, **kwargs):
        pass

moviepy_mock = MagicMock()
moviepy_mock.__all__ = [
    "ImageClip", "VideoFileClip", "ImageSequenceClip", "TextClip", "ColorClip",
    "CompositeVideoClip", "clips_array", "concatenate_videoclips",
    "CompositeAudioClip", "concatenate_audioclips", "AudioFileClip",
    "vfx", "afx", "SubtitlesClip", "CreditsClip", "Effect"
]
moviepy_mock.ImageClip = MagicMock()
moviepy_mock.Effect = MockEffect
sys.modules['moviepy'] = moviepy_mock
sys.modules['moviepy.video'] = MagicMock()
sys.modules['moviepy.video.io'] = MagicMock()
sys.modules['moviepy.video.io.ffmpeg_tools'] = MagicMock()
sys.modules['moviepy.video.tools'] = MagicMock()
sys.modules['moviepy.video.tools.drawing'] = MagicMock()
sys.modules['moviepy.video.tools.cuts'] = MagicMock()
sys.modules['moviepy.video.tools.subtitles'] = MagicMock()
sys.modules['moviepy.video.tools.credits'] = MagicMock()
sys.modules['mcp_ui'] = MagicMock()
sys.modules['mcp_ui.core'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['numexpr'] = MagicMock()
sys.modules['pydantic'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['cv2'] = MagicMock()

# Import server after mocking
from server import video_file_clip, validate_path

class TestVideoIO(unittest.TestCase):
    def test_video_file_clip_not_found(self):
        """Test that video_file_clip raises FileNotFoundError when file does not exist."""
        # Use a path that definitely doesn't exist
        non_existent_file = "non_existent_video_12345.mp4"
        if os.path.exists(non_existent_file):
            os.remove(non_existent_file)

        with self.assertRaises(FileNotFoundError):
            video_file_clip(non_existent_file)

if __name__ == '__main__':
    unittest.main()
