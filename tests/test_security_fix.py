import unittest
import sys
import os
import tempfile
from unittest.mock import MagicMock, patch

# Add src to sys.path
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

from server import write_videofile, CLIPS

class TestSecurityFix(unittest.TestCase):
    def setUp(self):
        CLIPS.clear()
        self.temp_dir = tempfile.gettempdir()

    def test_ffmpeg_params_rejected(self):
        """
        Verify that ffmpeg_params argument is no longer accepted by write_videofile.
        This confirms the fix for the command injection vulnerability.
        """
        mock_clip = MagicMock()
        clip_id = "test_clip_id"
        CLIPS[clip_id] = mock_clip

        dangerous_params = ["-f", "image2", os.path.join(self.temp_dir, "hacked.jpg")]
        output_path = os.path.join(self.temp_dir, "output.mp4")

        with patch('server.validate_write_path', return_value=output_path):
            with self.assertRaises(TypeError) as cm:
                write_videofile(
                    clip_id=clip_id,
                    filename="output.mp4",
                    ffmpeg_params=dangerous_params
                )

            # Verify the error message confirms the unexpected argument
            self.assertIn("unexpected keyword argument 'ffmpeg_params'", str(cm.exception))

    def test_write_videofile_success_without_params(self):
        """
        Verify that write_videofile still works for valid inputs (without ffmpeg_params).
        """
        mock_clip = MagicMock()
        clip_id = "test_clip_id"
        CLIPS[clip_id] = mock_clip

        output_path = os.path.join(self.temp_dir, "output.mp4")

        with patch('server.validate_write_path', return_value=output_path):
            result = write_videofile(
                clip_id=clip_id,
                filename="output.mp4",
                fps=30.0,
                codec="libx264"
            )

            self.assertIn("Successfully wrote video", result)

            # Verify internal call arguments
            mock_clip.write_videofile.assert_called_once()
            call_args = mock_clip.write_videofile.call_args
            self.assertEqual(call_args.kwargs['filename'], output_path)
            self.assertEqual(call_args.kwargs['fps'], 30.0)
            self.assertEqual(call_args.kwargs['codec'], 'libx264')

            # Ensure ffmpeg_params is NOT in the call args (even as None, ideally)
            # Since we removed it from the call, it shouldn't be passed.
            self.assertNotIn('ffmpeg_params', call_args.kwargs)

if __name__ == '__main__':
    unittest.main()
