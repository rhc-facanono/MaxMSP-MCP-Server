# MaxMSP-MCP Server for LLMs

![img](./assets/demo.gif)


## Installation  



### Prerequisites  

 - Python 3.8 or newer  
 - [uv package manager](https://github.com/astral-sh/uv)  
 - Max 9 or newer (because some of the scripts require the Javascript V8 engine), we have not tested it on Max 8 or earlier versions of Max yet.  

### Installing for a LLM client

Install `uv`, start a new environment and install the dependencies
To install the Max/MSP MCP server, run
```
python install.py --client claude # install for Claude
python install.py --client cursor # install for Cursor
```

### Installing to a Max patch  