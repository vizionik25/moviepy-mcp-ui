import unittest
import os
import tempfile
import sys
from unittest.mock import MagicMock, patch
from pathlib import Path

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
mock_moviepy = MagicMock()
mock_moviepy.__all__ = ["ColorClip", "ImageClip", "TextClip", "CompositeVideoClip", "AudioFileClip", "VideoFileClip"]
sys.modules['moviepy'] = mock_moviepy
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
sys.modules['custom_fx'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['numexpr'] = MagicMock()
sys.modules['pydantic'] = MagicMock()

from server import validate_path, validate_write_path, OUTPUT_DIR, color_clip  # noqa: E402

class TestValidatePath(unittest.TestCase):
    def setUp(self):
        self.cwd = Path.cwd().resolve()
        self.tmp = Path("/tmp").resolve() if Path("/tmp").exists() else Path("/tmp")

    def test_valid_path_in_cwd(self):
        """Test a valid file path within the current working directory."""
        filename = "test_file.txt"
        # Create a dummy file
        with open(filename, "w") as f:
            f.write("test")
        try:
            result = validate_path(filename)
            self.assertEqual(result, str(self.cwd / filename))
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def test_valid_path_in_tmp(self):
        """Test a valid file path within /tmp."""
        if not os.path.exists("/tmp"):
            self.skipTest("/tmp does not exist")

        with tempfile.NamedTemporaryFile(dir="/tmp", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            result = validate_path(tmp_path)
            # On some systems /tmp is a symlink to /private/tmp, resolve handles this
            expected = str(Path(tmp_path).resolve())
            self.assertEqual(result, expected)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_path_traversal_attempt(self):
        """Test path traversal attempts using ../"""
        # Attempt to access root or other restricted dirs via traversal
        # This path eventually resolves to /etc/passwd or similar
        # We use a known existing file outside like /bin/sh or /etc/passwd to ensure resolve works as expected
        target = "/etc/passwd"
        if not os.path.exists(target):
            target = "/bin/sh"

        # Construct a relative path that goes up enough levels
        # e.g. ../../../../../etc/passwd
        # Since we are in CWD, we just need enough ..
        rel_path = "../" * 20 + target.lstrip("/")

        with self.assertRaises(ValueError):
            validate_path(rel_path)

    def test_absolute_path_outside_allowed(self):
        """Test absolute path to a restricted file."""
        target = "/etc/passwd"
        if not os.path.exists(target):
            target = "/bin/sh"

        with self.assertRaises(ValueError):
            validate_path(target)

    def test_symlink_attack(self):
        """Test a symlink within allowed dir pointing outside."""
        link_name = "suspicious_link"
        target = "/etc/passwd"
        if not os.path.exists(target):
            target = "/bin/sh"

        if os.path.exists(link_name):
            os.remove(link_name)

        try:
            os.symlink(target, link_name)
            # validate_path resolves the path. It should resolve to the target (outside) and raise ValueError
            with self.assertRaises(ValueError):
                validate_path(link_name)
        except OSError:
            # Symlinks might not be supported or allowed in the environment
            self.skipTest("Symlinks not supported or failed to create")
        finally:
            if os.path.islink(link_name):
                os.unlink(link_name)

    def test_non_existent_file_in_cwd(self):
        """Test a non-existent file path inside CWD (should be allowed)."""
        filename = "non_existent_file_12345.txt"
        if os.path.exists(filename):
            os.remove(filename)

        # Should NOT raise ValueError
        result = validate_path(filename)
        self.assertEqual(result, str(self.cwd / filename))

    def test_non_existent_file_outside(self):
        """Test a non-existent file path outside allowed dirs."""
        filename = "/etc/non_existent_file_12345.txt"
        with self.assertRaises(ValueError):
            validate_path(filename)

    def test_recursive_symlink(self):
        """Test a recursive symlink."""
        link_name = "recursive_link"
        if os.path.exists(link_name):
            os.remove(link_name)
        try:
            os.symlink(link_name, link_name)
            # validate_path catches RuntimeError and raises ValueError
            with self.assertRaises(ValueError):
                validate_path(link_name)
        except OSError:
            self.skipTest("Symlinks not supported")
        finally:
             if os.path.islink(link_name):
                os.unlink(link_name)

    def test_null_byte(self):
        """Test path with null byte."""
        with self.assertRaises(ValueError):
            validate_path("test\0file.txt")


class TestValidateWritePath(unittest.TestCase):
    def setUp(self):
        self.output_dir = OUTPUT_DIR.resolve()
        self.tmp = Path("/tmp").resolve() if Path("/tmp").exists() else Path("/tmp")
        # Ensure output dir exists (it should, but just in case)
        self.output_dir.mkdir(exist_ok=True)

    def test_write_to_output_dir(self):
        """Test writing to the allowed output directory."""
        filename = str(self.output_dir / "test.mp4")
        result = validate_write_path(filename)
        self.assertEqual(result, filename)

    def test_write_to_output_dir_relative(self):
        """Test writing to the allowed output directory using relative path."""
        # Assuming CWD is project root
        filename = "output/test.mp4"
        result = validate_write_path(filename)
        self.assertEqual(result, str(self.output_dir / "test.mp4"))

    def test_write_to_tmp(self):
        """Test writing to /tmp."""
        if not os.path.exists("/tmp"):
            self.skipTest("/tmp does not exist")
        filename = "/tmp/test.mp4"
        result = validate_write_path(filename)
        self.assertEqual(result, str(self.tmp / "test.mp4"))

    def test_write_to_cwd_blocked(self):
        """Test writing to CWD (blocked)."""
        filename = "test.mp4" # implied in CWD
        with self.assertRaises(ValueError):
            validate_write_path(filename)

    def test_write_to_src_blocked(self):
        """Test writing to src/ directory (blocked)."""
        filename = "src/server.py"
        with self.assertRaises(ValueError):
            validate_write_path(filename)


class TestColorClip(unittest.TestCase):
    def test_color_clip_valid(self):
        """Test creating a valid color clip."""
        size = [1920, 1080]
        color = [255, 0, 0]
        duration = 5.0

        with patch('server.register_clip') as mock_register, \
             patch('server.ColorClip') as mock_color_clip_cls:

            mock_register.return_value = "test_clip_id"
            result = color_clip(size, color, duration)

            self.assertEqual(result, "test_clip_id")
            mock_color_clip_cls.assert_called_once()

            # Verify arguments passed to ColorClip
            _, kwargs = mock_color_clip_cls.call_args
            self.assertEqual(kwargs['size'], (1920, 1080))
            self.assertEqual(kwargs['duration'], 5.0)

    def test_color_clip_invalid_duration(self):
        """Test that non-positive duration raises ValueError."""
        size = [100, 100]
        color = [0, 0, 0]
        with self.assertRaisesRegex(ValueError, "Duration must be positive"):
            color_clip(size, color, duration=0)

        with self.assertRaisesRegex(ValueError, "Duration must be positive"):
            color_clip(size, color, duration=-1.0)

    def test_color_clip_invalid_size_empty(self):
        """Test that empty size raises ValueError."""
        with self.assertRaisesRegex(ValueError, "Size must be a list of two positive integers"):
            color_clip([], [0,0,0])

    def test_color_clip_invalid_size_len(self):
        """Test that size with wrong length raises ValueError."""
        with self.assertRaisesRegex(ValueError, "Size must be a list of two positive integers"):
            color_clip([100], [0,0,0])

        with self.assertRaisesRegex(ValueError, "Size must be a list of two positive integers"):
            color_clip([100, 100, 100], [0,0,0])

    def test_color_clip_invalid_size_negative(self):
        """Test that non-positive dimensions raise ValueError."""
        with self.assertRaisesRegex(ValueError, "Size must be a list of two positive integers"):
            color_clip([-100, 100], [0,0,0])

        with self.assertRaisesRegex(ValueError, "Size must be a list of two positive integers"):
            color_clip([100, 0], [0,0,0])
if __name__ == '__main__':
    unittest.main()
