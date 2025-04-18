autowatch = 1;
inlets = 1; // Receive network messages here
outlets = 1; // For status, responses, etc.

var this_patcher = this.patcher;

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
        case "add_object":
            if (data.type && data.position) {
                add_object(data.position[0], data.position[1], data.type, data.args, data.varname);
            } else {
                outlet(0, "error", "Missing type or position for add_object");
            }
            break;
        case "connect":
            connect(data.src, data.dst, data.outlet || 0, data.inlet || 0);
            break;
        default:
            outlet(0, "error", "Unknown action: " + data.action);
    }
}

// Adds a new Max object of given type at (x, y), optionally with varname
function add_object(x, y, type, args, varname) {
    var newObj = this_patcher.newdefault(x, y, type, args);
    if (varname) {
        newObj.varname = varname;
    }
    outlet(0, "object_added", newObj.varname || newObj.id);
}

// Connects src_varname's outlet to dst_varname's inlet
function connect(src_varname, dst_varname, outlet_idx, inlet_idx) {
    var src = this_patcher.getnamed(src_varname);
    var dst = this_patcher.getnamed(dst_varname);
    if (src && dst) {
        this_patcher.connect(src, outlet_idx, dst, inlet_idx);
        outlet(0, "connected", src_varname, dst_varname);
    } else {
        outlet(0, "error", "Could not find source or destination object");
    }
}

// Optionally, add a function to return a list of all objects for resource discovery
function list_objects() {
    var objs = [];
    this_patcher.apply(function(obj) {
        if (obj.varname) {
            objs.push(obj.varname);
        }
        return true;
    });
    outlet(0, "object_list", JSON.stringify(objs));
}