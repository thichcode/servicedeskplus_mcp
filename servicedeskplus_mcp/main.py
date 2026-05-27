#!/usr/bin/env python3
# ServiceDesk Plus MCP Server 2.0 (on-premise localhost:8080)
# Docs: https://www.manageengine.com/products/service-desk/sdpod-v3-api/

import asyncio
import json
import os
from dotenv import load_dotenv
from mcp.server import MCPServer

def load_sdp_functions():
    """Load all ServiceDesk Plus API functions from sdp_client.py"""
    # Import dynamically to avoid circular imports
    import importlib
    sdp_client = importlib.import_module("sdp_client")
    
    # Register all public functions (no underscore prefix)
    count = 0
    for name in dir(sdp_client):
        if not name.startswith("_"):
            func = getattr(sdp_client, name)
            if callable(func):
                server.register_tool(name, func)
                count += 1
    return count

if __name__ == "__main__":
    load_dotenv()  # Load .env file
    
    # Create MCP server
    server = MCPServer()
    
    # Register all SDP functions
    tool_count = load_sdp_functions()
    print(f"✅ Registered {tool_count} ServiceDesk Plus tools")
    
    # Run server on stdin/stdout (port 8080
    print("🚀 MCP server started on localhost:8080 (stdio transport)")
    asyncio.run(server.run_stdio())