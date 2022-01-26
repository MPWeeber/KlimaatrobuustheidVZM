# '''
# Do Postprocessing of scenarios



# '''

import os
import sys
import pandas
from pandas.api.types import CategoricalDtype
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('./_storage')
import d3d


#Oppervlakten
#Location | Oppervlakte in m2
I_oppv_m2    = 15000000.0
II_oppv_m2   =  8000000.0
III_oppv_m2  =  6500000.0
IV_oppv_m2   = 14000000.0
V_oppv_m2    =  1750000.0
VI_oppv_m2   =  1750000.0
VII_oppv_m2  =  8500000.0
VIII_oppv_m2 =  2500000.0
IX_oppv_m2   =  1500000.0
X_oppv_m2    =   500000.0

#Diepte bakjes
#Locatie        | Diepte in m vanaf NAP
I_diepte_m    =	 5.0
II_diepte_m   =  5.0
III_diepte_m  =  5.0
IV_diepte_m   =  5.0
V_diepte_m    =  7.0
VI_diepte_m   =  7.0
VII_diepte_m  = 10.0
VIII_diepte_m =	 5.0
IX_diepte_m   =	 4.0
X_diepte_m    =  7.0

#Verkrijg scenarios van 1_runall
runall = open("1_runall.bat",'r')
runall_lines = runall.readlines()
runall_lines = runall_lines[1:] #sla eerste lijn over voor comments

scenarios = []
for lines in runall_lines:
	scenarios.append(int(lines.split(" ")[2]))

#make file to store max chloride

postproces_max_waterstand_bestand = [["Scen_NR",'I. Krammer-Volkerak Oost', 'II. Krammer-Volkerak Midden',\
				'III. Krammer-Volkerak Ingang Eendracht', 'IV. Krammer-Volkerak West ', 'V. Eendracht Noord',\
				'VI. Eendracht Zuid', 'VII. Zoommeer', 'VIII. Zoommeer Zuid', 'IX. Bathse Spuikanaal', 'X. Voorhaven Kramersluizen',\
				'Volkerak-Zoommeer']]
postproces_max_waterstand_bestand.append(["NR","m NAP","m NAP","m NAP","m NAP","m NAP","m NAP","m NAP","m NAP","m NAP","m NAP"])

postproces_min_waterstand_bestand = [["Scen_NR",'I. Krammer-Volkerak Oost', 'II. Krammer-Volkerak Midden',\
				'III. Krammer-Volkerak Ingang Eendracht', 'IV. Krammer-Volkerak West ', 'V. Eendracht Noord',\
				'VI. Eendracht Zuid', 'VII. Zoommeer', 'VIII. Zoommeer Zuid', 'IX. Bathse Spuikanaal', 'X. Voorhaven Kramersluizen',\
				'Volkerak-Zoommeer']]
postproces_min_waterstand_bestand.append(["NR","m NAP","m NAP","m NAP","m NAP","m NAP","m NAP","m NAP","m NAP","m NAP","m NAP"])

postproces_chloride_bestand = [["Scen_NR",'I. Krammer-Volkerak Oost', 'II. Krammer-Volkerak Midden',\
				'III. Krammer-Volkerak Ingang Eendracht', 'IV. Krammer-Volkerak West ', 'V. Eendracht Noord',\
				'VI. Eendracht Zuid', 'VII. Zoommeer', 'VIII. Zoommeer Zuid', 'IX. Bathse Spuikanaal', 'X. Voorhaven Kramersluizen',\
				'Volkerak-Zoommeer']]
postproces_chloride_bestand.append(["NR","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l"])

postproces_chloride_groei_bestand = [["Scen_NR",'I. Krammer-Volkerak Oost', 'II. Krammer-Volkerak Midden',\
				'III. Krammer-Volkerak Ingang Eendracht', 'IV. Krammer-Volkerak West ', 'V. Eendracht Noord',\
				'VI. Eendracht Zuid', 'VII. Zoommeer', 'VIII. Zoommeer Zuid', 'IX. Bathse Spuikanaal', 'X. Voorhaven Kramersluizen',\
				'Volkerak-Zoommeer']]
