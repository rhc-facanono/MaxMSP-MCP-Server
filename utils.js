autowatch=1;

var p = this.patcher

function add_object(x, y, type, var_name, ...args) {
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
