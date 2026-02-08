#moviepy-mcp-ui Frontend

This is the React/Next.js frontend for the **mcp-ui-moviepy** project. It provides a user interface to interact with the MoviePy MCP server, visualize clips, and manage video editing workflows.

For full project documentation, including backend setup and usage, please refer to the main [README.md](../README.md).

## Getting Started

### Prerequisites

-   **Node.js**: Version 18 or higher.
-   **npm**: Package manager (or yarn/pnpm/bun).

### Installation

Navigate to the `web` directory and install dependencies:

```bash
cd web
npm install
```

### Running Development Server

To start the frontend development server independently:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Building for Production

To create an optimized production build:

```bash
npm run build
```

Then start the production server:

```bash
npm start
```

## Project Structure

-   `src/app`: Next.js App Router pages and layouts.
-   `src/components`: Reusable UI components.
-   `src/lib`: Utility functions and API clients.
-   `src/hooks`: Custom React hooks.

## Integration with MCP Server

The frontend communicates with the backend API server (running on `http://localhost:8000`) to execute MoviePy commands and retrieve clip data. Ensure the backend is running for full functionality.
