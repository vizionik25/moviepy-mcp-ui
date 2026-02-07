import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock dependencies BEFORE import
mock_numpy = MagicMock()
mock_cv2 = MagicMock()
mock_moviepy = MagicMock()
mock_pil = MagicMock()
mock_fastmcp = MagicMock()

# Mock numpy functionality used in RotatingCube
def mock_array(*args, **kwargs):
    m = MagicMock()
    m.shape = (100, 100, 3)
    # Support indexing
    m.__getitem__.return_value = m
    # Support mathematical operations
    m.__matmul__.return_value = m
    m.__sub__.return_value = m
    m.__add__.return_value = m
    m.__mul__.return_value = m
    m.__truediv__.return_value = m
    m.__lt__.return_value = False
    m.__le__.return_value = False
    m.__gt__.return_value = False
    m.__ge__.return_value = False

    # Support iteration (for loop over rot_pts)
    # rot_pts is N x 3. Iterating it yields rows.
    # Each row is unpacked into x, y, z.
    row_mock = MagicMock()
    # Use side_effect with lambda to return a FRESH iterator each time row_mock is iterated
    row_mock.__iter__.side_effect = lambda: iter([0.0, 0.0, 100.0])

    # Iterating the array yields rows.
    # We yield the SAME row_mock multiple times, so it must be restartable.
    m.__iter__.side_effect = lambda: iter([row_mock, row_mock, row_mock, row_mock])

    return m

mock_numpy.array.side_effect = mock_array
mock_numpy.zeros_like.return_value = mock_array()
mock_numpy.arange.return_value = mock_array()
mock_numpy.where.return_value = mock_array()
mock_numpy.clip.return_value = mock_array()
mock_numpy.deg2rad.return_value = 0.0
mock_numpy.cos.return_value = 1.0
mock_numpy.sin.return_value = 0.0
mock_numpy.mean.return_value = 100.0
mock_numpy.cross.return_value = MagicMock()
mock_numpy.cross.return_value.__getitem__.return_value = 1.0
mock_numpy.float32 = float
mock_numpy.any.return_value = mock_array()

mock_cv2.getPerspectiveTransform.return_value = MagicMock()
mock_cv2.warpPerspective.return_value = mock_array()

class MockEffect:
    def __init__(self, *args, **kwargs):
        pass
    def apply(self, clip):
        return clip

mock_moviepy.Effect = MockEffect

# Inject mocks
sys.modules["numpy"] = mock_numpy
sys.modules["cv2"] = mock_cv2
sys.modules["moviepy"] = mock_moviepy
sys.modules["PIL"] = mock_pil
sys.modules["PIL.Image"] = mock_pil
sys.modules["PIL.ImageDraw"] = mock_pil
sys.modules["PIL.ImageFont"] = mock_pil
sys.modules["fastmcp"] = mock_fastmcp

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from custom_fx.rotating_cube import RotatingCube

class TestRotatingCube(unittest.TestCase):
    def setUp(self):
        self.clip = MagicMock()
        self.clip.w = 100
        self.clip.h = 100

        # Mock get_frame to return a mock array
        self.mock_frame = mock_array()
        self.mock_frame.shape = (100, 100, 3)
        self.clip.get_frame.return_value = self.mock_frame

        # Mock transform
        def mock_transform(func):
            self.process_frame_func = func
            return self.clip
        self.clip.transform.side_effect = mock_transform

    def test_apply_returns_process_frame(self):
        effect = RotatingCube()
        effect.apply(self.clip)

        self.assertTrue(hasattr(self, 'process_frame_func'))
        self.assertEqual(self.process_frame_func.__name__, 'process_frame')

    def test_process_frame_execution(self):
        effect = RotatingCube()
        effect.apply(self.clip)

        process_frame = self.process_frame_func
        try:
            result = process_frame(self.clip.get_frame, 0)
        except Exception as e:
            self.fail(f"process_frame raised exception: {e}")

        self.assertIsInstance(result, MagicMock)

if __name__ == "__main__":
    unittest.main()