postproces_chloride_groei_bestand.append(["NR","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l","g CL/l"])


postproces_chloride_groei_dagen_bestand = [["Scen_NR",'I. Krammer-Volkerak Oost', 'II. Krammer-Volkerak Midden',\
				'III. Krammer-Volkerak Ingang Eendracht', 'IV. Krammer-Volkerak West ', 'V. Eendracht Noord',\
				'VI. Eendracht Zuid', 'VII. Zoommeer', 'VIII. Zoommeer Zuid', 'IX. Bathse Spuikanaal', 'X. Voorhaven Kramersluizen',\
				'Volkerak-Zoommeer']]
postproces_chloride_groei_dagen_bestand.append(["NR","dagen","dagen","dagen","dagen","dagen","dagen","dagen","dagen","dagen","dagen"])


#Loop over alle berekende scenarios
for scenario in scenarios: 

	print("Scenario : " + str(scenario))

	#Read Waterstands file
	invoerbestand_path = "./output/"+ str(scenario) +"_scenario/output/Invoer_bakjesmodel_VZM.csv"
	df_invoerbestand = pandas.read_csv(invoerbestand_path, sep = ";", skiprows = [1])

	volumesbestand_path = "./output/"+ str(scenario) +"_scenario/output/Waterbalans_Volumes_bakjes_bakjesmodel_VZM.csv"
	df_volumesbestand = pandas.read_csv(volumesbestand_path, sep = ";", skiprows = [1])
	
	#handmatig berekend vanuit de Volumes
	df_volumesbestand["ws_I"] = (df_volumesbestand["I"].astype(float) - (I_oppv_m2 * I_diepte_m)) / float(I_oppv_m2)
	df_volumesbestand["ws_II"] = (df_volumesbestand["II"].astype(float) - (II_oppv_m2 * II_diepte_m)) / float(II_oppv_m2)
	df_volumesbestand["ws_III"] = (df_volumesbestand["III"].astype(float) - (III_oppv_m2 * III_diepte_m)) / float(III_oppv_m2)
	df_volumesbestand["ws_IV"] = (df_volumesbestand["IV"].astype(float) - (IV_oppv_m2 * IV_diepte_m)) / float(IV_oppv_m2)
	df_volumesbestand["ws_V"] = (df_volumesbestand["V"].astype(float) - (V_oppv_m2 * V_diepte_m)) / float(V_oppv_m2)
	df_volumesbestand["ws_VI"] = (df_volumesbestand["VI"].astype(float) - (VI_oppv_m2 * VI_diepte_m)) / float(VI_oppv_m2)
	df_volumesbestand["ws_VII"] = (df_volumesbestand["VII"].astype(float) - (VII_oppv_m2 * VII_diepte_m)) / float(VII_oppv_m2)
	df_volumesbestand["ws_VIII"] = (df_volumesbestand["VIII"].astype(float) - (VIII_oppv_m2 * VIII_diepte_m)) / float(VIII_oppv_m2)
	df_volumesbestand["ws_IX"] = (df_volumesbestand["IX"].astype(float) - (IX_oppv_m2 * IX_diepte_m)) / float(IX_oppv_m2)
	df_volumesbestand["ws_X"] = (df_volumesbestand["X"].astype(float) - (X_oppv_m2 * X_diepte_m)) / float(X_oppv_m2)



	#Read HIS file
	his_file_path = "./output/"+ str(scenario) +"_scenario/Zout_Delwaq/delwaq.his"
	delwaq_his_output = d3d.DelwaqHisFile(his_file_path)
	#print(delwaq_his_output.__str__())
	#print(delwaq_his_output._notot)
	#print(delwaq_his_output._nodump)
	#print(delwaq_his_output._duname)
	#print(delwaq_his_output._duindx)
	#print(delwaq_his_output._syname)

	itimes = list(range(366,730+1))

	subs = ['Continuity',\
			'Chloride']


	areas = ['I. Krammer-Volkerak',\
				'II. Krammer-Volkerak',\
				'III. Krammer-Volkera',\
				'IV. Krammer-Volkerak',\
				'V. Eendracht Noord',\
				'VI. Eendracht Zuid',\
				'VII. Zoommeer',\
				'VIII. Zoommeer Zuid',\
				'IX. Bathse Spuikanaa',\
				'X. Voorhaven Kramers',\
				'Volkerak-Zoommeer']                     

	#get data 2019
	delwaq_his_2019_output = delwaq_his_output.get( itimes = itimes, subs = subs , areas = areas )
	#print(delwaq_his_2019_output.shape)  # 365 timesteps, 2 substances, 11 locations

	Max_I_waterstand_m_NAP     =   max(df_volumesbestand["ws_I"].values.tolist()) 
	Max_II_waterstand_m_NAP    =   max(df_volumesbestand["ws_II"].values.tolist())
	Max_III_waterstand_m_NAP   =   max(df_volumesbestand["ws_III"].values.tolist())
	Max_IV_waterstand_m_NAP    =   max(df_volumesbestand["ws_IV"].values.tolist())
	Max_V_waterstand_m_NAP     =   max(df_volumesbestand["ws_V"].values.tolist())
	Max_VI_waterstand_m_NAP    =   max(df_volumesbestand["ws_VI"].values.tolist())
	Max_VII_waterstand_m_NAP   =   max(df_volumesbestand["ws_VII"].values.tolist())
	Max_VIII_waterstand_m_NAP  =   max(df_volumesbestand["ws_VIII"].values.tolist())
	Max_IX_waterstand_m_NAP    =   max(df_volumesbestand["ws_IX"].values.tolist())
	Max_X_waterstand_m_NAP     =   max(df_volumesbestand["ws_X"].values.tolist())
	Max_VZM_waterstand_m_NAP   =   max(df_invoerbestand["Waterstand werkelijk"].values.tolist())

	Min_I_waterstand_m_NAP     =   min(df_volumesbestand["ws_I"].values.tolist()) 
	Min_II_waterstand_m_NAP    =   min(df_volumesbestand["ws_II"].values.tolist())
	Min_III_waterstand_m_NAP   =   min(df_volumesbestand["ws_III"].values.tolist())
	Min_IV_waterstand_m_NAP    =   min(df_volumesbestand["ws_IV"].values.tolist())
	Min_V_waterstand_m_NAP     =   min(df_volumesbestand["ws_V"].values.tolist())
	Min_VI_waterstand_m_NAP    =   min(df_volumesbestand["ws_VI"].values.tolist())
	Min_VII_waterstand_m_NAP   =   min(df_volumesbestand["ws_VII"].values.tolist())
	Min_VIII_waterstand_m_NAP  =   min(df_volumesbestand["ws_VIII"].values.tolist())
	Min_IX_waterstand_m_NAP    =   min(df_volumesbestand["ws_IX"].values.tolist())
	Min_X_waterstand_m_NAP     =   min(df_volumesbestand["ws_X"].values.tolist())
	Min_VZM_waterstand_m_NAP   =   min(df_invoerbestand["Waterstand werkelijk"].values.tolist())

	Max_I_g_chloride_per_liter     =   max(delwaq_his_2019_output[:,1,0]) 
	Max_II_g_chloride_per_liter    =   max(delwaq_his_2019_output[:,1,1])
	Max_III_g_chloride_per_liter   =   max(delwaq_his_2019_output[:,1,2])
	Max_IV_g_chloride_per_liter    =   max(delwaq_his_2019_output[:,1,3])
	Max_V_g_chloride_per_liter     =   max(delwaq_his_2019_output[:,1,4])
	Max_VI_g_chloride_per_liter    =   max(delwaq_his_2019_output[:,1,5])
	Max_VII_g_chloride_per_liter   =   max(delwaq_his_2019_output[:,1,6])
	Max_VIII_g_chloride_per_liter  =   max(delwaq_his_2019_output[:,1,7])
	Max_IX_g_chloride_per_liter    =   max(delwaq_his_2019_output[:,1,8])
	Max_X_g_chloride_per_liter     =   max(delwaq_his_2019_output[:,1,9])
	Max_VZM_g_chloride_per_liter   =   max(delwaq_his_2019_output[:,1,10])

	#groeiseizoen is gedefineerd als 15 maart - 15 september (dag 74 - 258 in een niet schrikkeljaar)
	Max_groei_I_g_chloride_per_liter     =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,0]) 
	Max_groei_II_g_chloride_per_liter    =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,1])
	Max_groei_III_g_chloride_per_liter   =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,2])
	Max_groei_IV_g_chloride_per_liter    =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,3])
	Max_groei_V_g_chloride_per_liter     =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,4])
	Max_groei_VI_g_chloride_per_liter    =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,5])
	Max_groei_VII_g_chloride_per_liter   =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,6])
	Max_groei_VIII_g_chloride_per_liter  =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,7])
	Max_groei_IX_g_chloride_per_liter    =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,8])
	Max_groei_X_g_chloride_per_liter     =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,9])
	Max_groei_VZM_g_chloride_per_liter   =   max(delwaq_his_2019_output[list(range(74-1,258-1)),1,10])

	#dagen in groeiseizoen hoer dan 450 CL mg/l
	Max_groei_dagen_I_g_chloride_per_liter     =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,0]  > 450.0 ) 
	Max_groei_dagen_II_g_chloride_per_liter    =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,1]  > 450.0 )
	Max_groei_dagen_III_g_chloride_per_liter   =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,2]  > 450.0 )
	Max_groei_dagen_IV_g_chloride_per_liter    =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,3]  > 450.0 )
	Max_groei_dagen_V_g_chloride_per_liter     =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,4]  > 450.0 )
	Max_groei_dagen_VI_g_chloride_per_liter    =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,5]  > 450.0 )
	Max_groei_dagen_VII_g_chloride_per_liter   =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,6]  > 450.0 )
	Max_groei_dagen_VIII_g_chloride_per_liter  =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,7]  > 450.0 )
	Max_groei_dagen_IX_g_chloride_per_liter    =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,8]  > 450.0 )
	Max_groei_dagen_X_g_chloride_per_liter     =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,9]  > 450.0 )
	Max_groei_dagen_VZM_g_chloride_per_liter   =   sum(delwaq_his_2019_output[list(range(74-1,258-1)),1,10] > 450.0 )


	#Voeg de Maximale waterstand toe aan het overzichtsbestand
	postproces_max_waterstand_bestand.append([str(scenario), str(Max_I_waterstand_m_NAP), str(Max_II_waterstand_m_NAP),\
		str(Max_III_waterstand_m_NAP), str(Max_IV_waterstand_m_NAP), str(Max_V_waterstand_m_NAP), str(Max_VI_waterstand_m_NAP),\
		str(Max_VII_waterstand_m_NAP), str(Max_VIII_waterstand_m_NAP), str(Max_IX_waterstand_m_NAP), str(Max_X_waterstand_m_NAP),\
		str(Max_VZM_waterstand_m_NAP)])

	#Voeg de Minimale waterstand toe aan het overzichtsbestand
	postproces_min_waterstand_bestand.append([str(scenario), str(Min_I_waterstand_m_NAP), str(Min_II_waterstand_m_NAP),\
		str(Min_III_waterstand_m_NAP), str(Min_IV_waterstand_m_NAP), str(Min_V_waterstand_m_NAP), str(Min_VI_waterstand_m_NAP),\
		str(Min_VII_waterstand_m_NAP), str(Min_VIII_waterstand_m_NAP), str(Min_IX_waterstand_m_NAP), str(Min_X_waterstand_m_NAP),\
		str(Min_VZM_waterstand_m_NAP)])

	#Voeg de Maxmale chloride concentraties toe aan het overzichtsbestand
	postproces_chloride_bestand.append([str(scenario), str(Max_I_g_chloride_per_liter), str(Max_II_g_chloride_per_liter),\
		str(Max_III_g_chloride_per_liter), str(Max_IV_g_chloride_per_liter), str(Max_V_g_chloride_per_liter), str(Max_VI_g_chloride_per_liter),\
		str(Max_VII_g_chloride_per_liter), str(Max_VIII_g_chloride_per_liter), str(Max_IX_g_chloride_per_liter), str(Max_X_g_chloride_per_liter),\
		str(Max_VZM_g_chloride_per_liter)])

	#Voeg de Maxmale chloride concentraties groeiseizoen toe aan het overzichtsbestand
	postproces_chloride_groei_bestand.append([str(scenario), str(Max_groei_I_g_chloride_per_liter), str(Max_groei_II_g_chloride_per_liter),\
		str(Max_groei_III_g_chloride_per_liter), str(Max_groei_IV_g_chloride_per_liter), str(Max_groei_V_g_chloride_per_liter), str(Max_groei_VI_g_chloride_per_liter),\
		str(Max_groei_VII_g_chloride_per_liter), str(Max_groei_VIII_g_chloride_per_liter), str(Max_groei_IX_g_chloride_per_liter), str(Max_groei_X_g_chloride_per_liter),\
		str(Max_groei_VZM_g_chloride_per_liter)])

	#Voeg de dagen boven 450 mg/l chloride concentraties groeiseizoen toe aan het overzichtsbestand
	postproces_chloride_groei_dagen_bestand.append([str(scenario), str(Max_groei_dagen_I_g_chloride_per_liter), str(Max_groei_dagen_II_g_chloride_per_liter),\
		str(Max_groei_dagen_III_g_chloride_per_liter), str(Max_groei_dagen_IV_g_chloride_per_liter), str(Max_groei_dagen_V_g_chloride_per_liter), str(Max_groei_dagen_VI_g_chloride_per_liter),\
		str(Max_groei_dagen_VII_g_chloride_per_liter), str(Max_groei_dagen_VIII_g_chloride_per_liter), str(Max_groei_dagen_IX_g_chloride_per_liter), str(Max_groei_dagen_X_g_chloride_per_liter),\
		str(Max_groei_dagen_VZM_g_chloride_per_liter)])


