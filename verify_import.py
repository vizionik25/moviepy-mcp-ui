import sys
from unittest.mock import MagicMock

# Mock moviepy
sys.modules['moviepy'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()

# Mock Effect specifically so it can be used as a base class
class MockEffect:
    def __init__(self, *args, **kwargs): pass
    def apply(self, clip): pass

sys.modules['moviepy'].Effect = MockEffect

# Now try to import CloneGrid
try:
    # Adjust path so we can import from src
    import os
    sys.path.insert(0, os.path.abspath('src'))

    from custom_fx.clone_grid import CloneGrid
    print("Successfully imported CloneGrid")

    # Try to instantiate and check logic
    grid = CloneGrid(4)
    print(f"Grid for 4: {grid.rows}x{grid.cols}")

except Exception as e:
    print(f"Failed to import or run: {e}")
    import traceback
    traceback.print_exc()
