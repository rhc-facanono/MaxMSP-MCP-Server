{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 9,
			"minor" : 0,
			"revision" : 2,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ 132.0, 159.0, 827.0, 757.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"filename" : "none",
					"id" : "obj-98",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 53.0, 343.0, 21.0, 22.0 ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0
					}
,
					"text" : "v8",
					"textfile" : 					{
						"text" : "autowatch=1;\n\nvar p = this.patcher\n\nfunction add_object(x, y, type, var_name, ...args) {\n    var new_obj = p.newdefault(x, y, type, args);\n    new_obj.varname = var_name;\n}\n\nfunction remove_object(var_name) {\n\tvar obj = p.getnamed(var_name);\n\tp.remove(obj);\n}\n\nfunction connect_objects(src_varname, outlet_idx, dst_varname, inlet_idx) {\n    var src = p.getnamed(src_varname);\n    var dst = p.getnamed(dst_varname);\n    p.connect(src, outlet_idx, dst, inlet_idx);\n}\n\nfunction disconnect_objects(src_varname, outlet_idx, dst_varname, inlet_idx) {\n\tvar src = p.getnamed(src_varname);\n    var dst = p.getnamed(dst_varname);\n\tp.disconnect(src, outlet_idx, dst, inlet_idx);\n}\n",
						"filename" : "none",
						"flags" : 0,
						"embed" : 1,
						"autowatch" : 1
					}

				}

			}
, 			{
				"box" : 				{
					"id" : "obj-85",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 53.0, 292.0, 66.0, 22.0 ],
					"text" : "string.tolist"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 53.0, 247.0, 65.0, 22.0 ],
					"text" : "route /mcp"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-1",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 53.0, 198.0, 97.0, 22.0 ],
					"text" : "udpreceive 5000"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-5", 0 ],
					"source" : [ "obj-1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-85", 0 ],
					"source" : [ "obj-5", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-98", 0 ],
					"source" : [ "obj-85", 0 ]
				}

			}
 ],
		"originid" : "pat-131",
		"dependency_cache" : [  ],
		"autosave" : 0
	}

}
