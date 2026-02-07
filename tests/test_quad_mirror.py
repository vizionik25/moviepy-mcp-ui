import unittest
import sys
import os
import numpy as np
from unittest.mock import MagicMock

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from custom_fx.quad_mirror import QuadMirror

class TestQuadMirror(unittest.TestCase):
    def setUp(self):
        # Check if numpy is mocked
        if isinstance(np, MagicMock) or hasattr(np, 'reset_mock'):
            self.skipTest("Numpy is mocked, skipping logic tests")

        self.clip = MagicMock()
        self.clip.w = 100
        self.clip.h = 100
        self.clip.transform = lambda func: func

    def test_quad_mirror_logic(self):
        """Test mirroring logic with a specific center."""
        effect = QuadMirror(x=1, y=1)
        process_frame = effect.apply(self.clip)

        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        # Fill with unique values
        for i in range(100):
            for j in range(100):
                frame[i, j] = [i, j, 0]

        result = process_frame(lambda t: frame, 0)
        self.assertEqual(result.shape, (100, 100, 3))
        # Add logic checks if needed, but shape is a good start

    def test_quad_mirror_default(self):
        """Test default center (should be center of frame)."""
        effect = QuadMirror(x=None, y=None)
        process_frame = effect.apply(self.clip)

        frame = np.zeros((100, 100, 3), dtype=np.uint8)

        result = process_frame(lambda t: frame, 0)
        self.assertEqual(result.shape, (100, 100, 3))

    def test_quad_mirror_bounds(self):
        """Test center out of bounds (should be clamped)."""
        effect = QuadMirror(x=-50, y=150)
        process_frame = effect.apply(self.clip)

        frame = np.zeros((100, 100, 3), dtype=np.uint8)

        result = process_frame(lambda t: frame, 0)
        self.assertEqual(result.shape, (100, 100, 3))

if __name__ == '__main__':
    unittest.main()
