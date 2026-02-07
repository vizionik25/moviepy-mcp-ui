import unittest
import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Configure sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# --- MOCK DEPENDENCIES ---

mock_pydantic = MagicMock()
class MockBaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def model_dump(self):
        return self.__dict__
mock_pydantic.BaseModel = MockBaseModel
sys.modules['pydantic'] = mock_pydantic

# Mock fastapi
mock_fastapi = MagicMock()
def identity_decorator(*args, **kwargs):
    def wrapper(func):
        return func
    return wrapper

mock_app = MagicMock()
mock_app.post.side_effect = identity_decorator
mock_app.get.side_effect = identity_decorator
mock_app.add_middleware = MagicMock()

mock_fastapi.FastAPI.return_value = mock_app
sys.modules['fastapi'] = mock_fastapi
sys.modules['fastapi.middleware'] = MagicMock()
sys.modules['fastapi.middleware.cors'] = MagicMock()

# Mock litellm
mock_litellm = MagicMock()
mock_litellm.acompletion = AsyncMock()
sys.modules['litellm'] = mock_litellm

# Mock server (and mcp inside it)
mock_server = MagicMock()
mock_mcp = MagicMock()
mock_mcp._tool_manager = MagicMock()
mock_mcp._tool_manager.call_tool = AsyncMock()
mock_mcp._tool_manager._tools = {}
mock_server.mcp = mock_mcp
sys.modules['server'] = mock_server

# Mock transitive deps deeply
def mock_module(name):
    parts = name.split('.')
    for i in range(1, len(parts) + 1):
        mod_name = '.'.join(parts[:i])
        if mod_name not in sys.modules:
            sys.modules[mod_name] = MagicMock()

mock_module('moviepy.video.tools.drawing')
mock_module('moviepy.video.tools.cuts')
mock_module('moviepy.video.io.ffmpeg_tools')
mock_module('moviepy.video.tools.subtitles')
mock_module('moviepy.video.tools.credits')
mock_module('moviepy.editor')
mock_module('mcp_ui.core')
mock_module('custom_fx')
mock_module('numpy')
mock_module('numexpr')
mock_module('fastmcp')

# --- IMPORT MODULE UNDER TEST ---
try:
    import src.api as api
except ImportError:
    import api

class TestApiJsonHealth(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_json_handled(self):
        """
        Verify that invalid JSON (JSONDecodeError) is caught and handled gracefully (defaults to {}).
        """
        request = MagicMock()
        request.messages = []
        request.api_keys = {"openai": "fake-key"}

        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = "{invalid_json"
        mock_tool_call.id = "call_123"

        mock_message.tool_calls = [mock_tool_call]
        mock_response.choices = [MagicMock(message=mock_message)]

        second_response = MagicMock()
        second_response.choices = [MagicMock(message=MagicMock(content="Final answer"))]

        api.litellm.acompletion.side_effect = [mock_response, second_response]
        api.mcp._tool_manager.call_tool.return_value = MagicMock(content=[])

        await api.chat(request)

        api.mcp._tool_manager.call_tool.assert_called_with("test_tool", {})

    async def test_other_exceptions_propagate(self):
        """
        Verify that exceptions other than JSONDecodeError (e.g. TypeError) are propagated.
        This ensures we are not swallowing unexpected errors.
        """
        request = MagicMock()
        request.messages = []
        request.api_keys = {"openai": "fake-key"}

        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = '{"valid": "json"}'
        mock_tool_call.id = "call_123"

        mock_message.tool_calls = [mock_tool_call]
        mock_response.choices = [MagicMock(message=mock_message)]

        # We don't need second response because we expect crash before second call

        api.litellm.acompletion.side_effect = None; api.litellm.acompletion.return_value = mock_response
        api.mcp._tool_manager.call_tool.return_value = MagicMock(content=[])

        # Patch json.loads to raise a TypeError
        with patch('src.api.json.loads', side_effect=TypeError("Not a JSON error")):
            # EXPECTED BEHAVIOR: TypeError is raised
            with self.assertRaisesRegex(TypeError, "Not a JSON error"):
                await api.chat(request)

if __name__ == '__main__':
    unittest.main()
