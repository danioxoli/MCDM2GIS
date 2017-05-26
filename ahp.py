import pandas as pd
import os
import numpy as np
import config

myfold = r"/home/monia/Desktop/TEST/"

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

train  = {"train ":1.0, "bus_stop":1.0/9.0}
bus_stop = {"train ":1.0/train ["bus_stop"], "bus_stop":1.0}
transport = {"train ":train ,"bus_stop":bus_stop}

parks = {"parks":1.0, "dog":1.0, "green":1.0}
dog = {"parks":1.0/parks["dog"], "dog":1.0, "green":1.0/1.0}
green = {"parks":1.0/parks["green"], "dog":1.0/dog["green"], "green":1.0}
nature = {"parks":parks, "dog":dog, "green":green}

# CATEGORIES WEIGHTS
cat_services = {"cat_services":1.0, "cat_transport":1.0, "cat_nature":9.0}
cat_transport = {"cat_services":1.0/cat_services["cat_transport"], "cat_transport":1.0, "cat_nature":9.0}
cat_nature = {"cat_services":1.0/cat_services["cat_nature"], "cat_transport":1.0/cat_transport["cat_nature"], "cat_nature":1.0}
categories = {"cat_services":cat_services, "cat_transport":cat_transport, "cat_nature":cat_nature}


##############################
keys=[]
#Get Categories and Sub-categories
#keys=[]#####MIRIAM ho aggiunto la lista 
for f in os.listdir(myfold+"categories"):
    keys.append(f)
    
keys.append('categories') # aggiungo all'elenco delle categorie "categories"
CR_list = {}
           
#CICLO PER RIEMPIRE LE MATRICI df_service, df_trasport, df_nature e df_categories
for x in keys:
    #Per creare delle variabili di variabili (ogni ciclo son diverse) uso global()
    #prende df_ ci aggiunge il valore della stringa x
    globals()['df_'+str(x)]= pd.DataFrame(index=globals()[str(x)].keys(),columns=globals()[str(x)].keys())
    
    for i in globals()[str(x)].keys():
        for j in globals()[str(x)].keys():
            globals()['df_'+str(x)][i][j] = globals()[str(x)][j][i]
    
    #Andando a utilizzare variabili di variabili, nel ciclo calcolano tutti i parametri per
    #le 3 categorie più quella globale
    # NORMALIZE WEIGHTS DATAFRAME    
    globals()['df_'+str(x)+'_norm']=globals()['df_'+str(x)].div(globals()['df_'+str(x)].sum(axis=0))#axis=0 --> somma colonne
           
    # COMPUTE SUM OF ROWS       
    globals()['df_'+str(x)+'_norm']["sum"] = globals()['df_'+str(x)+'_norm'].sum(axis=1)
    
    # COMPUTE WEIGHTS
    globals()['df_'+str(x)+'_norm']["W"] = globals()['df_'+str(x)+'_norm']["sum"].div(np.sum(globals()['df_'+str(x)+'_norm']["sum"],axis=0))
    
    # COMPUTE VALUES FOR CONSISTENCY CHECK
    globals()['df_'+str(x)+'_norm']["W'"]=np.nan
    for i in globals()[str(x)].keys():    
        globals()['df_'+str(x)+'_norm']["W'"][i] = globals()['df_'+str(x)].loc[i].dot(globals()['df_'+str(x)+'_norm']["W"])

    # COMPUTE PARAMETERS FOR CONSISTENCY CHECK
    globals()[str(x)+'_l_max'] = (sum(globals()['df_'+str(x)+'_norm']["W'"]/(globals()['df_'+str(x)+'_norm']["W"])))/len(globals()[str(x)].keys())
    globals()[str(x)+'_IC'] = (globals()[str(x)+'_l_max']-len(globals()[str(x)].keys()))/(len(globals()[str(x)].keys())-1)
    globals()[str(x)+'_CR'] = globals()[str(x)+'_IC']/config.conf_RI
           
    CR_list["{0}".format(x)] = globals()[str(x)+'_CR']
    

#CREATE FINAL WEIGHTS dizionario
df_final_weights={}
del keys[-1] #MIRIAM elimino l'ultimo elemento (categories)
for y in keys:
    #df_final_weights[y]={}
    for i in globals()[str(y)].keys():
        df_final_weights["{0}".format(i)] = globals()['df_'+str(y)+'_norm']["W"][i]*df_categories_norm["W"]["cat_"+y]

# salvare per poi caricare

f = open(myfold+"AHPWeights.py","w")
f.write("df_final_weights="+str(df_final_weights))
f.write("\n")
f.write("CR_list="+str(df_final_weights))
f.close()
