import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# Add src to sys.path to allow importing server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
sys.modules['moviepy'] = MagicMock()
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
sys.modules['cv2'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['numexpr'] = MagicMock()
sys.modules['pydantic'] = MagicMock()

# Import server after mocking
import src.server as server

class TestClipLimit(unittest.TestCase):
    def setUp(self):
        # Clear CLIPS before each test
        server.CLIPS.clear()

    def test_clip_limit_reached(self):
        """Test that register_clip raises RuntimeError when MAX_CLIPS is reached."""
        # Set a small limit for testing
        limit = 5
        with patch.object(server, 'MAX_CLIPS', limit):
            # Fill CLIPS up to the limit
            for i in range(limit):
                server.CLIPS[str(i)] = MagicMock()

            # Attempt to register one more clip
            new_clip = MagicMock()
            with self.assertRaisesRegex(RuntimeError, rf"Maximum number of clips \({limit}\) reached"):
                server.register_clip(new_clip)

    def test_clip_limit_not_reached(self):
        """Test that register_clip works fine when below the limit."""
        limit = 5
        with patch.object(server, 'MAX_CLIPS', limit):
            # Fill CLIPS up to limit - 1
            for i in range(limit - 1):
                server.CLIPS[str(i)] = MagicMock()

            # Attempt to register one more clip (should succeed)
            new_clip = MagicMock()
            clip_id = server.register_clip(new_clip)
            self.assertIn(clip_id, server.CLIPS)
            self.assertEqual(server.CLIPS[clip_id], new_clip)

if __name__ == '__main__':
    unittest.main()
