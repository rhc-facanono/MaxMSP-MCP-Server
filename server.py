# server.py
from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager
import logging, os

from typing import AsyncIterator, Dict, Any, List, Union

# Configuration: IP and port for MaxMSP's [udpreceive] object
MAX_OSC_HOST = os.environ.get("MAX_OSC_HOST", "127.0.0.1") # Localhost (adjust if Max runs on another machine)
MAXMSP_UDP_PORT = int(os.environ.get("MAXMSP_UDP_PORT", "5000")) # Must match your [udpreceive] port in Max
MAX_FEEDBACK_PORT = int(os.environ.get("MAX_FEEDBACK_PORT", "5001"))


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MaxMSPMCPServer")


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    try:
        logger.info("AbletonMCP server starting up")
        
        try:
            # ableton = get_ableton_connection()
            logger.info("Successfully connected to Ableton on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Ableton on startup: {str(e)}")
            logger.warning("Make sure the Ableton Remote Script is running")
        
        yield {}
    finally:
        global _ableton_connection
        if _ableton_connection:
            logger.info("Disconnecting from Ableton on shutdown")
            _ableton_connection.disconnect()
            _ableton_connection = None
        logger.info("AbletonMCP server shut down")

# Create the MCP server with lifespan support
mcp = FastMCP(
    "AbletonMCP",
    description="Ableton Live integration through the Model Context Protocol",
    lifespan=server_lifespan
)


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