#Schrijf het bestand weg

postproces_max_waterstand_bestand_file =  open("overzicht_resultaat/resultaat_maximale_waterstand_bakjes.csv","w")
postproces_max_waterstand_bestand_file.writelines("%s\n" % ";".join(line) for line in postproces_max_waterstand_bestand)
postproces_max_waterstand_bestand_file.close()

postproces_min_waterstand_bestand_file =  open("overzicht_resultaat/resultaat_minimale_waterstand_bakjes.csv","w")
postproces_min_waterstand_bestand_file.writelines("%s\n" % ";".join(line) for line in postproces_min_waterstand_bestand)
postproces_min_waterstand_bestand_file.close()

postproces_chloride_bestand_file =  open("overzicht_resultaat/resultaat_maximale_chloride_bakjes.csv","w")
postproces_chloride_bestand_file.writelines("%s\n" % ";".join(line) for line in postproces_chloride_bestand)
postproces_chloride_bestand_file.close()

postproces_chloride_groei_bestand_file =  open("overzicht_resultaat/resultaat_maximale_chloride_groeiseizoen_bakjes.csv","w")
postproces_chloride_groei_bestand_file.writelines("%s\n" % ";".join(line) for line in postproces_chloride_groei_bestand)
postproces_chloride_groei_bestand_file.close()

