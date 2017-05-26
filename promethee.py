# -*- coding: utf-8 -*-

import pandas as pd
import config 
from RoutingData import tree
from AHPWeights import df_final_weights
import settings

# Load object
myfold = r"/home/monia/Desktop/TEST/"


# For each file create matrix and extract NW

def GetMatrixIndex(obj,cat,subcat):
    ind=[]
    x = obj[cat][subcat].keys()[0]
    for l in range(0,len(obj[cat][subcat][x])):
        ind.append(obj[cat][subcat][x][l][0])
    return ind
    
        
def GetNW(obj,cat,subcat,modality,inde):     
    matrix = pd.DataFrame(index=inde,columns=['a','b','c','d'])
    for line in range(0,len(inde)):
        matrix['a'][line]=obj[cat][subcat][modality][line][1]
        matrix['b'][line]=obj[cat][subcat][modality][line][2]
        matrix['c'][line]=obj[cat][subcat][modality][line][3]
        matrix['d'][line]=obj[cat][subcat][modality][line][4]
    return matrix
            

dict_matrix = {}
for f in tree.keys():
    for item in tree[f].keys():
        dict_matrix[item] = {} 
        ind=GetMatrixIndex(tree,f,item)
        mat_cy = GetNW(tree,f,item,'cy.csv',ind)
        dict_matrix[item]['mat_cy']=mat_cy
        mat_dr = GetNW(tree,f,item,'dr.csv',ind)
        dict_matrix[item]['mat_dr']=mat_dr
        mat_wa = GetNW(tree,f,item,'wa.csv',ind)
        dict_matrix[item]['mat_wa']=mat_wa
        

dict_matrix_norm = {}   
for i in dict_matrix.keys():
    dict_matrix_norm[i] = {} 
    for y in dict_matrix[i].keys():
        dict_matrix_norm[i][y]=pd.DataFrame(index=ind,columns=['a','b','c','d'])
        for col in dict_matrix[i][y]:
            for row in ind:
                if col !='d':
                    if dict_matrix[i][y][col][row] < config.limits[y]['min']:
                        dict_matrix_norm[i][y][col][row] = 1
                    elif  dict_matrix[i][y][col][row] > config.limits[y]['max']:
                        dict_matrix_norm[i][y][col][row] = 0
                    else:
                        dict_matrix_norm[i][y][col][row] = (max(dict_matrix[i][y][col])-dict_matrix[i][y][col][row])/(max(dict_matrix[i][y][col])-min(dict_matrix[i][y][col]))
                else:
                    dict_matrix_norm[i][y][col][row] = (max(dict_matrix[i][y][col])-dict_matrix[i][y][col][row])/(max(dict_matrix[i][y][col])-min(dict_matrix[i][y][col]))
         
### FINE PARTE STATICA (VARIA SOLO SE CAMBIANO CATEGORIE O CONFIG)   

dict_final_matrix = {}

for i in dict_matrix_norm.keys():
    final_matrix = pd.DataFrame(index=ind,columns=['a','b','c','d']) 
    dict_final_matrix[i] = final_matrix
    for col in final_matrix:
        for row in ind: ### NON USAGE
           final_matrix[col][row] = dict_matrix_norm[i]['mat_cy'][col][row]*settings.set_cycle_w['usage']+dict_matrix_norm[i]['mat_dr'][col][row]*settings.set_drive_w['usage']+dict_matrix_norm[i]['mat_wa'][col][row]*settings.set_walk_w['usage']
           
pixel_weights = pd.DataFrame(index=ind,columns=dict_matrix_norm.keys())

for i in dict_final_matrix.keys():
    for row in ind:
        pixel_weights[i][row] = dict_final_matrix[i]['a'][row]*config.conf_w_to['nearest']+dict_final_matrix[i]['b'][row]*config.conf_w_to['second']+dict_final_matrix[i]['c'][row]*config.conf_w_to['third']+dict_final_matrix[i]['d'][row]*config.conf_w_to['sum']
           

p_diff = {} 

for pixel in ind:
    inde_list = list(ind)
    h = inde_list.index(pixel)
    del inde_list[h]
    p_diff[pixel] = pd.DataFrame(index=inde_list,columns=dict_matrix_norm.keys()) 


    for s in dict_matrix_norm.keys():
        count=0
        for row in ind:                
            if row!=pixel:
                val = pixel_weights[s][pixel]-pixel_weights[s][row]
                if val<0:
                    val=0
                else:
                    if val < config.prom_min:
                        val=0
                    elif val > config.prom_max:
                        val=1
                    else:
                        val = (val-config.prom_min)/(config.prom_max-config.prom_min)
                p_diff[pixel][s][count]=val
                count+=1
                
# caricare df_weights da AHP 

sik_dict = {} # creiamo un dizionario che contiene una tabella per ogni ID
for pixel in ind: # gira i dizionari da ID1 a ID20
    # crea una lista con tutti i valori di ID tranne quello della corrispettiva tabella 
    #(es tabella ID1 la lista comprende ID2, ID3,..., ID20)
    inde_list = list(ind)
    h = inde_list.index(pixel)
    del inde_list[h]
    sik_dict[pixel] = pd.DataFrame(index=inde_list,columns=['Sik'])#crea una tabella con prima colonna uguale a inde_list, e la seconda colonna chiamata Sik

   
    for row in range(0,len(ind)-1): #gira un contatore da 0 a 18
        serv={} #memorizzo i vari prodotti dei diversi servizi in un dizionario, lo annullo a ogni iterazione
        for s in dict_matrix_norm.keys():# gira i servizi 
            serv[s]=p_diff[pixel][s][row]*df_final_weights[s]
        service=sum(serv.values())#somma tutti i valori numerici nel dizionario serv
        sik_dict[pixel]['Sik'][row]=service
        

phi = pd.DataFrame(index=ind,columns=['plus','minus','phi2','phiN'])
#Phi plus somma verticalmente i valori di ogni tabella IDesima
for pixel in ind: 
    phi['plus'][pixel]=sik_dict[pixel]['Sik'].sum() #Somma verticalmente la colonna Sik
 
#Phi minus somma tutti i valori che sono relativi a un determinato pixel
#nel caso ID1 memorizzerà il valore nella tabella ID2 nella riga ID2 rispetto a ID1 più il valore nella tabella ID3 nella riga ID3 rispetto a ID2 etc.
phi_minus={}
for pixel in ind: #prendi l'ID da cercare   
    phi_minus[pixel]=0
    for i in ind: #gira sulle tabelle ID1...ID20
        for j in range(0,len(ind)-1): #gira su un contatore che va da 0 a 19
            if sik_dict[i].index[j]==pixel: #se il dizionario IDesimo ha un indice j uguale a ID
                phi_minus[pixel]=sik_dict[i]["Sik"][j]+phi_minus[pixel] #aggiorna la lista con la somma del valore phi minus

#La lista phi_minus non è ordinata, per inserirla nella tabella phi bisona accertarsi che
#gli indici della tabella phi siano uguali a quelli di phi_minus
for pixel in ind:
        phi['minus'][pixel]=phi_minus[pixel]

#La colonna phi è la differenza tra le prime due   
phi['phi2']=phi['plus']-phi['minus']

#Memorizzo il valore massimo e minimo
phi_min=min(phi['phi2'])
phi_max=max(phi['phi2'])

#Riempie l'ultima colonna con il valore di phi normalizzato
phi['phiN']=(phi['phi2']-phi_min)/(phi_max-phi_min)
    














