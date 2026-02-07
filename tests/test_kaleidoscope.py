import unittest
import sys
import os
import numpy as np
from unittest.mock import MagicMock

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.custom_fx.kaleidoscope import Kaleidoscope

class TestKaleidoscope(unittest.TestCase):
    def setUp(self):
        # Create a mock clip with standard dimensions
        self.mock_clip = MagicMock()
        self.mock_clip.w = 100
        self.mock_clip.h = 100
        # Mock transform to simply return the function being applied
        self.mock_clip.transform = lambda func: func

    def test_valid_input(self):
        """Test Kaleidoscope with valid n_slices."""
        effect = Kaleidoscope(n_slices=6)
        process_frame = effect.apply(self.mock_clip)

        # Create a dummy frame (100x100 RGB)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        # Fill with some pattern to verify transformation if needed,
        # but here we just check it runs.
        frame[:] = [10, 20, 30]

        def get_frame(t):
            return frame

        # Run process_frame
        result = process_frame(get_frame, 0)

        # Verify result shape and type
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (100, 100, 3))

    def test_zero_slices(self):
        """
        Test Kaleidoscope with n_slices=0.
        Currently raises ZeroDivisionError due to division by zero in apply logic.
        This test documents current behavior. Ideally, this should raise ValueError on init.
        """
        effect = Kaleidoscope(n_slices=0)
        process_frame = effect.apply(self.mock_clip)

        def get_frame(t):
            return np.zeros((100, 100, 3), dtype=np.uint8)

        # Assert correct error is raised
        with self.assertRaises(ZeroDivisionError):
            process_frame(get_frame, 0)

    def test_invalid_type(self):
        """
        Test Kaleidoscope with invalid type for n_slices.
        Currently raises TypeError during math operations.
        This test documents current behavior.
        """
        effect = Kaleidoscope(n_slices="invalid")
        process_frame = effect.apply(self.mock_clip)

        def get_frame(t):
            return np.zeros((100, 100, 3), dtype=np.uint8)

        with self.assertRaises(TypeError):
            process_frame(get_frame, 0)

if __name__ == '__main__':
    unittest.main()
