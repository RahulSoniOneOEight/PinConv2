"""Minimal MCP stdio bridge for OpenMontage Studio.

Studio exposes its MCP server as ``OpenMontage Studio.exe --mcp``. This client
speaks newline-delimited JSON-RPC over stdio, which lets the Python CLI use the
same ledger and tools as the agent runtime. It is read/write only through the
Studio tools; it never edits Studio files directly.
"""

from __future__ import annotations

import json
import queue
import subprocess
import threading
from pathlib import Path
from typing import Any

DEFAULT_EXE = Path(
    r"C:\Users\LENOVO\AppData\Local\Programs\OpenMontage Studio\OpenMontage Studio.exe"
)


class MCPError(RuntimeError):
    """The MCP server refused or failed a request."""


class MCPStdioClient:
    def __init__(self, command: list[str] | None = None, timeout: float = 60.0) -> None:
        self.command = command or [str(DEFAULT_EXE), "--mcp"]
        self.timeout = timeout
        self._next_id = 1
        self._responses: queue.Queue[dict[str, Any]] = queue.Queue()
        self._stderr: list[str] = []
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._reader = threading.Thread(target=self._read_stdout, daemon=True)
        self._reader.start()
        self._err_reader = threading.Thread(target=self._read_stderr, daemon=True)
        self._err_reader.start()
        self.initialize()

    def _read_stdout(self) -> None:
        assert self.process.stdout is not None
        for line in self.process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                self._responses.put(json.loads(line))
            except json.JSONDecodeError:
                continue

    def _read_stderr(self) -> None:
        assert self.process.stderr is not None
        for line in self.process.stderr:
            self._stderr.append(line.rstrip())
            if len(self._stderr) > 200:
                del self._stderr[:100]

    def _send(self, message: dict[str, Any]) -> None:
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        while True:
            try:
                message = self._responses.get(timeout=self.timeout)
            except queue.Empty as error:
                raise MCPError(
                    f"MCP timeout for {method}; stderr: {' | '.join(self._stderr[-3:])}"
                ) from error
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise MCPError(f"{method}: {message['error']}")
            payload = message.get("result", {})
            return payload if isinstance(payload, dict) else {"value": payload}

    def initialize(self) -> dict[str, Any]:
        result = self._request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "pinconv2", "version": "0.2"},
            },
        )
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        return result

    def list_tools(self) -> list[dict[str, Any]]:
        result = self._request("tools/list", {})
        return list(result.get("tools", []))

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        content = result.get("content") or []
        text = ""
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text += str(item.get("text", ""))
        if not text:
            return result
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return {"text": text}
        return parsed if isinstance(parsed, dict) else {"value": parsed}

    def close(self) -> None:
        try:
            if self.process.stdin:
                self.process.stdin.close()
            self.process.wait(timeout=5)
        except Exception:
            self.process.kill()