postproces_chloride_groei_dagen_bestand_file =  open("overzicht_resultaat/resultaat_dagen_chloride_boven_450CLmgL_groeiseizoen_bakjes.csv","w")
postproces_chloride_groei_dagen_bestand_file.writelines("%s\n" % ";".join(line) for line in postproces_chloride_groei_dagen_bestand)
postproces_chloride_groei_dagen_bestand_file.close()

# Start plotten

#Bind resultaat en scenario input
scenario_input = pandas.read_csv("scenario_overview.csv", sep = ";")
scenario_columns = scenario_input.columns[1:]


#maak volgorde van categorieen
#pas de volgorde toe op de data
scenario_input["1_volkeraksluizen"] = pandas.Categorical(scenario_input["1_volkeraksluizen"], categories= ["1_continue_15m3s","3_continue_25m3s","4_continue_25m3s_winterdoorspoeling",\
	"5_continue_40m3s"], ordered = True)
scenario_input["2_neerslag"] = pandas.Categorical(scenario_input["2_neerslag"], categories= ["1_KNMI_neerslag_geen_scenario",\
						"7_KNMI_neerslag_geen_scenario_2018","8_KNMI_neerslag_vlak_2050_2018","9_KNMI_neerslag_extreem_2085_2018"], ordered = True)
