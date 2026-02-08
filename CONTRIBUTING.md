# Contributing to mcp-ui-moviepy

Thank you for your interest in contributing to **mcp-ui-moviepy**! We welcome improvements, bug fixes, and new features.

## Getting Started

### Prerequisites

1.  **Python 3.12+**: Ensure Python is installed.
2.  **Node.js**: Version 18+ is required for the frontend.
3.  **uv**: We use `uv` for Python dependency management.
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

### Setting up the Environment

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/mcp-ui-moviepy.git
    cd mcp-ui-moviepy
    ```

2.  **Install Python dependencies**:
    ```bash
    uv sync
    ```

3.  **Install Frontend dependencies**:
    ```bash
    cd web
    npm install
    cd ..
    ```

## Development Workflow

### Running the Project

You can start the full stack (backend + frontend) using the provided script:

```bash
uv run run.py
```

-   **Backend**: `http://localhost:8000`
-   **Frontend**: `http://localhost:3000`

### Running Tests

To run the test suite, you may need to install `pytest` if it's not already in the environment. You can use `uv` to run it with `pytest` temporarily installed:

```bash
PYTHONPATH=src uv run --with pytest pytest tests/
```

Or run specific test files:

```bash
PYTHONPATH=src uv run --with pytest pytest tests/test_security_fix.py
```

### Adding New Effects

We encourage adding creative video effects! Follow these steps to contribute a new effect:

1.  **Create a new file** in `src/custom_fx/` (e.g., `src/custom_fx/my_effect.py`).
2.  **Implement your effect** class or function. Ensure it accepts a `clip` and returns a modified clip.
    ```python
    from moviepy.editor import VideoClip
    import numpy as np

    class MyEffect:
        def __init__(self, intensity=1.0):
            self.intensity = intensity

        def apply(self, clip):
            # Implementation...
            return clip.fl_image(self.process_frame)

        def process_frame(self, image):
            # Frame processing logic...
            return image
    ```
3.  **Export your effect** in `src/custom_fx/__init__.py`:
    ```python
    from .my_effect import MyEffect
    ```
4.  **Register the effect as a tool** in `src/server.py`:
    ```python
    @mcp.tool
    def vfx_my_effect(clip_id: str, intensity: float = 1.0) -> str:
        """Apply my custom effect."""
        clip = get_clip(clip_id)
        return register_clip(clip.with_effects([MyEffect(intensity)]))
    ```
5.  **Add a test case** (optional but recommended) in `tests/`.

## Code Style

-   **Python**: Follow PEP 8 guidelines. Use type hints where possible.
-   **TypeScript/React**: Use functional components and hooks. Follow standard ESLint configuration.
-   **Documentation**: Add docstrings to all new functions and classes.

## Pull Request Process

1.  **Fork the repository** and create a feature branch (`git checkout -b feature/amazing-feature`).
2.  **Commit your changes** (`git commit -m 'Add some amazing feature'`).
3.  **Push to the branch** (`git push origin feature/amazing-feature`).
4.  **Open a Pull Request**. Please describe your changes clearly and link any relevant issues.

Thank you for contributing!
