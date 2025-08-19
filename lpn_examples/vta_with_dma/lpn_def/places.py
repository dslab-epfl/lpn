from lpnlang import Place, Transition, Token

pcompute2store = Place("pcompute2store")
pcompute2load = Place("pcompute2load")
pstore2compute = Place("pstore2compute")
pload2compute = Place("pload2compute")
pcompute_process = Place("pcompute_process");  
pload_process = Place("pload_process");  
pstore_process = Place("pstore_process");  
pcompute_cap = Place("pcompute_cap") 
pload_cap = Place("pload_cap") 
pstore_cap = Place("pstore_cap")
plaunch = Place("plaunch")
psReadCmd = Place("psReadCmd")
pnumInsn = Place("pnumInsn")
psDrain = Place("psDrain") 
pcontrol = Place("pcontrol")
pcontrol_prime = Place("pcontrol_prime")
pcompute_inst_q = Place("pcompute_inst_q")
pcompute_done = Place("pcompute_done")
pstore_inst_q = Place("pstore_inst_q")
pstore_done = Place("pstore_done")
pload_inst_q = Place("pload_inst_q")
pload_done = Place("pload_done")