scenario_input["3_krammersluizen"] = pandas.Categorical(scenario_input["3_krammersluizen"], categories= ["1_operatie_krammersluizen_met_zss_0cm", "2_operatie_krammersluizen_met_zss_10cm",\
	"3_operatie_krammersluizen_met_zss_20cm", "4_operatie_krammersluizen_met_zss_30cm", "5_operatie_krammersluizen_met_zss_40cm", "6_operatie_krammersluizen_met_zss_50cm",\
	"7_operatie_krammersluizen_met_zss_60cm", "8_operatie_krammersluizen_met_zss_70cm", "9_operatie_krammersluizen_met_zss_80cm", "10_operatie_krammersluizen_met_zss_90cm",\
	"11_operatie_krammersluizen_met_zss_100cm"], ordered = True)
scenario_input["4_bergsediepsluis"] = pandas.Categorical(scenario_input["4_bergsediepsluis"], categories= ["1_standaard_operatie_bergsediepsluis"], ordered = True)
scenario_input["5_kreekraksluis"] = pandas.Categorical(scenario_input["5_kreekraksluis"], categories= ["1_standaard_operatie_kreekraksluis"], ordered = True)
scenario_input["6_verdamping"] = pandas.Categorical(scenario_input["6_verdamping"], categories= ["1_verdamping_wilhelminadorp2003", "2_verdamping_GilzeRijen2018"], ordered = True)
scenario_input["7_kwel"] = pandas.Categorical(scenario_input["7_kwel"], categories= ["1_standaard_kwel_3kgs","2_scenario_kwel_6kgs"], ordered = True)
scenario_input["8a_watervraag_hollandse_delta"] = pandas.Categorical(scenario_input["8a_watervraag_hollandse_delta"] ,categories= ["1_10proc_zomer_watervraag_hollandse_delta"], ordered = True)
scenario_input["8b_watervraag_schelde_stromen"] = pandas.Categorical(scenario_input["8b_watervraag_schelde_stromen"], categories= ["1_10proc_zomer_watervraag_schelde_stromen"], ordered = True)
scenario_input["8c_watervraag_brabantse_delta"] = pandas.Categorical(scenario_input["8c_watervraag_brabantse_delta"], categories= ["1_10proc_zomer_watervraag_brabantse_delta"], ordered = True)
scenario_input["9a_Dintel"] = pandas.Categorical(scenario_input["9a_Dintel"], categories= ["1_afvoer_2017_Dintelsas","4_afvoer_2018_Dintelsas","5_afvoer_2018_Dintelsas_2050_RV",\
	"6_afvoer_2018_Dintelsas_2085_RV"], ordered = True)
