import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Define a dummy Effect class to avoid inheriting from MagicMock
class DummyEffect:
    def __init__(self):
        pass
    def apply(self, clip):
        pass

# Mock dependencies before importing the module under test
mock_moviepy = MagicMock()
mock_moviepy.Effect = DummyEffect
sys.modules['moviepy'] = mock_moviepy
sys.modules['numpy'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageDraw'] = MagicMock()
sys.modules['PIL.ImageFont'] = MagicMock()
sys.modules['fastmcp'] = MagicMock()
sys.modules['pydantic'] = MagicMock()

# Now we can safely import the class
from custom_fx.auto_framing import AutoFraming

class TestAutoFraming(unittest.TestCase):
    def setUp(self):
        # Reset mocks for each test
        sys.modules['cv2'].reset_mock()
        sys.modules['numpy'].reset_mock()

        # Mock CascadeClassifier specifically
        self.mock_cascade = MagicMock()
        sys.modules['cv2'].CascadeClassifier.return_value = self.mock_cascade

        # Common constants
        self.mock_cv2 = sys.modules['cv2']
        self.mock_cv2.data.haarcascades = '/path/to/haarcascades/'

    def test_init(self):
        """Test initialization of AutoFraming parameters."""
        af = AutoFraming(target_aspect_ratio=1.0, smoothing=0.5)
        self.assertEqual(af.target_aspect_ratio, 1.0)
        self.assertEqual(af.smoothing, 0.5)
        self.assertIsNone(af.focus_func)
        self.mock_cv2.CascadeClassifier.assert_called_with('/path/to/haarcascades/haarcascade_frontalface_default.xml')

    def test_custom_focus_func(self):
        """Test that custom focus function takes precedence."""
        def my_focus(frame, t):
            return (100, 200)

        af = AutoFraming(focus_func=my_focus)

        # Mock frame
        mock_frame = MagicMock()
        mock_frame.shape = (1080, 1920, 3)
        mock_get_frame = MagicMock(return_value=mock_frame)

        # Mock clip
        mock_clip = MagicMock()
        # Ensure transform returns something (though we don't use the return value)
        mock_clip.transform.return_value = MagicMock()

        af.apply(mock_clip)

        # Check if transform was called
        self.assertTrue(mock_clip.transform.called)

        process_frame_func = mock_clip.transform.call_args[0][0]
        process_frame_func(mock_get_frame, 0)

        self.assertEqual(af.current_x, 100)
        self.assertEqual(af.current_y, 200)

    def test_face_detection_largest_face(self):
        """Test selection of the largest face."""
        af = AutoFraming()

        mock_frame = MagicMock()
        mock_frame.shape = (1000, 1000, 3)
        mock_get_frame = MagicMock(return_value=mock_frame)

        mock_clip = MagicMock()
        af.apply(mock_clip)
        process_frame_func = mock_clip.transform.call_args[0][0]

        # Mock faces: [x, y, w, h]
        faces = [
            [10, 10, 10, 10], # Area 100
            [200, 200, 100, 100], # Area 10000
            [500, 500, 50, 50] # Area 2500
        ]
        self.mock_cascade.detectMultiScale.return_value = faces

        process_frame_func(mock_get_frame, 0)

        # Expected center of largest face:
        # x = 200 + 100/2 = 250
        # y = 200 + 100/2 = 250
        self.assertEqual(af.current_x, 250)
        self.assertEqual(af.current_y, 250)

    def test_no_face_fallback(self):
        """Test fallback to center/last position when no face found."""
        af = AutoFraming(smoothing=0) # Disable smoothing

        mock_frame = MagicMock()
        mock_frame.shape = (100, 200, 3) # H=100, W=200
        mock_get_frame = MagicMock(return_value=mock_frame)

        mock_clip = MagicMock()
        af.apply(mock_clip)
        process_frame_func = mock_clip.transform.call_args[0][0]

        # 1. No faces detected -> Center
        self.mock_cascade.detectMultiScale.return_value = []
        process_frame_func(mock_get_frame, 0)

        self.assertEqual(af.current_x, 100) # W/2
        self.assertEqual(af.current_y, 50)  # H/2

        # 2. Face detected -> New position
        # Face at 0,0 size 20,20 -> Center 10,10
        self.mock_cascade.detectMultiScale.return_value = [[0, 0, 20, 20]]
        process_frame_func(mock_get_frame, 1)
        self.assertEqual(af.current_x, 10)
        self.assertEqual(af.current_y, 10)

        # 3. No faces detected again -> Keep last position
        self.mock_cascade.detectMultiScale.return_value = []
        process_frame_func(mock_get_frame, 2)
        self.assertEqual(af.current_x, 10)
        self.assertEqual(af.current_y, 10)

    def test_smoothing(self):
        """Test exponential moving average smoothing."""
        af = AutoFraming(smoothing=0.5)

        mock_frame = MagicMock()
        mock_frame.shape = (100, 100, 3)
        mock_get_frame = MagicMock(return_value=mock_frame)

        mock_clip = MagicMock()
        af.apply(mock_clip)
        process_frame_func = mock_clip.transform.call_args[0][0]

        # Step 1: Target at 100.
        faces = [[90, 90, 20, 20]] # Center 100, 100
        self.mock_cascade.detectMultiScale.return_value = faces
        process_frame_func(mock_get_frame, 0)
        self.assertEqual(af.current_x, 100)

        # Step 2: Target shifts to 0.
        # current = 100 * 0.5 + 0 * 0.5 = 50
        faces = [[-10, -10, 20, 20]] # Center 0, 0
        self.mock_cascade.detectMultiScale.return_value = faces
        process_frame_func(mock_get_frame, 1)
        self.assertEqual(af.current_x, 50)

        # Step 3: Target stays 0.
        # current = 50 * 0.5 + 0 * 0.5 = 25
        process_frame_func(mock_get_frame, 2)
        self.assertEqual(af.current_x, 25)

    def test_clamping(self):
        """Test that the crop window is clamped to image boundaries."""
        af = AutoFraming(target_aspect_ratio=1.0, smoothing=0)

        # Frame: 100x100
        mock_frame = MagicMock()
        mock_frame.shape = (100, 100, 3)

        mock_get_frame = MagicMock(return_value=mock_frame)
        mock_clip = MagicMock()
        af.apply(mock_clip)
        process_frame_func = mock_clip.transform.call_args[0][0]

        # Target aspect 1.0 -> Crop 100x100

        # Case 1: Center is far left (-500, 50)
        # Should clamp to x1=0
        self.mock_cascade.detectMultiScale.return_value = [[-510, 40, 20, 20]] # Center -500, 50
        process_frame_func(mock_get_frame, 0)

        args = mock_frame.__getitem__.call_args[0][0]
        y_slice = args[0]
        x_slice = args[1]

        self.assertEqual(x_slice.start, 0)
        self.assertEqual(x_slice.stop, 100)
        self.assertEqual(y_slice.start, 0)
        self.assertEqual(y_slice.stop, 100)

        # Case 2: Center is far right (500, 50)
        # Should clamp to x1 = w - crop_w = 100 - 100 = 0
        self.mock_cascade.detectMultiScale.return_value = [[490, 40, 20, 20]] # Center 500, 50
        process_frame_func(mock_get_frame, 1)

        args = mock_frame.__getitem__.call_args[0][0]
        x_slice = args[1]
        self.assertEqual(x_slice.start, 0)
        self.assertEqual(x_slice.stop, 100)

if __name__ == '__main__':
    unittest.main()
