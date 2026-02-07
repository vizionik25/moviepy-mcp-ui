import unittest
import sys
import os
from unittest.mock import MagicMock

# 1. Mock external dependencies BEFORE importing the module under test
# Mock moviepy and its submodules
sys.modules['moviepy'] = MagicMock()
sys.modules['moviepy.video'] = MagicMock()
sys.modules['moviepy.video.fx'] = MagicMock()

# Specifically mock Effect so it can be subclassed by CloneGrid
class MockEffect:
    def __init__(self, *args, **kwargs): pass
    def transform(self, func): return func

sys.modules['moviepy'].Effect = MockEffect

# Mock other dependencies
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageDraw'] = MagicMock()
sys.modules['PIL.ImageFont'] = MagicMock()
sys.modules['numexpr'] = MagicMock()

# 2. Add src to sys.path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# 3. Import the module under test
from custom_fx.clone_grid import CloneGrid

class TestCloneGrid(unittest.TestCase):

    def test_powers_of_two(self):
        """Test grid calculation for standard powers of 2."""
        cases = [
            (2, (1, 2)),      # 2^1 -> rows=1, cols=2 (k=1, rows=2^0, cols=2^1)
            (4, (2, 2)),      # 2^2 -> rows=2, cols=2 (k=2, rows=2^1, cols=2^1)
            (8, (2, 4)),      # 2^3 -> rows=2, cols=4 (k=3, rows=2^1, cols=2^2)
            (16, (4, 4)),     # 2^4 -> rows=4, cols=4 (k=4, rows=2^2, cols=2^2)
            (32, (4, 8)),     # 2^5 -> rows=4, cols=8 (k=5, rows=2^2, cols=2^3)
            (64, (8, 8)),     # 2^6 -> rows=8, cols=8 (k=6, rows=2^3, cols=2^3)
        ]

        for n, expected in cases:
            with self.subTest(n=n):
                grid = CloneGrid(n)
                self.assertEqual((grid.rows, grid.cols), expected)

    def test_non_powers_of_two(self):
        """Test grid calculation for non-powers of 2 (fallback logic)."""
        # Logic: cols = ceil(sqrt(n)), rows = ceil(n / cols)
        cases = [
            (3, (2, 2)),      # sqrt(3)=1.73 -> cols=2. rows=ceil(3/2)=2.
            (5, (2, 3)),      # sqrt(5)=2.23 -> cols=3. rows=ceil(5/3)=2.
            (6, (2, 3)),      # sqrt(6)=2.45 -> cols=3. rows=ceil(6/3)=2.
            (7, (3, 3)),      # sqrt(7)=2.64 -> cols=3. rows=ceil(7/3)=3.
            (9, (3, 3)),      # sqrt(9)=3.0 -> cols=3. rows=ceil(9/3)=3. (Wait, log2(9)=3.17, not int. Fallback used)
            (10, (3, 4)),     # sqrt(10)=3.16 -> cols=4. rows=ceil(10/4)=3.
        ]

        for n, expected in cases:
            with self.subTest(n=n):
                grid = CloneGrid(n)
                self.assertEqual((grid.rows, grid.cols), expected)

    def test_edge_cases(self):
        """Test edge cases like 1, 0, or negative numbers."""
        # Case n=1: log2(1)=0. k=0. rows=2^0=1, cols=2^0=1. Should be (1, 1).
        grid = CloneGrid(1)
        self.assertEqual((grid.rows, grid.cols), (1, 1))

        # Case n=0: log2(0) raises ValueError.
        with self.assertRaises(ValueError):
            CloneGrid(0)

        # Case n=-1: log2(-1) raises ValueError.
        with self.assertRaises(ValueError):
            CloneGrid(-1)

if __name__ == '__main__':
    unittest.main()