scenario_input["9b_Steenbergse_Vliet"] = pandas.Categorical(scenario_input["9b_Steenbergse_Vliet"], categories= ["1_afvoer_2017_Benedensas","4_afvoer_2018_Benedensas",\
	"5_afvoer_2018_Benedensas_2050", "6_afvoer_2018_Benedensas_2085"], ordered = True)
scenario_input["10_bathse_spuisluis"] = pandas.Categorical(scenario_input["10_bathse_spuisluis"], categories= ["1_standaard_beheer"], ordered = True)
scenario_input["A_zeespiegelstijging"] = pandas.Categorical(scenario_input["A_zeespiegelstijging"], categories= ["1_waterstand_bath_2003","2_waterstand_bath_2003_plus_10_cm",\
	"3_waterstand_bath_2003_plus_20_cm", "4_waterstand_bath_2003_plus_30_cm", "5_waterstand_bath_2003_plus_40_cm",\
	"6_waterstand_bath_2003_plus_50_cm", "7_waterstand_bath_2003_plus_60_cm", "8_waterstand_bath_2003_plus_70_cm",\
	"9_waterstand_bath_2003_plus_80_cm", "10_waterstand_bath_2003_plus_90_cm", "11_waterstand_bath_2003_plus_100_cm"], ordered = True)
