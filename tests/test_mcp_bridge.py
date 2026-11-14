"""Integration test for the MCP stdio bridge using a local stub server."""

from __future__ import annotations

import sys
from pathlib import Path

from pinconv2.level2.mcp_bridge import MCPStdioClient

STUB = r"""
import json
import sys


def send(payload):
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


for line in sys.stdin:
    if not line.strip():
        continue
    message = json.loads(line)
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        send(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "serverInfo": {"name": "pinconv2-stub", "version": "0.1"},
                },
            }
        )
    elif method == "tools/list":
        send(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "ping",
                            "description": "stub ping",
                            "inputSchema": {"type": "object"},
                        }
                    ]
                },
            }
        )
    elif method == "tools/call":
        arguments = message["params"].get("arguments", {})
        send(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"pong": arguments, "server": "stub"}
                            ),
                        }
                    ]
                },
            }
        )
"""


def test_mcp_bridge_round_trip(tmp_path: Path) -> None:
    script = tmp_path / "stub_mcp.py"
    script.write_text(STUB, encoding="utf-8")
    client = MCPStdioClient([sys.executable, str(script)])
    try:
        tools = client.list_tools()
        assert [tool["name"] for tool in tools] == ["ping"]
        result = client.call_tool("ping", {"asset": "AS-15"})
        assert result["server"] == "stub"
        assert result["pong"] == {"asset": "AS-15"}
    finally:
        client.close()
