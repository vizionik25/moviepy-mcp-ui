import unittest
import os
import sys
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add src to sys.path to allow importing server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure FastMCP mock
fastmcp_mock = MagicMock()
mock_mcp_instance = MagicMock()

def identity_decorator(func):
    return func

mock_mcp_instance.tool.side_effect = identity_decorator
mock_mcp_instance.prompt.side_effect = identity_decorator
fastmcp_mock.FastMCP.return_value = mock_mcp_instance

# Configure MoviePy Mock
moviepy_mock = MagicMock()
moviepy_mock.__all__ = [
    "ImageClip", "VideoFileClip", "ImageSequenceClip", "TextClip", "ColorClip",
    "CompositeVideoClip", "clips_array", "concatenate_videoclips",
    "CompositeAudioClip", "concatenate_audioclips", "AudioFileClip",
    "vfx", "afx", "SubtitlesClip", "CreditsClip"
]
moviepy_mock.ImageClip = MagicMock()

# Apply mocks to sys.modules
sys.modules['fastmcp'] = fastmcp_mock
sys.modules['moviepy'] = moviepy_mock
sys.modules['moviepy.video'] = MagicMock()
sys.modules['moviepy.video.tools'] = MagicMock()
sys.modules['moviepy.video.tools.drawing'] = MagicMock()
sys.modules['moviepy.video.tools.cuts'] = MagicMock()
sys.modules['moviepy.video.io'] = MagicMock()
sys.modules['moviepy.video.io.ffmpeg_tools'] = MagicMock()
sys.modules['moviepy.video.tools.subtitles'] = MagicMock()
sys.modules['moviepy.video.tools.credits'] = MagicMock()
sys.modules['mcp_ui'] = MagicMock()
sys.modules['mcp_ui.core'] = MagicMock()
#  # Removed
sys.modules['numpy'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['numexpr'] = MagicMock()
sys.modules['pydantic'] = MagicMock()

# Import after mocking
from src.server import image_clip, CLIPS

class TestImageClip(unittest.TestCase):
    def setUp(self):
        # Reset CLIPS between tests to ensure isolation
        CLIPS.clear()

    @patch('src.server.validate_path')
    @patch('os.path.exists')
    @patch('src.server.ImageClip')
    def test_image_clip_valid_duration(self, mock_ImageClip, mock_exists, mock_validate_path):
        """Test image_clip with a valid positive duration."""
        filename = "test_image.jpg"
        mock_validate_path.return_value = "/abs/path/to/test_image.jpg"
        mock_exists.return_value = True

        # Setup mock clip
        mock_clip_instance = MagicMock()
        mock_ImageClip.return_value = mock_clip_instance

        duration = 5.0
        clip_id = image_clip(filename, duration=duration)

        # Verify validate_path called
        mock_validate_path.assert_called_with(filename)

        # Verify file existence check
        mock_exists.assert_called_with("/abs/path/to/test_image.jpg")

        # Verify ImageClip created with correct params
        mock_ImageClip.assert_called_with(img="/abs/path/to/test_image.jpg", duration=duration, transparent=True)

        # Verify clip registered
        self.assertIn(clip_id, CLIPS)
        self.assertEqual(CLIPS[clip_id], mock_clip_instance)

    @patch('src.server.validate_path')
    @patch('os.path.exists')
    def test_image_clip_zero_duration(self, mock_exists, mock_validate_path):
        """Test image_clip with zero duration raises ValueError."""
        filename = "test_image.jpg"
        mock_validate_path.return_value = "/abs/path/to/test_image.jpg"
        mock_exists.return_value = True

        with self.assertRaisesRegex(ValueError, "Duration must be positive"):
            image_clip(filename, duration=0)

    @patch('src.server.validate_path')
    @patch('os.path.exists')
    def test_image_clip_negative_duration(self, mock_exists, mock_validate_path):
        """Test image_clip with negative duration raises ValueError."""
        filename = "test_image.jpg"
        mock_validate_path.return_value = "/abs/path/to/test_image.jpg"
        mock_exists.return_value = True

        with self.assertRaisesRegex(ValueError, "Duration must be positive"):
            image_clip(filename, duration=-1.0)

    @patch('src.server.validate_path')
    @patch('os.path.exists')
    def test_image_clip_file_not_found(self, mock_exists, mock_validate_path):
        """Test image_clip raises FileNotFoundError if file does not exist."""
        filename = "missing.jpg"
        mock_validate_path.return_value = "/abs/path/to/missing.jpg"
        mock_exists.return_value = False

        with self.assertRaisesRegex(FileNotFoundError, f"File {mock_validate_path.return_value} not found."):
            image_clip(filename, duration=5.0)

if __name__ == '__main__':
    unittest.main()
