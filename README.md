# moviepy-mcp-ui

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
    git clone https://github.com/yourusername/moviepy-mcp-ui.git
    cd moviepy-mcp-ui
    ```
2.  **Install Python dependencies (using `uv`):**
    ```bash
    uv sync
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
```
This will launch:
-   **Backend API**: http://localhost:8000
-   **Frontend UI**: http://localhost:3000
The frontend UI has a built in MCP Client meaning everything works out the box after you add your API Key from your LLM provider. 

### Alternatively you can use the MCP Server with other clients
## Using with Claude Desktop, VSCode, etc...
First you will need to decide if you want to run it as a 'stdio', 'sse', or 'http'(recommended) implementation. Unless you will be working with 
large files or many files to where you need the speed of 'stdio' offers, than it's recommended to use 'http'. Once you've decided on the transport
to use let's say 'http'. You'll first need to spin up the server like so:

```bash
uv run src/server.py --transport="http" --host="0.0.0.0" --port=8080
```

Then use this server with Claude Desktop, add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "moviepy": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```
Or if you are using stdio then you can omit spinning up the server manuallyand add this to your config.json:
```json
{
  "mcpServers": {
    "moviepy": {
      "command": "/full/path/to/your/projects/venv/uv",
      "args": [
        "run",
        "/full/path/to/src/server.py"
      ]
    }
  }
}
```

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
