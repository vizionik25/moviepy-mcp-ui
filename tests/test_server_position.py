import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to sys.path to allow importing server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Configure FastMCP mock to act as a transparent decorator
fastmcp_mock = MagicMock()
mock_mcp_instance = MagicMock()

# Define a side effect for @mcp.tool and @mcp.prompt to return the original function
def identity_decorator(func):
    return func

mock_mcp_instance.tool.side_effect = identity_decorator
mock_mcp_instance.prompt.side_effect = identity_decorator

# Make FastMCP() return our configured instance
fastmcp_mock.FastMCP.return_value = mock_mcp_instance

# Apply mocks to sys.modules
sys.modules['fastmcp'] = fastmcp_mock
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
sys.modules['moviepy.video.tools'] = MagicMock()
sys.modules['moviepy.video.tools.drawing'] = MagicMock()
sys.modules['moviepy.video.tools.cuts'] = MagicMock()
sys.modules['moviepy.video.io'] = MagicMock()
sys.modules['moviepy.video.io.ffmpeg_tools'] = MagicMock()
sys.modules['moviepy.video.tools.subtitles'] = MagicMock()
sys.modules['moviepy.video.tools.credits'] = MagicMock()
sys.modules['mcp_ui'] = MagicMock()
sys.modules['mcp_ui.core'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['numexpr'] = MagicMock()
sys.modules['pydantic'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['PIL'] = MagicMock()

# Now import the functions to test
from server import set_position, CLIPS, register_clip

class TestSetPosition(unittest.TestCase):
    def setUp(self):
        # Clear CLIPS before each test
        CLIPS.clear()

    def test_missing_position_args(self):
        """Test that set_position raises ValueError when no position arguments are provided."""
        # Create a mock clip and register it
        mock_clip = MagicMock()
        clip_id = register_clip(mock_clip)

        # Verify that calling set_position without x, y, or pos_str raises ValueError
        with self.assertRaises(ValueError) as cm:
            set_position(clip_id)

        self.assertEqual(str(cm.exception), "Provide x, y, or pos_str")

    def test_set_position_xy(self):
        """Test setting position with x and y coordinates."""
        mock_clip = MagicMock()
        mock_clip.with_position.return_value = mock_clip  # method chaining returns clip
        clip_id = register_clip(mock_clip)

        result_id = set_position(clip_id, x=100, y=200)

        # Verify get_clip was called (implicit in set_position)
        # Verify with_position was called with correct tuple
        mock_clip.with_position.assert_called_with((100, 200), relative=False)

        # Verify the result is a new clip ID (since register_clip is called)
        self.assertNotEqual(clip_id, result_id)
        self.assertIn(result_id, CLIPS)

    def test_set_position_pos_str(self):
        """Test setting position with a position string."""
        mock_clip = MagicMock()
        mock_clip.with_position.return_value = mock_clip
        clip_id = register_clip(mock_clip)

        result_id = set_position(clip_id, pos_str="center")

        mock_clip.with_position.assert_called_with("center", relative=False)
        self.assertIn(result_id, CLIPS)

    def test_set_position_x_only(self):
        """Test setting position with only x coordinate."""
        mock_clip = MagicMock()
        mock_clip.with_position.return_value = mock_clip
        clip_id = register_clip(mock_clip)

        result_id = set_position(clip_id, x=50)

        # Verify it defaults to ("center") for the missing coordinate
        mock_clip.with_position.assert_called_with((50, "center"), relative=False)
        self.assertIn(result_id, CLIPS)

    def test_set_position_y_only(self):
        """Test setting position with only y coordinate."""
        mock_clip = MagicMock()
        mock_clip.with_position.return_value = mock_clip
        clip_id = register_clip(mock_clip)

        result_id = set_position(clip_id, y=75)

        # Verify it defaults to ("center") for the missing coordinate
        mock_clip.with_position.assert_called_with(("center", 75), relative=False)
        self.assertIn(result_id, CLIPS)

    def test_set_position_invalid_clip(self):
        """Test setting position on a non-existent clip."""
        with self.assertRaises(ValueError) as cm:
            set_position("non_existent_id", x=10)

        self.assertIn("Clip with ID non_existent_id not found", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
