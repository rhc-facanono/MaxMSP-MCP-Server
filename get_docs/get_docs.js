inlets=1;
outlets=1;
autowatch = 1;

function get_help(){
	dict = max.getrefdict("cycle~").get("description");
	outlet(0,"dictionary", dict)
	} 
	