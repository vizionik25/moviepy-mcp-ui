import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies to avoid side effects during import
sys.modules["fastmcp"] = MagicMock()
sys.modules["moviepy"] = MagicMock()
sys.modules["litellm"] = MagicMock()
sys.modules["moviepy.video.tools.drawing"] = MagicMock()
sys.modules["moviepy.video.tools.cuts"] = MagicMock()
sys.modules["moviepy.video.io.ffmpeg_tools"] = MagicMock()
sys.modules["moviepy.video.tools.subtitles"] = MagicMock()
sys.modules["moviepy.video.tools.credits"] = MagicMock()
sys.modules["moviepy.audio.tools.cuts"] = MagicMock()
sys.modules["moviepy.config"] = MagicMock()
sys.modules["mcp_ui.core"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["numexpr"] = MagicMock()
sys.modules["custom_fx"] = MagicMock()

# Now import the app
from src.api import app

class TestAPISecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_cors_policy(self):
        """Test that CORS is restricted."""
        # Current behavior: * allows any origin.
        # We want to verify it, and then after fix, verify it's restricted.

        # Test with an arbitrary origin
        response = self.client.options(
            "/api/chat",
            headers={"Origin": "http://evil.com", "Access-Control-Request-Method": "POST"}
        )

        # Should NOT allow evil.com
        allow_origin = response.headers.get("access-control-allow-origin")
        print(f"Origin: http://evil.com -> Access-Control-Allow-Origin: {allow_origin}")
        self.assertIsNone(allow_origin)

        # Test with localhost:3000
        response_safe = self.client.options(
            "/api/chat",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"}
        )
        allow_origin_safe = response_safe.headers.get("access-control-allow-origin")
        print(f"Origin: http://localhost:3000 -> Access-Control-Allow-Origin: {allow_origin_safe}")
        self.assertEqual(allow_origin_safe, "http://localhost:3000")

    @patch("src.api.litellm.acompletion")
    def test_error_handling(self, mock_acompletion):
        """Test that internal errors are masked."""
        # Mock litellm to raise an exception
        mock_acompletion.side_effect = Exception("Secret database info leaked in stack trace")

        payload = {
            "messages": [{"role": "user", "content": "hello"}],
            "api_keys": {"openai": "sk-test"}
        }

        response = self.client.post("/api/chat", json=payload)

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")

        # Desired behavior: detail should be generic "Internal Server Error"
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "Internal Server Error"})

if __name__ == '__main__':
    unittest.main()
