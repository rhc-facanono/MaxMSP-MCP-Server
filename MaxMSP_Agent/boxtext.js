
autowatch = 1; // 1
inlets = 1; // Receive network messages here
outlets = 2; // For status, responses, etc.

function safe_parse_json(str) {
    try {
        return JSON.parse(str);
    } catch (e) {
        outlet(0, "error", "Invalid JSON: " + e.message);
        return null;
    }
}

function anything() {
    var a = arrayfromargs(messagename, arguments);
    switch (messagename) {
        case "add_boxtext":
            if (arguments.length < 1) {
                post("add_boxtext: no arguments\n");
                return;
            }
            add_boxtext(arguments[0]);
            break;
        default:
            outlet(1, messagename, ...arguments);
    }
	
}
function add_boxtext(data){
    // post(patcher_dict + "\n");
    var patcher_dict = safe_parse_json(data);
    var p = max.frontpatcher;

    patcher_dict.boxes.forEach(function (b) {
        var obj = p.getnamed(b.box.varname);
        if (obj) {
            b.box["text"] = obj.boxtext;
        }
    });

    outlet(1,JSON.stringify(patcher_dict, null, 2));
}


