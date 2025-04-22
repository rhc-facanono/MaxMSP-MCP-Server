# MaxMSP-MCP Server

This project uses the Model Context Protocol (MCP) to let LLMs directly understand, edit, and generate Max patches. Examples:

![img](./assets/demo.gif)

## Installation  

### Prerequisites  

 - Python 3.8 or newer  
 - [uv package manager](https://github.com/astral-sh/uv)  
 - Max 9 or newer (because some of the scripts require the Javascript V8 engine), we have not tested it on Max 8 or earlier versions of Max yet.  

### Installing the MCP server

1. Install uv:
```
# On macOS and Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# On Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
2. Clone this repository and open its directory:
```
git clone https://github.com/tiianhk/MaxMSP-MCP-Server.git
cd MaxMSP-MCP-Server
```
3. Start a new environment and install python dependencies:
```
uv venv
uv pip install -r requirements.txt
```
4. Install the MaxMSP MCP server:
```
# Install for Claude
python install.py --client claude
# Install for Cursor
python install.py --client cursor
```

### Installing to a Max patch  
