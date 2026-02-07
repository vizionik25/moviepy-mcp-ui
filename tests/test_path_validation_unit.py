import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# --- 1. Mock External Dependencies ---
# These must be mocked BEFORE importing src.server to avoid ImportErrors
# and prevent side effects (like mcp.tool registration).

# Mock fastmcp
mock_fastmcp = MagicMock()
mock_mcp_instance = MagicMock()
# Decorators should simply return the decorated function
mock_mcp_instance.tool.side_effect = lambda func: func
mock_mcp_instance.prompt.side_effect = lambda func: func
mock_fastmcp.FastMCP.return_value = mock_mcp_instance
sys.modules['fastmcp'] = mock_fastmcp

# Mock other heavy dependencies
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

# --- 2. Import Target Functions ---
# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.server import validate_path, validate_write_path
except ImportError as e:
    print(f"Failed to import server: {e}")
    sys.exit(1)

class TestPathValidationUnit(unittest.TestCase):
    def setUp(self):
        # Common mock objects we expect to interact with
        self.mock_cwd = MagicMock()
        self.mock_tmp = MagicMock()
        self.mock_output = MagicMock()

    @patch('src.server.Path')
    def test_validate_path_valid_cwd(self, MockPath):
        """Test validate_path with a file inside CWD."""
        # Arrange
        filename = "safe_file.txt"

        # Mocks for resolved paths
        mock_resolved_file = MagicMock()
        mock_resolved_cwd = MagicMock()
        mock_resolved_tmp = MagicMock()

        # MockPath behavior for:
        # 1. Path(filename).resolve()
        # 2. Path.cwd().resolve()
        # 3. Path("/tmp").resolve()

        # We use side_effect on the constructor to return different mocks based on input
        def path_constructor_side_effect(arg=None):
            m = MagicMock()
            if arg == filename:
                m.resolve.return_value = mock_resolved_file
            elif arg == "/tmp":
                m.exists.return_value = True
                m.resolve.return_value = mock_resolved_tmp
            return m

        MockPath.side_effect = path_constructor_side_effect

        # Mock class methods (Path.cwd())
        mock_cwd_obj = MagicMock()
        mock_cwd_obj.resolve.return_value = mock_resolved_cwd
        MockPath.cwd.return_value = mock_cwd_obj

        # Logic: is_relative_to(cwd) -> True
        mock_resolved_file.is_relative_to.side_effect = lambda other: other == mock_resolved_cwd

        # Act
        result = validate_path(filename)

        # Assert
        self.assertEqual(result, str(mock_resolved_file))
        mock_resolved_file.is_relative_to.assert_any_call(mock_resolved_cwd)

    @patch('src.server.Path')
    def test_validate_path_valid_tmp(self, MockPath):
        """Test validate_path with a file inside /tmp."""
        # Arrange
        filename = "/tmp/safe_file.txt"

        mock_resolved_file = MagicMock()
        mock_resolved_cwd = MagicMock()
        mock_resolved_tmp = MagicMock()

        def path_constructor_side_effect(arg=None):
            m = MagicMock()
            if arg == filename:
                m.resolve.return_value = mock_resolved_file
            elif arg == "/tmp":
                m.exists.return_value = True
                m.resolve.return_value = mock_resolved_tmp
            return m

        MockPath.side_effect = path_constructor_side_effect

        mock_cwd_obj = MagicMock()
        mock_cwd_obj.resolve.return_value = mock_resolved_cwd
        MockPath.cwd.return_value = mock_cwd_obj

        # Logic: is_relative_to(cwd) -> False, is_relative_to(tmp) -> True
        def is_relative_to_side_effect(other):
            if other == mock_resolved_cwd: return False
            if other == mock_resolved_tmp: return True
            return False
        mock_resolved_file.is_relative_to.side_effect = is_relative_to_side_effect

        # Act
        result = validate_path(filename)

        # Assert
        self.assertEqual(result, str(mock_resolved_file))

    @patch('src.server.Path')
    def test_validate_path_traversal(self, MockPath):
        """Test validate_path with a path traversing outside allowed dirs."""
        # Arrange
        filename = "../etc/passwd"

        mock_resolved_file = MagicMock()
        mock_resolved_cwd = MagicMock()
        mock_resolved_tmp = MagicMock()

        def path_constructor_side_effect(arg=None):
            m = MagicMock()
            if arg == filename:
                m.resolve.return_value = mock_resolved_file
            elif arg == "/tmp":
                m.exists.return_value = True
                m.resolve.return_value = mock_resolved_tmp
            return m

        MockPath.side_effect = path_constructor_side_effect

        mock_cwd_obj = MagicMock()
        mock_cwd_obj.resolve.return_value = mock_resolved_cwd
        MockPath.cwd.return_value = mock_cwd_obj

        # Logic: returns False for both
        mock_resolved_file.is_relative_to.return_value = False

        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            validate_path(filename)
        self.assertIn("Access to path", str(cm.exception))

    @patch('src.server.Path')
    def test_validate_path_resolve_error(self, MockPath):
        """Test validate_path when resolve() raises OSError."""
        # Arrange
        filename = "some_file"

        mock_path_obj = MagicMock()
        mock_path_obj.resolve.side_effect = OSError("Permission denied")

        MockPath.return_value = mock_path_obj # Assuming first call is Path(filename)

        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            validate_path(filename)
        self.assertIn("Invalid path", str(cm.exception))

    @patch('src.server.OUTPUT_DIR')
    @patch('src.server.Path')
    def test_validate_write_path_valid_output(self, MockPath, MockOutputDir):
        """Test validate_write_path with a file inside output directory."""
        # Arrange
        filename = "output/video.mp4"

        mock_resolved_file = MagicMock()
        mock_resolved_tmp = MagicMock()
        mock_resolved_output = MagicMock() # The resolved output dir

        # Configure OUTPUT_DIR mock
        MockOutputDir.resolve.return_value = mock_resolved_output

        def path_constructor_side_effect(arg=None):
            m = MagicMock()
            if arg == filename:
                m.resolve.return_value = mock_resolved_file
            elif arg == "/tmp":
                m.exists.return_value = True
                m.resolve.return_value = mock_resolved_tmp
            return m
        MockPath.side_effect = path_constructor_side_effect

        # Logic: is_relative_to(output) -> True
        def is_relative_to_side_effect(other):
            if other == mock_resolved_output: return True
            return False
        mock_resolved_file.is_relative_to.side_effect = is_relative_to_side_effect

        # Act
        result = validate_write_path(filename)

        # Assert
        self.assertEqual(result, str(mock_resolved_file))

    @patch('src.server.OUTPUT_DIR')
    @patch('src.server.Path')
    def test_validate_write_path_invalid_location(self, MockPath, MockOutputDir):
        """Test validate_write_path attempting to write to CWD (not output/)."""
        # Arrange
        filename = "rogue_file.txt"

        mock_resolved_file = MagicMock()
        mock_resolved_tmp = MagicMock()
        mock_resolved_output = MagicMock()

        MockOutputDir.resolve.return_value = mock_resolved_output

        def path_constructor_side_effect(arg=None):
            m = MagicMock()
            if arg == filename:
                m.resolve.return_value = mock_resolved_file
            elif arg == "/tmp":
                m.exists.return_value = True
                m.resolve.return_value = mock_resolved_tmp
            return m
        MockPath.side_effect = path_constructor_side_effect

        # Logic: returns False for output and tmp
        mock_resolved_file.is_relative_to.return_value = False

        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            validate_write_path(filename)
        self.assertIn("Write access to path", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
