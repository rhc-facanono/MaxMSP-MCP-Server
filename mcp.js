autowatch=1;
inlets = 1; // 0: JSON input
outlets = 2; // 0: error messages, 1: feedback messages


var p = this.patcher

// Helper: Safely parse JSON, report errors
function safe_parse_json(str) {
    try {
        return JSON.parse(str);
    } catch (e) {
        outlet(0, "error", "Invalid JSON: " + e.message);
        return null;
    }
}

// Called when a message arrives at inlet 0 (from [udpreceive] or similar)
function anything() {
    var msg = arrayfromargs(messagename, arguments).join(" ");
    var data = safe_parse_json(msg);
    if (!data) return;

    switch (data.action) {
        case "fetch_test":
            if (data.request_id) {
                fetch_test(data.request_id);
            } else {
                outlet(0, "error", "Missing request_id for fetch_test");
            }
            break;
        case "add_object":
            if (data.obj_type && data.position && data.varname) {
                add_object(data.position[0], data.position[1], data.obj_type, data.args, data.varname);
            } else {
                outlet(0, "error", "Missing obj_type or position or varname for add_object");
            }
            break;
        case "remove_object":
            if (data.varname) {
                remove_object(data.varname);
            } else {
                outlet(0, "error", "Missing varname for remove_object");
            }
            break;
        case "connect_objects":
            if (data.src_varname && data.dst_varname) {
                connect_objects(data.src_varname, data.outlet_idx || 0, data.dst_varname, data.inlet_index || 0);
            } else {
                outlet(0, "error", "Missing src_varname or dst_varname for connect_objects");
            }
            break;
        case "disconnect_objects":
            if (data.src_varname && data.dst_varname) {
                disconnect_objects(data.src_varname, data.outlet_idx || 0, data.dst_varname, data.inlet_index || 0);
            } else {
                outlet(0, "error", "Missing src_varname or dst_varname for disconnect_objects");
            }
            break;
        default:
            outlet(0, "error", "Unknown action: " + data.action);
    }
}

function notify_test(){
    outlet(1, "/mcp/notify", JSON.stringify({"results": "some notification"}, null, 2));
}

function fetch_test(request_id) {
    outlet(1, "/mcp/response", request_id, JSON.stringify({"results": "my response"}, null, 2));
}

function add_object(x, y, type, args, var_name) {
    var new_obj = p.newdefault(x, y, type, args);
    new_obj.varname = var_name;
}

function remove_object(var_name) {
	var obj = p.getnamed(var_name);
	p.remove(obj);
}

function connect_objects(src_varname, outlet_idx, dst_varname, inlet_idx) {
    var src = p.getnamed(src_varname);
    var dst = p.getnamed(dst_varname);
    p.connect(src, outlet_idx, dst, inlet_idx);
}

function disconnect_objects(src_varname, outlet_idx, dst_varname, inlet_idx) {
	var src = p.getnamed(src_varname);
    var dst = p.getnamed(dst_varname);
	p.disconnect(src, outlet_idx, dst, inlet_idx);
}
