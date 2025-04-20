autowatch = 1;

const Max = require("max-api");
const { Server } = require("socket.io");

// Configuration
const PORT = 5002;
const NAMESPACE = "/mcp";

// Create Socket.IO server
const io = new Server(PORT, {
  cors: { origin: "*" }
});


function safe_parse_json(str) {
    try {
        return JSON.parse(str);
    } catch (e) {
        Max.post("error, Invalid JSON: " + e.message);
        return null;
    }
}

Max.addHandler("response", async (...msg) => {
	var str = msg.join("")
	var data = safe_parse_json(str);
	await io.of(NAMESPACE).emit("response", data);
	//await Max.post(`Sent response: ${JSON.stringify(data)}`);
});

Max.post(`Socket.IO MCP server listening on port ${PORT}`);

//Max.outlet('command', 'get_patcher_objects');

io.of(NAMESPACE).on("connection", (socket) => {
  Max.post(`Socket.IO client connected: ${socket.id}`);

  socket.on("package", async (data) => {
  // Max.post(`Received package: ${JSON.stringify(data)}`);
	
	Max.outlet("package", JSON.stringify(data)); 
  });

  socket.on("disconnect", () => {
    Max.post(`Socket.IO client disconnected: ${socket.id}`);
  });
});
