# mcp-ui-moviepy

A powerful **Model Context Protocol (MCP)** server that exposes **MoviePy** functionalities as tools for LLMs, complete with a built-in React/Next.js UI for visualization and interaction.

This project enables Large Language Models (LLMs) to perform complex video editing tasks, apply custom visual effects, and generate multimedia content programmatically.

## Features

-   **Video Editing**: Cut, concatenate, composite, and transform video clips.
-   **Audio Editing**: Manipulate audio tracks, add background music, and apply audio effects.
-   **Custom Visual Effects**: Includes a library of advanced effects like:
    -   **Matrix Digital Rain**: Cyberpunk-style code rain overlay.
    -   **Kaleidoscope**: Mesmerizing radial symmetry patterns.
    -   **Rotating Cube**: 3D cube projection of video content.
    -   **Glitch & RGB Sync**: Stylistic chromatic aberration and synchronization.
    -   **Auto-Framing**: Intelligent cropping for vertical video platforms (TikTok/Reels).
-   **MCP Integration**: Fully compliant with the Model Context Protocol, ready for use with clients like Claude Desktop.
-   **React UI**: A modern dashboard for visualizing clips, previewing edits, and managing the editing workflow.
-   **FastAPI Backend**: Robust API server handling communication between the MCP server, LLM, and Frontend.

## Prerequisites

-   **Python**: Version 3.12 or higher.
-   **Node.js**: Version 18+ (for the frontend).
-   **uv**: Recommended for Python dependency management.
-   **ImageMagick**: Required for text-based video generation (`TextClip`).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/mcp-ui-moviepy.git
    cd mcp-ui-moviepy
    ```

2.  **Install Python dependencies (using `uv`):**
    ```bash
    uv sync
    ```
    Alternatively, using pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Frontend dependencies:**
    ```bash
    cd web
    npm install
    cd ..
    ```

## Usage

### Running the Application

You can start both the backend MCP server and the frontend UI with a single command:

```bash
# Using uv (recommended)
uv run run.py

# Or using python directly
python run.py
```

This will launch:
-   **Backend API**: http://localhost:8000
-   **Frontend UI**: http://localhost:3000

### Using with MCP Clients (e.g., Claude Desktop)

To use this server with Claude Desktop, add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "moviepy": {
      "command": "uv",
      "args": [
        "run",
        "src/server.py"
      ]
    }
  }
}
```

Make sure to provide the absolute path to your project directory if `uv` is not in your global path or if you are running from a different location.

### Environment Variables

Create a `.env` file in the root directory (optional) or set these environment variables:

-   `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins (default: `http://localhost:3000,http://127.0.0.1:3000`).
-   `OPENAI_API_KEY`: Required if using OpenAI models via `litellm`.
-   `ANTHROPIC_API_KEY`: Required if using Anthropic models via `litellm`.
-   `GEMINI_API_KEY`: Required if using Gemini models via `litellm`.

## Tools Reference

The server exposes a wide range of tools. Here are some key categories:

### Clip Management
-   `list_clips()`: List all loaded clips.
-   `delete_clip(clip_id)`: Remove a clip from memory.

### Video IO
-   `video_file_clip(filename)`: Load a video file.
-   `image_clip(filename)`: Create a clip from an image.
-   `text_clip(text, ...)`: Create a text overlay.
-   `write_videofile(clip_id, filename)`: Render and save the video.

### Transformations
-   `subclip(clip_id, start, end)`: Trim a clip.
-   `composite_video_clips(clip_ids)`: Layer multiple clips.
-   `concatenate_video_clips(clip_ids)`: Join clips sequentially.
-   `vfx_resize(clip_id, width, height)`: Resize video.
-   `vfx_multiply_speed(clip_id, factor)`: Change playback speed.

### Custom Effects
See the `src/custom_fx/` directory for implementation details.
-   `vfx_matrix`: Apply Matrix digital rain.
-   `vfx_kaleidoscope`: Apply kaleidoscope effect.
-   `vfx_rotating_cube`: Map video to a 3D rotating cube.
-   `vfx_rgb_sync`: Apply RGB sync / glitch effects.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to set up your development environment and submit pull requests.

## License

[MIT License](LICENSE)
