import sys
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import io
import os
import logging

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Extensive Mocking Setup ---

# Mock 'fastmcp'
sys.modules['fastmcp'] = MagicMock()

# Mock 'moviepy'
mock_moviepy = MagicMock()
mock_moviepy.__all__ = []
sys.modules['moviepy'] = mock_moviepy

# Mock 'custom_fx'
mock_custom_fx = MagicMock()
mock_custom_fx.__all__ = []
sys.modules['custom_fx'] = mock_custom_fx
sys.modules['src.custom_fx'] = mock_custom_fx

# Mock 'mcp_ui.core'
sys.modules['mcp_ui'] = MagicMock()
sys.modules['mcp_ui.core'] = MagicMock()

# Mock 'fastapi' and its components
mock_fastapi_module = MagicMock()
sys.modules['fastapi'] = mock_fastapi_module
sys.modules['fastapi.middleware'] = MagicMock()
sys.modules['fastapi.middleware.cors'] = MagicMock()

# Mock FastAPI class instance to handle decorators
mock_app = MagicMock()
def decorator_side_effect(*args, **kwargs):
    def wrapper(func):
        return func
    return wrapper

mock_app.get.side_effect = decorator_side_effect
mock_app.post.side_effect = decorator_side_effect
mock_fastapi_module.FastAPI.return_value = mock_app

# Mock 'pydantic'
sys.modules['pydantic'] = MagicMock()

# Mock 'litellm'
sys.modules['litellm'] = MagicMock()

# --- End Mocking Setup ---

# Mock 'server' module
mock_server = MagicMock()
mock_mcp = MagicMock()
mock_server.mcp = mock_mcp
sys.modules['server'] = mock_server
sys.modules['src.server'] = mock_server

from src import api

class TestApiLogging(unittest.IsolatedAsyncioTestCase):
    async def test_get_clips_logging(self):
        # Setup the mock to raise an exception
        mock_tool_manager = MagicMock()
        mock_tool_manager.call_tool = AsyncMock(side_effect=Exception("Test Exception For Logging"))

        # Configure api.mcp
        api.mcp._tool_manager = mock_tool_manager

        # Patch the logger used in api module
        # Since logger is defined at module level, we can patch it directly
        with patch.object(api, 'logger') as mock_logger:

            captured_output = io.StringIO()
            original_stdout = sys.stdout
            sys.stdout = captured_output

            try:
                # Call the function
                await api.get_clips()
            finally:
                sys.stdout = original_stdout

            output = captured_output.getvalue()

            # Verify print was NOT called (stdout should be empty or not contain the error string)
            self.assertNotIn("Test Exception For Logging", output)

            # Verify logger.error WAS called
            mock_logger.error.assert_called_once()
            args, kwargs = mock_logger.error.call_args
            self.assertEqual(args[0], "Failed to list clips")
            self.assertTrue(kwargs.get('exc_info'))

if __name__ == '__main__':
    unittest.main()