scenario_input["B_inlaatstop_volkeraksluizen"] = pandas.Categorical(scenario_input["B_inlaatstop_volkeraksluizen"], categories= ["1_inlaat_continue","2_inlaatstop_volkeraksluizen"], ordered = True)
scenario_input["C1_waterstand_VZM_lowerlimit"] = pandas.Categorical(scenario_input["C1_waterstand_VZM_lowerlimit"], categories= ["1_continue_min10cmNAP", "2_peiltrap_gemiddeld"], ordered = True)
scenario_input["C2_waterstand_VZM_upperlimit"] = pandas.Categorical(scenario_input["C2_waterstand_VZM_upperlimit"], categories= ["1_continue_plus15cmNAP"], ordered = True)

#Lees postproces bestanden weer in
df_postproces_maximale_waterstand_bestand = pandas.read_csv("overzicht_resultaat/resultaat_maximale_waterstand_bakjes.csv",sep = ";", skiprows = [1])
df_postproces_maximale_waterstand_bestand['Scen_NR'] = df_postproces_maximale_waterstand_bestand['Scen_NR'].astype(int)

df_postproces_minimale_waterstand_bestand = pandas.read_csv("overzicht_resultaat/resultaat_minimale_waterstand_bakjes.csv",sep = ";", skiprows = [1])
df_postproces_minimale_waterstand_bestand['Scen_NR'] = df_postproces_minimale_waterstand_bestand['Scen_NR'].astype(int)

df_postproces_chloride_bestand = pandas.read_csv("overzicht_resultaat/resultaat_maximale_chloride_bakjes.csv",sep = ";", skiprows = [1])
df_postproces_chloride_bestand['Scen_NR'] = df_postproces_chloride_bestand['Scen_NR'].astype(int)

df_postproces_chloride_groei_bestand = pandas.read_csv("overzicht_resultaat/resultaat_maximale_chloride_groeiseizoen_bakjes.csv",sep = ";", skiprows = [1])
df_postproces_chloride_groei_bestand['Scen_NR'] = df_postproces_chloride_bestand['Scen_NR'].astype(int)

df_postproces_chloride_groei_dagen_bestand = pandas.read_csv("overzicht_resultaat/resultaat_dagen_chloride_boven_450CLmgL_groeiseizoen_bakjes.csv",sep = ";", skiprows = [1])
df_postproces_chloride_groei_dagen_bestand['Scen_NR'] = df_postproces_chloride_bestand['Scen_NR'].astype(int)

figuurdata_max_waterstand = scenario_input.merge(df_postproces_maximale_waterstand_bestand, on='Scen_NR') 
figuurdata_min_waterstand = scenario_input.merge(df_postproces_minimale_waterstand_bestand, on='Scen_NR') 
figuurdata_max_chloride = scenario_input.merge(df_postproces_chloride_bestand, on='Scen_NR') 
figuurdata_max_chloride_groeiseizoen = scenario_input.merge(df_postproces_chloride_groei_bestand, on='Scen_NR') 
figuurdata_dagen_chloride_groeiseizoen = scenario_input.merge(df_postproces_chloride_groei_dagen_bestand, on='Scen_NR') 


