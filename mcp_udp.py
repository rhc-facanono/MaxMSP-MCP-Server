# import socket
from pythonosc.udp_client import SimpleUDPClient
import json

class MaxMCPUDPServer:
    def __init__(self, max_ip, max_port):
        self.sock = SimpleUDPClient(max_ip, max_port)

    def send_command(self, action, **kwargs):
        """Send a JSON command to MaxMSP."""
        msg = {"action": action}
        msg.update(kwargs)
        data = json.dumps(msg)
        self.sock.send_message("/mcp", data)
        print(f"Sent to MaxMSP: {data}")

    def add_object(self, obj_type, args, position, varname=None):
        """Add a new Max object.
        
        Args:
            obj_type (str): Type of the Max object (e.g., "cycle~", "dac~").
            args (list): Arguments for the object.
            position (list): Position in the Max patch as [x, y].
            varname (str, optional): Variable name for the object.
        """
        payload = {"type": obj_type, "args": args, "position": position}
        if varname:
            payload["varname"] = varname
        self.send_command("add_object", **payload)

    def connect(self, src, dst, outlet=0, inlet=0):
        """Connect two Max objects.
        
        Args:
            src (str): Name of the source object.
            dst (str): Name of the destination object.
            outlet (int): Outlet index on the source object.
                Must be less than the total number of outlets on the source.
            inlet (int): Inlet index on the destination object.
                Must be less than the total number of inlets on the destination.
        """
        self.send_command("connect", src=src, dst=dst, outlet=outlet, inlet=inlet)

# Example usage
if __name__ == '__main__':
    import time
    import os

    server = MaxMCPUDPServer(
        os.environ.get("PD_OSC_HOST", "127.0.0.1"),
        int(os.environ.get("PD_OSC_PORT", "5000"))
    )
    # Add a 'cycle~' object at position (100, 100), name it 'osc1'
    # server.add_object("cycle~", [400], [100, 100], varname="osc1")
    # time.sleep(0.1)
    # # Add a 'dac~' object at (200, 100), name it 'dac1'
    # server.add_object("dac~", [], [200, 100], varname="dac1")
    # time.sleep(0.1)
    # # Connect 'osc1' outlet 0 to 'dac1' inlet 0
    # server.connect("osc1", "dac1", outlet=0, inlet=0)

    server.sock.send_message("/mcp", "hi")
