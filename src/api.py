from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import litellm
import os
import re
import json
import ast
from typing import List, Dict, Any

# To ensure server.py is importable
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from server import mcp

app = FastAPI()

# Secure CORS Policy
# 1. Allow Localhost (IPv4)
# 2. Allow Private Networks (RFC 1918)
# 3. Allow explicitly defined origins via ALLOWED_ORIGINS env var

allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
allowed_origins_list = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

# Escape user provided origins to be safe in regex
escaped_origins = [re.escape(origin) for origin in allowed_origins_list]

# Regex pattern for localhost and private IPs
private_ip_pattern = (
    r"^https?://("
    r"localhost|"
    r"127\.0\.0\.1|"
    r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|"
    r"192\.168\.\d{1,3}\.\d{1,3}"
    r")(:\d+)?$"
)

if escaped_origins:
    allow_origin_regex = f"({private_ip_pattern})|({'|'.join(escaped_origins)})"
else:
    allow_origin_regex = private_ip_pattern

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=allow_origin_regex,
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
    if request.api_keys.get("openai"):
        os.environ["OPENAI_API_KEY"] = request.api_keys["openai"]
        model = "gpt-4o"
    if request.api_keys.get("anthropic"):
        os.environ["ANTHROPIC_API_KEY"] = request.api_keys["anthropic"]

        if not model:
            model = "claude-3-5-sonnet-20240620"
    if request.api_keys.get("gemini"):
        os.environ["GEMINI_API_KEY"] = request.api_keys["gemini"]
        os.environ["GOOGLE_API_KEY"] = request.api_keys["gemini"]

        if not model:
            model = "gemini/gemini-1.5-pro"

    if not model:
        raise HTTPException(status_code=400, detail="No valid API key provided")

    tools = get_openai_tools()
    messages = request.messages

    try:
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
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
            except Exception:
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
                tools=tools
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
        print(e)
        return []
