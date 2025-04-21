
autowatch = 1; // 1
inlets = 1; // Receive network messages here
outlets = 2; // For status, responses, etc.

var p = this.patcher
var obj_count = 0;
var boxes = [];
var lines = [];

function safe_parse_json(str) {
    try {
        return JSON.parse(str);
    } catch (e) {
        outlet(0, "error", "Invalid JSON: " + e.message);
        return null;
    }
}

function split_long_string(inString, maxLength) {
    var longString = inString.replace(/\s+/g, "");
    var result = [];
    for (var i = 0; i < longString.length; i += maxLength) {
        result.push(longString.substring(i, i + maxLength));
    }
    return result;
}

// Called when a message arrives at inlet 0 (from [udpreceive] or similar)
function anything() {
    var msg = arrayfromargs(messagename, arguments).join(" ");
    var data = safe_parse_json(msg);
    if (!data) return;

    switch (data.action) {
        case "fetch_test":
            if (data.request_id) {
                get_objects_in_patch(data.request_id);
            } else {
                outlet(0, "error", "Missing request_id for fetch_test");
            }
            break;
        case "get_objects_in_patch":
            if (data.request_id) {
                get_objects_in_patch(data.request_id);
            } else {
                outlet(0, "error", "Missing request_id for get_objects_in_patch");
            }
            break;
        case "get_objects_in_selected":
            if (data.request_id) {
                get_objects_in_selected(data.request_id);
            } else {
                outlet(0, "error", "Missing request_id for get_objects_in_selected");
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

// function fetch_test(request_id) {
// 	var str = get_patcher_objects(request_id)
// 	//outlet(1, request_id)
// }

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

// ========================================
// fetch request:

function get_objects_in_patch(request_id) {
    
	var p = this.patcher
    obj_count = 0;
    boxes = [];
    lines = [];

    p.applydeep(collect_objects);
    var patcher_dict = {};
    patcher_dict["boxes"] = boxes;
    patcher_dict["lines"] = lines;

    // use these if no v8:
    // var results = {"request_id": request_id, "results": patcher_dict}
    // outlet(1, "response", split_long_string(JSON.stringify(results, null, 2), 2000));

    // use this if has v8:
    outlet(1, "add_boxtext", request_id, JSON.stringify(patcher_dict, null, 0));
}

function get_objects_in_selected(request_id) {
    
	var p = this.patcher
    obj_count = 0;
    boxes = [];
    lines = [];

    p.applydeepif(collect_objects, function (obj) {
        return obj.selected;
    });
    var patcher_dict = {};
    patcher_dict["boxes"] = boxes;
    patcher_dict["lines"] = lines;

    // use these if no v8:
    // var results = {"request_id": request_id, "results": patcher_dict}
    // outlet(1, "response", split_long_string(JSON.stringify(results, null, 2), 2000));

    // use this if has v8:
    outlet(1, "add_boxtext", request_id, JSON.stringify(patcher_dict, null, 0));
}

function collect_objects(obj) {
    //var keys = Object.keys(obj.varname);
    //post(typeof obj.varname + "\n");
    if (obj.varname.substring(0, 8) == "maxmcpid"){
        return;
    }
    if (!obj.varname){
        obj.varname = "obj-" + obj_count;
    }
    obj_count+=1;

    var outputs = obj.patchcords.outputs;
    if (outputs.length){
        for (var i = 0; i < outputs.length; i++) {
            lines.push({patchline: {
                source: [obj.varname, outputs[i].srcoutlet],
                destination: [outputs[i].dstobject.varname, outputs[i].dstinlet]
            }})
        }
    }
    var attrnames = obj.getattrnames();
    var attr = {};
    if (attrnames.length){
        for (var i = 0; i < attrnames.length; i++) {
            var name = attrnames[i];
            var value = obj.getattr(name);
            attr[name] = value;
        }
    }
    boxes.push({box:{
        maxclass: obj.maxclass,
        varname: obj.varname,
        patching_rect: obj.rect,
        // numinlets: obj.patchcords.inputs.length,
        // numoutputs: obj.patchcords.outputs.length,
        // attributes: attr,
    }})
}




// ========================================
// for debugging use only:


function remove_varname() {
    // for debugging
    // remove all objects' varname
    var p = max.frontpatcher;
    p.applydeep(function (obj) {
        obj.varname = "";
    });
}

function assign_mcp_identifier_to_all_objects() {
    // for debugging
    // remove all objects' varname
	var idx = 0
    var p = max.frontpatcher;
    p.applydeep(function (obj) {
        obj.varname = "maxmcpid-"+idx;
		idx += 1
    });
}


function print_varname() {
    // for debugging
    // remove all objects' varname
    var p = max.frontpatcher;
    p.applydeep(function (obj) {
        post(obj.varname)
    });
}

function parsed_patcher() {
	if (max.frontpatcher.filepath == ""){
		post(NOT_SAVED);
		return;
	}
	var lines = new String();
    var patcher_file = new File(max.frontpatcher.filepath);
    //post("max.frontpatcher.filepath: " + patcher_file + "\n");

	while (patcher_file.position != patcher_file.eof){
		lines += patcher_file.readline();
	}
	patcher_file.close();

    var parsed_patcher = JSON.parse(lines);
	// post(JSON.stringify(parsed_patcher));
}
