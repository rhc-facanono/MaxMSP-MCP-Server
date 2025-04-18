# Building an MCP Server for MaxMSP with Python & `thispatcher`

## Overview

This solution enables MaxMSP to expose its objects as MCP resources and allows remote (programmatic) manipulation of Max’s patchers (adding objects, connecting cords) via the MCP protocol.

## Components

1. **Python MCP Server** (using [`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk))
2. **MaxMSP Scripting Bridge** (via Max’s `js` or `py` object, using `thispatcher`)
3. **Communication Layer** (WebSocket or UDP/TCP between Python and MaxMSP)

---

## 1. Python MCP Server

You’ll create a Python server that implements MCP and communicates with MaxMSP.

```python name=mcp_max_server.py
import asyncio
from mcp.server import MCPServer  # from your SDK
import websockets  # or use Python's socket module

class MaxMSPResource:
    def __init__(self, ws):
        self.ws = ws

    async def add_object(self, obj_type, position):
        msg = {"action": "add_object", "type": obj_type, "position": position}
        await self.ws.send(json.dumps(msg))

    async def connect_objects(self, src, dst):
        msg = {"action": "connect", "src": src, "dst": dst}
        await self.ws.send(json.dumps(msg))

class MaxMSPServer(MCPServer):
    async def on_connect(self, ws, path):
        self.max_resource = MaxMSPResource(ws)
        # Expose MCP resources here, e.g. self.max_resource

    # Implement MCP resource handlers here

async def main():
    async with websockets.serve(MaxMSPServer().on_connect, 'localhost', 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 2. MaxMSP Scripting Bridge

Use the [`js`](https://docs.cycling74.com/max8/refpages/js) object (or `py` if available) to receive commands from the Python server and manipulate the patcher.

**Example: `mcp_bridge.js`**

```javascript name=mcp_bridge.js
autowatch = 1;
var this_patcher = this.patcher;

function add_object(type, x, y) {
    var newObj = this_patcher.newdefault(x, y, type);
    outlet(0, "object_added", newObj.varname);
}

function connect(src_varname, dst_varname, outlet, inlet) {
    var src = this_patcher.getnamed(src_varname);
    var dst = this_patcher.getnamed(dst_varname);
    this_patcher.connect(src, outlet, dst, inlet);
    outlet(0, "connected", src_varname, dst_varname);
}

// Add functions to receive messages from UDP/TCP/WebSocket (see Max’s [node.script], [mxj net.tcp.recv], [udpreceive], etc.)
```

- **Place this script in a Max patch with a [js] object.**
- Use [node.script] or [udpreceive] to get messages from Python, and trigger these JS functions.

---

## 3. Communication Layer

- **From Python:** Send JSON messages to MaxMSP (e.g. via UDP/TCP/WebSocket).
- **In Max:** Use [node.script], [mxj net.tcp.recv], or [udpreceive] to receive messages, parse them, and call your JS functions.

**Example: UDP Listener in Max**

- [udpreceive 9999] → [route add_object connect] → [js mcp_bridge.js]

---

## Example Message Protocol

Python sends:

```json
{"action": "add_object", "type": "cycle~", "position": [100, 100]}
{"action": "connect", "src": "osc1", "dst": "dac1", "outlet": 0, "inlet": 0}
```

Max receives, calls corresponding JS function to create/connect objects.

---

## Exposing Max Objects as MCP Resources

- Implement resource discovery in your Python server by querying Max for current objects (send a request, have JS reply with current object list).
- Register each object as an MCP resource with unique URIs.

---

## Summary

- **Python MCP Server** exposes Max’s objects as resources and listens for MCP commands.
- **MaxMSP Bridge** receives commands, manipulates patcher via `thispatcher`, and can report back state.
- **Communication is via UDP/TCP/WebSocket** between Python and Max.

---

**Tips:**
- Start with just add/connect commands.
- Once working, implement resource discovery and sync.
- Consider security for remote control.

**References:**
- [`thispatcher` docs](https://docs.cycling74.com/legacy/max8/refpages/Thispatcher)
- [js object docs](https://docs.cycling74.com/max8/refpages/js)
- [node.script](https://docs.cycling74.com/max8/refpages/node.script)
- [Max UDP/TCP objects](https://docs.cycling74.com/max8/vignettes/networking)
