import unittest
import os
import tempfile
import sys
from unittest.mock import MagicMock
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
sys.modules['custom_fx'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['numexpr'] = MagicMock()
sys.modules['pydantic'] = MagicMock()

from server import validate_path, validate_write_path, OUTPUT_DIR, delete_clip, CLIPS, register_clip

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


class TestClipManagement(unittest.TestCase):
    def setUp(self):
        # Clear CLIPS before each test
        CLIPS.clear()

    def test_delete_existing_clip(self):
        """Test deleting an existing clip."""
        mock_clip = MagicMock()
        clip_id = "test_clip_1"
        CLIPS[clip_id] = mock_clip

        result = delete_clip(clip_id)

        self.assertEqual(result, f"Clip {clip_id} deleted.")
        self.assertNotIn(clip_id, CLIPS)
        mock_clip.close.assert_called_once()

    def test_delete_non_existent_clip(self):
        """Test deleting a clip that does not exist."""
        clip_id = "non_existent_clip"

        result = delete_clip(clip_id)

        self.assertEqual(result, f"Clip {clip_id} not found.")
        self.assertNotIn(clip_id, CLIPS)

    def test_delete_clip_error_on_close(self):
        """Test deleting a clip where close() raises an exception."""
        mock_clip = MagicMock()
        mock_clip.close.side_effect = Exception("Close error")
        clip_id = "error_clip"
        CLIPS[clip_id] = mock_clip

        result = delete_clip(clip_id)

        # It should still be deleted and return success message
        self.assertEqual(result, f"Clip {clip_id} deleted.")
        self.assertNotIn(clip_id, CLIPS)
        mock_clip.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
