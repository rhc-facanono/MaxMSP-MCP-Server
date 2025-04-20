# server.py
from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
import asyncio

from typing import Callable, Any
import logging
import uuid
import os
import json

# Configuration: IP and port for MaxMSP's [udpreceive] object
MAX_OSC_HOST = os.environ.get(
    "MAX_OSC_HOST", "127.0.0.1"
)  # Localhost (adjust if Max runs on another machine)
MAXMSP_UDP_PORT = int(
    os.environ.get("MAXMSP_UDP_PORT", "5000")
)  # Must match your [udpreceive] port in Max
MAXMSP_FEEDBACK_PORT = int(os.environ.get("MAXMSP_FEEDBACK_PORT", "5002"))

current_dir = os.path.dirname(os.path.abspath(__file__))
docs_path = os.path.join(current_dir, "docs.json")
with open(docs_path, "r") as f:
    docs = json.load(f)
flattened_docs = {}
for obj_list in docs.values():
    for obj in obj_list:
        flattened_docs[obj["name"]] = obj

maxmsp = None
osc_server_started = False

class MaxMSPConnection:
    def __init__(self, max_ip, max_port, feedback_port):
        from pythonosc.udp_client import SimpleUDPClient
        from pythonosc.dispatcher import Dispatcher
        
        self.host = max_ip
        self.port = max_port
        self.feedback_port = feedback_port

        self.sock = SimpleUDPClient(max_ip, max_port)
        self.dispatcher = Dispatcher()
        self.dispatcher.map("/mcp/notify", on_notify)
        self.dispatcher.map("/mcp/response", self._on_response)
        self._pending = {} # fetch requests that are not yet completed

    def send_command(self, cmd: dict):
        """Send a command to MaxMSP."""
        self.sock.send_message("/mcp", json.dumps(cmd))
        logging.info(f"Sent to MaxMSP: {cmd}")

    async def send_request(self, payload: dict, timeout = 2.0):
        """Send a fetch request to MaxMSP."""
        request_id = str(uuid.uuid4())
        future = self.loop.create_future()
        self._pending[request_id] = future

        payload.update({"request_id": request_id})
        self.sock.send_message("/mcp", json.dumps(payload))
        logging.info(f"Request to MaxMSP: {payload}")

        try:
            response = await asyncio.wait_for(future, timeout)
            return response
        except asyncio.TimeoutError:
            raise TimeoutError("No response received in time")
        finally:
            self._pending.pop(request_id, None)

    def _on_response(self, address, *args):
        # Expected: /mcp/response <request_id> <json_response>
        logging.info(f"Response: {args}")
        if len(args) < 2:
            return
        request_id, json_response = args[0], args[1]
        future = self._pending.get(request_id)
        if future and not future.done():
            future.set_result(json.loads(json_response))

    async def start_server(self) -> None:
        """IMPORTANT: This method should only be called ONCE per application instance.
        Multiple calls can lead to binding multiple ports unnecessarily.
        """
        from pythonosc.osc_server import AsyncIOOSCUDPServer
        
        try:
            # Create the server with the current feedback port
            self.loop = asyncio.get_event_loop()
            server = AsyncIOOSCUDPServer(
                (self.host, self.feedback_port), 
                self.dispatcher, 
                self.loop
            )
            await server.create_serve_endpoint()
            
            # Log a warning if we had to use an alternate port
            logging.warning(f"Make sure that Max is sending to port {self.feedback_port}")
            return
            
        except OSError as e:
            logging.error(f"Error starting OSC server: {e}")

@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Manage server lifespan"""
    global maxmsp, osc_server_started
    try:
        maxmsp = MaxMSPConnection(MAX_OSC_HOST, MAXMSP_UDP_PORT, MAXMSP_FEEDBACK_PORT)
        try:
            if not osc_server_started:
                # Start with port auto-selection if the configured port is unavailable
                await maxmsp.start_server()
                osc_server_started = True
                
                if maxmsp.feedback_port != MAXMSP_FEEDBACK_PORT:
                    logging.warning(f"Make sure Max is configured to send to port {maxmsp.feedback_port}")
                logging.info(f"Listening on {maxmsp.host}:{maxmsp.feedback_port}")
            else:
                logging.info(f"OSC server already running on {maxmsp.host}:{maxmsp.feedback_port}")
            
            # Yield the OSC connection to make it available in the lifespan context
            yield {"maxmsp": maxmsp}
        except Exception as e:
            logging.error(f"lifespan error starting OSC server: {e}")
            raise
    finally:
        pass

def on_notify(address: str, *args: Any) -> None:
    """Handle feedback messages from Max and notify MCP.

    Args:
        address: The OSC address received
        args: The arguments sent with the OSC message
    """
    
    logging.info(f"Received feedback from: {address}")
    logging.info(f"Content: {args}")


# Create the MCP server with lifespan support
mcp = FastMCP(
    "MaxMSPMCP",
    description="MaxMSP integration through the Model Context Protocol",
    lifespan=server_lifespan,
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
    cmd = {"action": "add_object"}
    kwargs = {
        "position": position,
        "obj_type": obj_type,
        "args": args,
        "varname": varname,
    }
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
    kwargs = {"varname": varname}
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
    cmd = {"action": "connect_objects"}
    kwargs = {
        "src_varname": src_varname,
        "outlet_idx": outlet_idx,
        "dst_varname": dst_varname,
        "inlet_idx": inlet_idx,
    }
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
    cmd = {"action": "disconnect_objects"}
    kwargs = {
        "src_varname": src_varname,
        "outlet_idx": outlet_idx,
        "dst_varname": dst_varname,
        "inlet_idx": inlet_idx,
    }
    cmd.update(kwargs)
    maxmsp.send_command(cmd)


@mcp.resource("list://objects")
def list_objects():
    """Returns a list of all available objects in MaxMSP."""
    return list(flattened_docs.keys())


@mcp.resource("docs://{object_name}")
def get_object_doc(object_name: str):
    """Retrieve the official documentation for a given object.

    Use this resource to understand how a specific object works, including its
    description, inlets, outlets, arguments, methods(messages), and attributes.

    Args:
        object_name (str): Name of the object to look up.

    Returns:
        dict: Official documentation details for the specified object.
    """
    try:
        return flattened_docs[object_name]
    except KeyError:
        return {
            "success": False,
            "error": "Invalid object name",
            "suggestion": "Make sure the object name is a valid MaxMSP object name.",
        }

@mcp.resource("patcher://objects")
async def test_fetch_request():
    """Send a test fetch request to MaxMSP and return the response.
    
    Use this resource to verify the connection and functionality of the fetch command.
    
    Returns:
        list: A list containing the response from MaxMSP.
    """
    
    payload = {"action": "fetch_test"}
    response = await maxmsp.send_request(payload)

    return [response]


if __name__ == "__main__":
    mcp.run()
