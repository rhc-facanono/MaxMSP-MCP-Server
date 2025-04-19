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

    def send_command(self, cmd: dict):
        """Send a command to MaxMSP to involke the corresponding JavaScript function."""
        self.sock.send_message("/mcp", json.dumps(cmd))
        print(f"Sent to MaxMSP: {cmd}")


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
def add_max_object(
    ctx: Context,
    position: list,
    obj_type: str,
    varname: str,
    args: list,
):
    """Add a new Max object.
    Args:
        position (list): Position in the Max patch as [x, y].
        obj_type (str): Type of the Max object (e.g., "cycle~", "dac~").
        varname (str): Variable name for the object.
        args (list): Arguments for the object.
    """
    maxmsp = ctx.request_context.lifespan_context.get("maxmsp")
    assert len(position) == 2, "Position must be a list of two integers."
    # position = " ".join(str(x) for x in position)
    # args = " ".join(str(x) for x in args)
    # maxmsp.send_command(" ".join([
    #     "add_object",
    #     position,
    #     obj_type,
    #     varname,
    #     args
    # ]))
    cmd = {"action": "add_object"}
    kwargs = {"position":   position, 
              "obj_type":   obj_type, 
              "args":       args,
              "varname":    varname}
    cmd.update(kwargs)
    maxmsp.send_command(cmd)


@mcp.tool()
def remove_max_object(
    ctx: Context,
    varname: str,
):
    """Delete a Max object.
    Args:
        varname (str): Variable name for the object.
    """
    maxmsp = ctx.request_context.lifespan_context.get("maxmsp")
    cmd = {"action": "remove_object"}
    kwargs = {"varname":    varname}
    cmd.update(kwargs)
    maxmsp.send_command(cmd)


@mcp.tool()
def connect_max_objects(
    ctx: Context,
    src_varname: str,
    outlet_idx: int,
    dst_varname: str,
    inlet_idx: int,
):
    """Connect two Max objects.
    Args:
        src_varname (str): Variable name of the source object.
        outlet_idx (int): Outlet index on the source object.
        dst_varname (str): Variable name of the destination object.
        inlet_idx (int): Inlet index on the destination object.
    """
    maxmsp = ctx.request_context.lifespan_context.get("maxmsp")
    # maxmsp.send_command(" ".join([
    #     "connect_objects",
    #     src_varname,
    #     str(outlet_idx),
    #     dst_varname,
    #     str(inlet_idx)
    # ]))
    cmd = {"action": "connect_objects"}
    kwargs = {"src_varname":    src_varname, 
              "outlet_idx":     outlet_idx, 
              "dst_varname":    dst_varname,
              "inlet_idx":      inlet_idx}
    cmd.update(kwargs)
    maxmsp.send_command(cmd)


@mcp.tool()
def disconnect_max_objects(
    ctx: Context,
    src_varname: str,
    outlet_idx: int,
    dst_varname: str,
    inlet_idx: int,
):
    """Disconnect two Max objects.
    Args:
        src_varname (str): Variable name of the source object.
        outlet_idx (int): Outlet index on the source object.
        dst_varname (str): Variable name of the destination object.
        inlet_idx (int): Inlet index on the destination object.
    """
    maxmsp = ctx.request_context.lifespan_context.get("maxmsp")
    # maxmsp.send_command(" ".join([
    #     "disconnect_objects",
    #     src_varname,
    #     str(outlet_idx),
    #     dst_varname,
    #     str(inlet_idx)
    # ]))
    cmd = {"action": "disconnect_objects"}
    kwargs = {"src_varname":    src_varname, 
              "outlet_idx":     outlet_idx, 
              "dst_varname":    dst_varname,
              "inlet_idx":      inlet_idx}
    cmd.update(kwargs)
    maxmsp.send_command(cmd)


if __name__ == "__main__":
    mcp.run()
