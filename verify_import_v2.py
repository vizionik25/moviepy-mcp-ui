import sys
import os
from unittest.mock import MagicMock

# 1. Mock external dependencies
sys.modules['moviepy'] = MagicMock()
sys.modules['moviepy.video'] = MagicMock()
sys.modules['moviepy.video.fx'] = MagicMock()

# Specifically mock Effect so it can be subclassed
class MockEffect:
    def __init__(self, *args, **kwargs): pass
    def transform(self, func): return func

# We need to ensure that when 'from moviepy import Effect' runs, it gets MockEffect
# The original code does: 'from moviepy import Effect'
# If moviepy is a MagicMock, accessing .Effect returns another MagicMock.
# We want it to be our class or at least a type we can inherit from.
sys.modules['moviepy'].Effect = MockEffect

sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageDraw'] = MagicMock()
sys.modules['PIL.ImageFont'] = MagicMock()
sys.modules['numexpr'] = MagicMock()


# 2. Add src to sys.path
sys.path.insert(0, os.path.abspath('src'))

# 3. Import and test logic
try:
    # We can import the module directly to avoid __init__.py issues if we want,
    # but let's try to be robust and just mock everything.
    from custom_fx.clone_grid import CloneGrid

    print("Successfully imported CloneGrid")

    # Test cases
    cases = [
        (2, (1, 2)),      # 2^1 -> rows=1, cols=2 ? Or rows=2, cols=1? Logic: k=1. rows=2^(0)=1. cols=2^(1)=2. Correct.
        (4, (2, 2)),      # 2^2 -> k=2. rows=2^1=2. cols=2^1=2.
        (8, (2, 4)),      # 2^3 -> k=3. rows=2^1=2. cols=2^2=4.
        (16, (4, 4)),     # 2^4 -> k=4. rows=2^2=4. cols=2^2=4.
        (32, (4, 8)),     # 2^5 -> k=5. rows=2^2=4. cols=2^3=8.
        (64, (8, 8)),     # 2^6 -> k=6. rows=2^3=8. cols=2^3=8.
        (3, (2, 2)),      # sqrt(3)=1.73 -> cols=2. rows=ceil(3/2)=2. 2x2 grid for 3 items.
        (5, (2, 3)),      # sqrt(5)=2.23 -> cols=3. rows=ceil(5/3)=2.
    ]

    for n, expected in cases:
        g = CloneGrid(n)
        actual = (g.rows, g.cols)
        print(f"n={n}: Expected {expected}, Got {actual}")
        assert actual == expected, f"Failed for n={n}"

    print("All verification tests passed!")

except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
