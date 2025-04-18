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

    def add_object(self, obj_type, position, varname=None):
        """Add a Max object via MCP."""
        payload = {"type": obj_type, "position": position}
        if varname:
            payload["varname"] = varname
        self.send_command("add_object", **payload)

    def connect(self, src, dst, outlet=0, inlet=0):
        """Connect two Max objects."""
        self.send_command("connect", src=src, dst=dst, outlet=outlet, inlet=inlet)

# Example usage
if __name__ == '__main__':
    import time

    server = MaxMCPUDPServer()
    # Add a 'cycle~' object at position (100, 100), name it 'osc1'
    server.add_object("cycle~", [100, 100], varname="osc1")
    time.sleep(0.1)
    # Add a 'dac~' object at (200, 100), name it 'dac1'
    server.add_object("dac~", [200, 100], varname="dac1")
    time.sleep(0.1)
    # Connect 'osc1' outlet 0 to 'dac1' inlet 0
    server.connect("osc1", "dac1", outlet=0, inlet=0)