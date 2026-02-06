import asyncio
from server import mcp
import sys

async def main():
    try:
        # Try calling list_clips
        result = await mcp._tool_manager.call_tool("list_clips", {})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
