import unittest
import sys
import os
import numpy as np
from unittest.mock import MagicMock

# Mock moviepy before importing anything that uses it
mock_moviepy = MagicMock()
# Ensure Effect is a type so it can be inherited
class MockEffect:
    def __init__(self, *args, **kwargs):
        pass
    def apply(self, clip):
        return clip

mock_moviepy.Effect = MockEffect
sys.modules["moviepy"] = mock_moviepy

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from custom_fx.quad_mirror import QuadMirror

class TestQuadMirror(unittest.TestCase):
    def setUp(self):
        # Create a simple 5x5 frame for testing
        # Using a grid where value = y * 10 + x for easy identification
        self.h, self.w = 5, 5
        self.frame = np.arange(self.h * self.w).reshape(self.h, self.w)
        # 0  1  2  3  4
        # 5  6  7  8  9
        # 10 11 12 13 14
        # 15 16 17 18 19
        # 20 21 22 23 24

        self.clip = MagicMock()
        # Mock get_frame to return our test frame
        self.clip.get_frame.return_value = self.frame

        # Mock transform to capture the process_frame function
        def mock_transform(func):
            # This simulates what clip.transform(func) does - it returns a new clip
            # We want to inspect the func, so we store it
            self.process_frame_func = func
            return self.clip

        self.clip.transform.side_effect = mock_transform

    def test_quad_mirror_logic(self):
        """Test mirroring logic with a specific center."""
        # Center at (1, 1)
        # Expected behavior:
        # X mapping around 1:
        # 0 -> 0 (<=1)
        # 1 -> 1 (<=1)
        # 2 -> 2*1 - 2 = 0
        # 3 -> 2*1 - 3 = -1 -> clipped to 0
        # 4 -> 2*1 - 4 = -2 -> clipped to 0
        # Indices X: [0, 1, 0, 0, 0]

        # Y mapping around 1:
        # Same logic -> Indices Y: [0, 1, 0, 0, 0]

        effect = QuadMirror(x=1, y=1)
        effect.apply(self.clip)

        # Retrieve the captured function
        process_frame = self.process_frame_func

        # Call it with get_frame mock and t=0
        # The inner function signature is process_frame(get_frame, t)
        result = process_frame(self.clip.get_frame, 0)

        expected_indices_x = [0, 1, 0, 0, 0]
        expected_indices_y = [0, 1, 0, 0, 0]

        # Construct expected result manually
        expected = self.frame[expected_indices_y][:, expected_indices_x]

        np.testing.assert_array_equal(result, expected)

    def test_quad_mirror_default(self):
        """Test default center (should be center of frame)."""
        # Center of 5x5 is (2, 2)
        effect = QuadMirror(x=None, y=None)
        effect.apply(self.clip)

        process_frame = self.process_frame_func
        result = process_frame(self.clip.get_frame, 0)

        # Center = 2
        # X map:
        # 0 -> 0
        # 1 -> 1
        # 2 -> 2
        # 3 -> 4 - 3 = 1
        # 4 -> 4 - 4 = 0
        # Indices: [0, 1, 2, 1, 0]

        expected_indices = [0, 1, 2, 1, 0]
        expected = self.frame[expected_indices][:, expected_indices]

        np.testing.assert_array_equal(result, expected)

    def test_quad_mirror_bounds(self):
        """Test center out of bounds (should be clamped)."""
        # Set center way out of bounds (e.g. 100, 100)
        # Should clamp to (4, 4) for 5x5 frame
        effect = QuadMirror(x=100, y=100)
        effect.apply(self.clip)

        process_frame = self.process_frame_func
        result = process_frame(self.clip.get_frame, 0)

        # Center = 4
        # X map:
        # 0..4 all <= 4 -> Identity
        # Indices: [0, 1, 2, 3, 4]

        # It should be identical to original frame
        np.testing.assert_array_equal(result, self.frame)

        # Test negative bounds
        # Set center to (-10, -10) -> Clamped to (0, 0)
        effect = QuadMirror(x=-10, y=-10)
        effect.apply(self.clip)

        process_frame = self.process_frame_func
        result = process_frame(self.clip.get_frame, 0)

        # Center = 0
        # X map:
        # 0 -> 0
        # 1 -> 0 - 1 = -1 -> 0
        # ... all map to 0
        # Indices: [0, 0, 0, 0, 0]

        expected_indices = [0, 0, 0, 0, 0]
        expected = self.frame[expected_indices][:, expected_indices]

        np.testing.assert_array_equal(result, expected)

if __name__ == "__main__":
    unittest.main()
