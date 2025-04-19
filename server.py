# server.py
from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
import os
import json

# Configuration: IP and port for MaxMSP's [udpreceive] object
MAX_OSC_HOST = os.environ.get("MAX_OSC_HOST", "127.0.0.1") # Localhost (adjust if Max runs on another machine)
MAXMSP_UDP_PORT = int(os.environ.get("MAXMSP_UDP_PORT", "5000")) # Must match your [udpreceive] port in Max
# MAX_FEEDBACK_PORT = int(os.environ.get("MAX_FEEDBACK_PORT", "5001"))


class MaxMSPConnection:
    def __init__(self, max_ip, max_port):
        from pythonosc.udp_client import SimpleUDPClient
        self.sock = SimpleUDPClient(max_ip, max_port)

    def send_command(self, action, **kwargs):
        """Send a JSON command to MaxMSP."""
        msg = {"action": action}
        msg.update(kwargs)
        data = json.dumps(msg)
        self.sock.send_message("/mcp", data)
        print(f"Sent to MaxMSP: {data}")


@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Manage server lifespan"""
    try:
        maxmsp = MaxMSPConnection(MAX_OSC_HOST, MAXMSP_UDP_PORT)
        yield {"maxmsp": maxmsp}
    finally:
        pass


# Create the MCP server with lifespan support
mcp = FastMCP(
    "MaxMSPMCP",
    description="MaxMSP integration through the Model Context Protocol",
    lifespan=server_lifespan
)


@mcp.tool()
def create_max_object(
    ctx: Context,
    obj_type: str,
    args: list,
    position: list,
    varname: str = None,
):
    """Create a new Max object."""
    payload = {"type": obj_type, "args": args, "position": position}
    if varname:
        payload["varname"] = varname
    maxmsp = ctx.request_context.lifespan_context.get("maxmsp")
    maxmsp.send_command("add_object", **payload)


@mcp.tool()
def connect_max_objects(
    ctx: Context,
    src: str,
    dst: str,
    outlet: int = 0,
    inlet: int = 0,
):
    """Connect two Max objects."""
    maxmsp = ctx.request_context.lifespan_context.get("maxmsp")
    maxmsp.send_command("connect", src=src, dst=dst, outlet=outlet, inlet=inlet)

if __name__ == "__main__":
    mcp.run()
