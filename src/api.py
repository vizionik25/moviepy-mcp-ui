from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import litellm
import logging
import os
import json
import ast
import asyncio
from typing import List, Dict, Any, Optional

# To ensure server.py is importable
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from server import mcp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
    api_keys: Dict[str, str]

def get_openai_tools():
    tools = []
    for name, tool in mcp._tool_manager._tools.items():
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.parameters
            }
        })
    return tools

@app.post("/api/chat")
async def chat(request: ChatRequest):
    model = None
    api_key = None

    if request.api_keys.get("openai"):
        model = "gpt-4o"
        api_key = request.api_keys["openai"]
    elif request.api_keys.get("anthropic"):
        model = "claude-3-5-sonnet-20240620"
        api_key = request.api_keys["anthropic"]
    elif request.api_keys.get("gemini"):
        model = "gemini/gemini-1.5-pro"
        api_key = request.api_keys["gemini"]

    if not model or not api_key:
        raise HTTPException(status_code=400, detail="No valid API key provided")

    tools = get_openai_tools()
    messages = request.messages

    try:
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            api_key=api_key
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    response_message = response.choices[0].message

    if response_message.tool_calls:
        messages.append(response_message.model_dump())

        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            try:
                function_args = json.loads(tool_call.function.arguments)
            except:
                function_args = {}

            content = ""
            try:
                result = await mcp._tool_manager.call_tool(function_name, function_args)
                texts = []
                for item in result.content:
                    if item.type == 'text':
                        texts.append(item.text)
                    elif item.type == 'image':
                        texts.append("[Image]")
                content = "\n".join(texts)
            except Exception as e:
                content = f"Error executing tool {function_name}: {str(e)}"

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": content
            })

        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                tools=tools,
                api_key=api_key
            )
            return response.choices[0].message
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return response_message

@app.get("/api/clips")
async def get_clips():
    try:
        result = await mcp._tool_manager.call_tool("list_clips", {})
        text = result.content[0].text
        clips_dict = ast.literal_eval(text)

        clips = []
        for cid, ctype in clips_dict.items():
            clips.append({
                "id": cid,
                "name": f"Clip {cid[:8]}",
                "duration": "Unknown",
                "thumbnail": "/placeholder.svg",
                "type": ctype
            })
        return clips
    except Exception as e:
        logger.error("Failed to list clips", exc_info=True)
        return []