for variabel in scenario_columns:
	print(variabel)
	#Maak Figuren Zout
	# plot data
	#order = figuurdata_max_chloride[variabel].cat.categories.values.tolist()


	#Max waterstand
	resorted_data = figuurdata_max_waterstand.sort_values(variabel)
	ax1 = resorted_data.plot.scatter(x = variabel, y = 'Volkerak-Zoommeer', style= ".")
	ax1.set_xlabel(variabel)
	ax1.set_ylabel("Maximale waterstand (m NAP)")
	ax1.set_title("Waterstand Volkerak-Zoommeer : " + str(variabel))
	#ax1.legend(loc='upper right')
	plt.xticks(rotation = 90)
	plt.ylim((-0.5,1.00))
	plt.subplots_adjust(left = 0.125, right = 0.9, bottom = 0.4, top = 0.9)
	plt.rcParams["figure.figsize"] = (12,8)
	path_file_zb_var = os.path.join("overzicht_resultaat/", "Maximum_waterstand_VZM_"+ variabel + ".PNG")
	ax1.figure.savefig(path_file_zb_var, format = "png")
	plt.close()

	#Min waterstand
	resorted_data = figuurdata_min_waterstand.sort_values(variabel)
	ax1 = resorted_data.plot.scatter(x = variabel, y = 'Volkerak-Zoommeer', style= ".")
	ax1.set_xlabel(variabel)
	ax1.set_ylabel("Minimale waterstand (m NAP)")
	ax1.set_title("Waterstand Volkerak-Zoommeer : " + str(variabel))
	#ax1.legend(loc='upper right')
	plt.xticks(rotation = 90)
	plt.ylim((-0.5,1.0))
	plt.subplots_adjust(left = 0.125, right = 0.9, bottom = 0.4, top = 0.9)
	plt.rcParams["figure.figsize"] = (12,8)
	path_file_zb_var = os.path.join("overzicht_resultaat/", "Minimum_waterstand_VZM_"+ variabel + ".PNG")
	ax1.figure.savefig(path_file_zb_var, format = "png")
	plt.close()

	#Max Chloride
	resorted_data = figuurdata_max_chloride.sort_values(variabel)
	ax1 = resorted_data.plot.scatter(x = variabel, y = 'VIII. Zoommeer Zuid', style= ".")
	ax1.set_xlabel(variabel)
	ax1.set_ylabel("Maximum zoutgehalte (g CL/l)")
	ax1.set_title("Zoutgehalte VIII. Zoommeer Zuid : " + str(variabel))
	#ax1.legend(loc='upper right')
	plt.xticks(rotation = 90)
	plt.ylim((0,1000))
	plt.subplots_adjust(left = 0.125, right = 0.9, bottom = 0.4, top = 0.9)
	plt.rcParams["figure.figsize"] = (12,8)
	path_file_zb_var = os.path.join("overzicht_resultaat/", "Maximum_zoutgehalte_VZM_VIII_"+ variabel + ".PNG")
	ax1.figure.savefig(path_file_zb_var, format = "png")
	plt.close()

	#Max Chloride Groeiseizoen
	resorted_data = figuurdata_max_chloride_groeiseizoen.sort_values(variabel)
	ax1 = resorted_data.plot.scatter(x = variabel, y = 'VIII. Zoommeer Zuid', style= ".")
	ax1.set_xlabel(variabel)
	ax1.set_ylabel("Maximum zoutgehalte in groeiseizoen (g CL/l)")
	ax1.set_title("Zoutgehalte groeiseizoen VIII. Zoommeer Zuid : " + str(variabel))
	#ax1.legend(loc='upper right')
	plt.xticks(rotation = 90)
	plt.ylim((0,1000))
	plt.subplots_adjust(left = 0.125, right = 0.9, bottom = 0.4, top = 0.9)
	plt.rcParams["figure.figsize"] = (12,8)
	path_file_zb_var = os.path.join("overzicht_resultaat/", "Maximum_zoutgehalte_Groeiseizoen_VZM_VIII_"+ variabel + ".PNG")
	ax1.figure.savefig(path_file_zb_var, format = "png")
	plt.close()

	#Max Chloride Groeiseizoen Dagen overschreiding 
	resorted_data = figuurdata_dagen_chloride_groeiseizoen.sort_values(variabel)
	ax1 = resorted_data.plot.scatter(x = variabel, y = 'VIII. Zoommeer Zuid', style= ".")
	ax1.set_xlabel(variabel)
	ax1.set_ylabel("Dagen boven zoutgehalte 450 mg/l in groeiseizoen (dag)")
	ax1.set_title("Dagen Zoutgehalte Groeiseizoen VIII. Zoommeer Zuid : " + str(variabel))
	#ax1.legend(loc='upper right')
	plt.xticks(rotation = 90)
	plt.ylim((0,200))
	plt.subplots_adjust(left = 0.125, right = 0.9, bottom = 0.4, top = 0.9)
	plt.rcParams["figure.figsize"] = (12,8)
	path_file_zb_var = os.path.join("overzicht_resultaat/", "Maximum_zoutgehalte_Groeiseizoen_dagen_overschreiding_VZM_VIII_"+ variabel + ".PNG")
	ax1.figure.savefig(path_file_zb_var, format = "png")
	plt.close()


print("Done.")