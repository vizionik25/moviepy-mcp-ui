import unittest
import os
import sys
import ast
from unittest.mock import MagicMock, patch

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# --- MOCKING DEPENDENCIES START ---
fastmcp_mock = MagicMock()
mock_mcp_instance = MagicMock()

def identity_decorator(func):
    return func

mock_mcp_instance.tool.side_effect = identity_decorator
mock_mcp_instance.prompt.side_effect = identity_decorator
fastmcp_mock.FastMCP.return_value = mock_mcp_instance

# Setup sys.modules
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

# Import server
import server
from server import validate_math_expression, vfx_head_blur, CLIPS, register_clip

# Patch 'vfx' in server module since 'from moviepy import *' didn't provide it in the mock env
server.vfx = MagicMock()

# --- MOCKING DEPENDENCIES END ---

class TestValidateMathExpression(unittest.TestCase):
    """
    Tests for the validate_math_expression function.
    """

    def test_valid_arithmetic(self):
        """Test simple arithmetic expressions."""
        valid_expressions = [
            "1 + 1",
            "10 * t",
            "t / 2",
            "100 - 50",
            "t ** 2",
            "(t + 1) * 2",
            "-t",
            "+t"
        ]
        for expr in valid_expressions:
            with self.subTest(expr=expr):
                try:
                    validate_math_expression(expr)
                except ValueError as e:
                    self.fail(f"Valid expression '{expr}' raised ValueError: {e}")

    def test_valid_functions(self):
        """Test allowed function calls."""
        valid_expressions = [
            "sin(t)",
            "cos(t * 2)",
            "abs(t - 100)",
            "min(t, 100)",
            "max(t, 0)",
            "sqrt(t)",
            "exp(t)",
            "log(t + 1)"
        ]
        for expr in valid_expressions:
            with self.subTest(expr=expr):
                try:
                    validate_math_expression(expr)
                except ValueError as e:
                    self.fail(f"Valid expression '{expr}' raised ValueError: {e}")

    def test_valid_constants(self):
        """Test allowed constants."""
        valid_expressions = [
            "pi * t",
            "e ** t"
        ]
        for expr in valid_expressions:
            with self.subTest(expr=expr):
                try:
                    validate_math_expression(expr)
                except ValueError as e:
                    self.fail(f"Valid expression '{expr}' raised ValueError: {e}")

    def test_invalid_syntax(self):
        """Test expressions with invalid syntax."""
        invalid_expressions = [
            "1 +",
            "sin(t",
            "((t + 1)",
            "t * *"
        ]
        for expr in invalid_expressions:
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError) as cm:
                    validate_math_expression(expr)
                self.assertIn("Invalid syntax", str(cm.exception))

    def test_disallowed_functions(self):
        """Test calls to disallowed functions."""
        disallowed = [
            "eval('1+1')",
            "exec('print(1)')",
            "open('/etc/passwd')",
            "print('hello')",
            "__import__('os')",
            "globals()",
            "locals()"
        ]
        for expr in disallowed:
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError) as cm:
                    validate_math_expression(expr)
                self.assertIn("Security check failed", str(cm.exception))

    def test_disallowed_variables(self):
        """Test usage of disallowed variables."""
        disallowed = [
            "__builtins__",
            "os",
            "sys",
            "x",
            "y"
        ]
        for expr in disallowed:
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError) as cm:
                    validate_math_expression(expr)
                self.assertIn("Security check failed", str(cm.exception))

    def test_disallowed_ast_nodes_syntax(self):
        """Test usage of disallowed language constructs that are statements."""
        disallowed = [
            "t = 1", # Assignment
            "import os",
            "class A: pass"
        ]
        for expr in disallowed:
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError) as cm:
                    validate_math_expression(expr)
                # These raise SyntaxError in ast.parse mode='eval' which is caught and re-raised as ValueError("Invalid syntax: ...")
                self.assertIn("Invalid syntax", str(cm.exception))

    def test_disallowed_ast_nodes_expression(self):
        """Test usage of disallowed language constructs that are expressions."""
        disallowed = [
            "lambda x: x",
            "[x for x in range(10)]", # List comprehension
            "{'a': 1}", # Dict
        ]
        for expr in disallowed:
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError) as cm:
                    validate_math_expression(expr)
                self.assertIn("Security check failed", str(cm.exception))

    def test_custom_allowed_vars(self):
        """Test that we can pass custom allowed variables."""
        validate_math_expression("x + y", allowed_vars={"x", "y"})

        with self.assertRaises(ValueError):
            validate_math_expression("z", allowed_vars={"x", "y"})


class TestVfxHeadBlur(unittest.TestCase):
    """
    Tests for vfx_head_blur to ensure it correctly uses validation
    and handles errors.
    """

    def setUp(self):
        self.clip_id = "test_clip_id"
        self.mock_clip = MagicMock()

        self.get_clip_patcher = patch('server.get_clip', return_value=self.mock_clip)
        self.register_clip_patcher = patch('server.register_clip', return_value="new_clip_id")

        self.mock_get_clip = self.get_clip_patcher.start()
        self.mock_register_clip = self.register_clip_patcher.start()

        self.numexpr_patcher = patch('server.numexpr')
        self.mock_numexpr = self.numexpr_patcher.start()

    def tearDown(self):
        self.get_clip_patcher.stop()
        self.register_clip_patcher.stop()
        self.numexpr_patcher.stop()

    def test_valid_input(self):
        """Test vfx_head_blur with valid math expressions."""
        self.mock_numexpr.evaluate.return_value = 10.0

        result = vfx_head_blur(self.clip_id, "100 + t", "50 * t", 10.0)

        self.assertEqual(result, "new_clip_id")
        self.mock_clip.with_effects.assert_called_once()
        self.mock_numexpr.evaluate.assert_any_call("100 + t", local_dict={"t": 0})
        self.mock_numexpr.evaluate.assert_any_call("50 * t", local_dict={"t": 0})

    def test_invalid_syntax_fx(self):
        """Test vfx_head_blur with invalid syntax in fx_code."""
        with self.assertRaises(ValueError) as cm:
            vfx_head_blur(self.clip_id, "100 +", "50 * t", 10.0)
        self.assertIn("Invalid syntax", str(cm.exception))

    def test_disallowed_function(self):
        """Test vfx_head_blur with disallowed function call."""
        with self.assertRaises(ValueError) as cm:
            vfx_head_blur(self.clip_id, "eval('1')", "50 * t", 10.0)
        self.assertIn("Security check failed", str(cm.exception))

    def test_numexpr_evaluation_error(self):
        """Test handling of runtime errors from numexpr during initial check."""
        self.mock_numexpr.evaluate.side_effect = Exception("Runtime error")

        with self.assertRaises(ValueError) as cm:
            vfx_head_blur(self.clip_id, "1 / 0", "50 * t", 10.0)
        self.assertIn("Invalid math expression", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
