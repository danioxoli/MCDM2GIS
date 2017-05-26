import config


# WALKING/CYCLING/DRIVING WEIGHTS 
set_walk_w={"usage":1.00,"weight_param":1.0/config.limits['mat_wa']["max"]}
set_cycle_w={"usage":0.0,"weight_param":1.0/config.limits['mat_cy']["max"]}
set_drive_w={"usage":0.0,"weight_param":1.0/config.limits['mat_dr']["max"]}

w_walk=set_walk_w["usage"]*set_walk_w["weight_param"]/(set_walk_w["usage"]*set_walk_w["weight_param"]+set_cycle_w["usage"]*set_cycle_w["weight_param"]+set_drive_w["usage"]*set_drive_w["weight_param"])

w_cycle=set_cycle_w["usage"]*set_cycle_w["weight_param"]/(set_walk_w["usage"]*set_walk_w["weight_param"]+set_cycle_w["usage"]*set_cycle_w["weight_param"]+set_drive_w["usage"]*set_drive_w["weight_param"])

w_drive=set_drive_w["usage"]*set_drive_w["weight_param"]/(set_walk_w["usage"]*set_walk_w["weight_param"]+set_cycle_w["usage"]*set_cycle_w["weight_param"]+set_drive_w["usage"]*set_drive_w["weight_param"])

set_walk_w["w_walk"] = w_walk
set_cycle_w["w_cycle"] = w_cycle
set_drive_w["w_drive"] = w_drive

# SUB-CATEGORIES WEIGHTS


ATM = {"ATM":1.0,"hospital":9.0,"supermarket":9.0}
hospital = {"ATM":1.0/ATM["hospital"],"hospital":1.0,"supermarket":1.0}
supermarket = {"ATM":1.0/ATM["supermarket"],"hospital":1.0/hospital["supermarket"],"supermarket":1.0}
services = {"ATM":ATM, "hospital":hospital, "supermarket":supermarket}

train_metro = {"train_metro":1.0, "bus_stops":1.0/9.0}
bus_stops = {"train_metro":1.0/train_metro["bus_stops"], "bus_stops":1.0}
transport = {"train_metro":train_metro,"bus_stops":bus_stops}

parks = {"parks":1.0, "dog_parks":1.0, "green_areas":1.0}
dog_parks = {"parks":1.0/parks["dog_parks"], "dog_parks":1.0, "green_areas":1.0}
green_areas = {"parks":1.0/parks["green_areas"], "dog_parks":1.0/dog_parks["green_areas"], "green_areas":1.0}
nature = {"parks":parks, "dog_parks":dog_parks, "green_areas":green_areas}

# CATEGORIES WEIGHTS
cat_services = {"cat_services":1.0, "cat_transport":1.0, "cat_nature":9.0}
cat_transport = {"cat_services":1.0/cat_services["cat_transport"], "cat_transport":1.0, "cat_nature":9.0}
cat_nature = {"cat_services":1.0/cat_services["cat_nature"], "cat_transport":1.0/cat_transport["cat_nature"], "cat_nature":1.0}
categories = {"cat_services":cat_services, "cat_transport":cat_transport, "cat_nature":cat_nature}


### SALVARE DIZIONARI

