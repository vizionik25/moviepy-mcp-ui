import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# Add src to sys.path to allow importing server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Configure FastMCP mock to avoid execution environment issues
fastmcp_mock = MagicMock()
mock_mcp_instance = MagicMock()

# Define a side effect for @mcp.tool and @mcp.prompt to return the original function
# This is crucial so that decorated functions like list_clips remain callable
def identity_decorator(func):
    return func

mock_mcp_instance.tool.side_effect = identity_decorator
mock_mcp_instance.prompt.side_effect = identity_decorator

# Make FastMCP() return our configured instance
fastmcp_mock.FastMCP.return_value = mock_mcp_instance
sys.modules['fastmcp'] = fastmcp_mock

# Mock other external dependencies to isolate the unit test
sys.modules['moviepy'] = MagicMock()
sys.modules['moviepy.video.io.VideoFileClip'] = MagicMock()
sys.modules['moviepy.video.tools.drawing'] = MagicMock()
sys.modules['moviepy.video.tools.cuts'] = MagicMock()
sys.modules['moviepy.video.io.ffmpeg_tools'] = MagicMock()
sys.modules['moviepy.video.tools.subtitles'] = MagicMock()
sys.modules['moviepy.video.tools.credits'] = MagicMock()
sys.modules['mcp_ui'] = MagicMock()
sys.modules['mcp_ui.core'] = MagicMock()
sys.modules['custom_fx'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['numexpr'] = MagicMock()
sys.modules['pydantic'] = MagicMock()

# Import the server module after setting up mocks
import server
from server import get_clip, CLIPS

class TestClipManagement(unittest.TestCase):
    def test_get_clip_success(self):
        """Test retrieving a clip that exists."""
        clip_id = "test_clip_123"
        mock_clip = MagicMock()

        # Patch the CLIPS dictionary in server directly
        with patch.dict(server.CLIPS, {clip_id: mock_clip}, clear=True):
            result = get_clip(clip_id)
            self.assertEqual(result, mock_clip)

    def test_get_clip_failure(self):
        """Test retrieving a clip that does not exist."""
        clip_id = "non_existent_clip"

        # Ensure CLIPS is empty or does not contain the key
        with patch.dict(server.CLIPS, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                get_clip(clip_id)

            self.assertEqual(str(context.exception), f"Clip with ID {clip_id} not found.")

if __name__ == '__main__':
    unittest.main()
