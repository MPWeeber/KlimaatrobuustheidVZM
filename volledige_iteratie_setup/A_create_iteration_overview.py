'''
Create iteration scenarios based on possible combinations
'''



import os
import shutil
import sys
import numpy

import pandas as pd
import matplotlib.pyplot as plt

import itertools

from collections import OrderedDict

#INITIALISE

#path to "input" dir
path_input_dir = "./input/"

#path to "input overview"
path_input_overview_dir = "./input_overview/"


#categorie order
categories_1_volkeraksluizen  = ["1_continue_15m3s","3_continue_25m3s","4_continue_25m3s_winterdoorspoeling","5_continue_40m3s"]
categories_2_neerslag = ["1_KNMI_neerslag_geen_scenario",\
						"7_KNMI_neerslag_geen_scenario_2018","8_KNMI_neerslag_vlak_2050_2018","9_KNMI_neerslag_extreem_2085_2018"]
categories_3_krammersluizen = ["1_operatie_krammersluizen_met_zss_0cm", "2_operatie_krammersluizen_met_zss_10cm",\
	"3_operatie_krammersluizen_met_zss_20cm", "4_operatie_krammersluizen_met_zss_30cm", "5_operatie_krammersluizen_met_zss_40cm", "6_operatie_krammersluizen_met_zss_50cm",\
	"7_operatie_krammersluizen_met_zss_60cm", "8_operatie_krammersluizen_met_zss_70cm", "9_operatie_krammersluizen_met_zss_80cm", "10_operatie_krammersluizen_met_zss_90cm",\
	"11_operatie_krammersluizen_met_zss_100cm"]
categories_4_bergsediepsluis = ["1_standaard_operatie_bergsediepsluis"]
categories_5_kreekraksluis = ["1_standaard_operatie_kreekraksluis"]
categories_6_verdamping = ["1_verdamping_wilhelminadorp2003", "2_verdamping_GilzeRijen2018"]
categories_7_kwel = ["1_standaard_kwel_3kgs","2_scenario_kwel_6kgs"]
categories_8a_watervraag_hollandse_delta = ["1_10proc_zomer_watervraag_hollandse_delta"]
categories_8b_watervraag_schelde_stromen = ["1_10proc_zomer_watervraag_schelde_stromen"]
categories_8c_watervraag_brabantse_delta = ["1_10proc_zomer_watervraag_brabantse_delta"]
categories_9a_Dintel = ["1_afvoer_2017_Dintelsas","4_afvoer_2018_Dintelsas","5_afvoer_2018_Dintelsas_2050_RV","6_afvoer_2018_Dintelsas_2085_RV"]
categories_9b_Steenbergse_Vliet = ["1_afvoer_2017_Benedensas","4_afvoer_2018_Benedensas","5_afvoer_2018_Benedensas_2050","6_afvoer_2018_Benedensas_2085"]
categories_10_bathse_spuisluis = ["1_standaard_beheer"]
categories_A_zeespiegelstijging = ["1_waterstand_bath_2003","2_waterstand_bath_2003_plus_10_cm",\
	"3_waterstand_bath_2003_plus_20_cm", "4_waterstand_bath_2003_plus_30_cm", "5_waterstand_bath_2003_plus_40_cm",\
	"6_waterstand_bath_2003_plus_50_cm", "7_waterstand_bath_2003_plus_60_cm", "8_waterstand_bath_2003_plus_70_cm",\
	"9_waterstand_bath_2003_plus_80_cm", "10_waterstand_bath_2003_plus_90_cm", "11_waterstand_bath_2003_plus_100_cm"]
categories_B_inlaatstop_volkeraksluizen = ["1_inlaat_continue","2_inlaatstop_volkeraksluizen"]
categories_C1_waterstand_VZM_lowerlimit = ["1_continue_min10cmNAP", "2_peiltrap_gemiddeld"]
categories_C2_waterstand_VZM_upperlimit = ["1_continue_plus15cmNAP"]



iteration_csv = [["Overall_Topic_1", "Overall_Topic_2", "Topic_name", "ModelType",\
 "System", "Layername", "parameter_cat", "layer_filename", "unit", "statistic", "description"]]


#start log
log = []
validation_log = []
nr_csvs = 0
nr_of_scenarios = 0
log.append(["---log for iteration scenarios---"])
log.append([""])

input_dict = OrderedDict()
input_dict_val = []
input_dict_scen = OrderedDict()

#get all level1 dirs and loop over them
waterbalans_dict = OrderedDict()
saltbalans_dict = OrderedDict()

#delete previous results


#create output folder
dir_wb = "waterbalans"
path_dir_wb = os.path.join(path_input_overview_dir, dir_wb)
if os.path.exists(path_dir_wb):
	shutil.rmtree(path_dir_wb)
	os.makedirs(path_dir_wb)

else:
   	os.makedirs(path_dir_wb)

dir_sb = "saltbalans"
path_dir_sb = os.path.join(path_input_overview_dir, dir_sb)
if os.path.exists(path_dir_sb):
	shutil.rmtree(path_dir_sb)
	os.makedirs(path_dir_sb)
else:
	os.makedirs(path_dir_sb)

log.append(["- Structure and number of files"])
level1_dirs = [cur_dir for cur_dir in os.listdir(path_input_dir) \
	if(os.path.isdir(os.path.join(path_input_dir,cur_dir)))]

for level1_dir in level1_dirs:
	log.append(["   /"+ level1_dir])
	#get all csv files in a level1 dir and loop over them		
	path_l1_dir = os.path.join(path_input_dir, level1_dir) 
	csvs_l1_dir = [file for file in os.listdir(path_l1_dir) if(file.endswith(".csv"))]
		
	#make input for variable
	input_dict[level1_dir] = []

	unit_waterbalans = []
	unit_saltbalans = []

	first = True
	salt_present = False

	#loop over the variations of variable
	for csv_file in csvs_l1_dir:
		print(csv_file)

		#add data to the log and count xmls
		path_csv_file = os.path.join(path_l1_dir,csv_file)
		log.append(["        /"+ csv_file])
		nr_csvs = nr_csvs + 1

		#add input for variable
		name_csv_file = csv_file.replace(".csv","")
		input_dict[level1_dir].append([name_csv_file])

		#read csv with Pandas
		pd_df = pd.read_csv(path_csv_file, sep = ";")
		date_parser = pd.to_datetime(pd_df["Tijdstip"], format="%d-%m-%Y %H:%M")

	
		
		if((len(pd_df.columns) == 3) & (first == True)):
			salt_present = True

		df_var_waterbalans = pd.DataFrame(data = {name_csv_file : pd_df.iloc[:, 1].values}, index = date_parser)
		unit_waterbalans.append(pd_df.columns[1]) 
		if(salt_present):
			df_var_saltbalans = pd.DataFrame(data = {name_csv_file : pd_df.iloc[:, 2].values}, index = date_parser)
			unit_saltbalans.append(pd_df.columns[2]) 
	
		#change all time to year 2019
		jaar_collectie = pd.DatetimeIndex(df_var_waterbalans.index).year.values.tolist()
		jaar_dataset = max(set(jaar_collectie), key = jaar_collectie.count)
		#zet het jaar op 2019 (geen schikkeljaar) -> rekenjaar is 2019 (2018 opstart)
		if( (2019 - jaar_dataset) > 0 ):
			df_var_waterbalans.index = df_var_waterbalans.index + pd.DateOffset(years= (2019 - jaar_dataset))
			if(salt_present):
				df_var_saltbalans.index = df_var_saltbalans.index + pd.DateOffset(years= (2019 - jaar_dataset))	
		elif((2019 - jaar_dataset) < 0):
			df_var_waterbalans.index = df_var_waterbalans.index - pd.DateOffset(years= (jaar_dataset - 2019))
			if(salt_present):
				df_var_saltbalans.index = df_var_saltbalans.index + pd.DateOffset(years= (jaar_dataset - 2019))	
		else:
			pass
	
		#make to complete dataframes over time	
		if(first):
			first = False
			df_var_waterbalans_comp = df_var_waterbalans
			if(salt_present):
				df_var_saltbalans_comp = df_var_saltbalans

		else:
			df_var_waterbalans_comp = pd.merge(df_var_waterbalans_comp, df_var_waterbalans, how = "outer", left_index = True, right_index = True)
			if(salt_present):
				df_var_saltbalans_comp = pd.merge(df_var_saltbalans_comp,df_var_saltbalans, how = "outer", left_index = True, right_index = True)

	#check if one unit
	if(len(set(unit_waterbalans)) != 1):
		raise ValueError("Units for waterbalans not unique in input variable '" + level1_dir + "'." +\
						 "Combinations are : " + str(set(unit_waterbalans)) + ".")
	if(salt_present):
		if(len(set(unit_saltbalans)) != 1):
			raise ValueError("Units for saltbalans not unique in input variable '" + level1_dir + "'." +\
						 "Combinations are : " + str(set(unit_saltbalans)) + ".")

	#set unit
	unit_wb_comp = list(set(unit_waterbalans))[0]
	if(salt_present):
		unit_sb_comp = list(set(unit_saltbalans))[0]

	#maak volgorde van categorieen (NU HANDMATIG GECODEERD, IN DE TOEKOMST MET INPUT FILE PER VARIABEL)
	if(level1_dir == "1_volkeraksluizen"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_1_volkeraksluizen]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_1_volkeraksluizen]
	elif(level1_dir == "2_neerslag"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_2_neerslag]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_2_neerslag]
	elif(level1_dir == "3_krammersluizen"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_3_krammersluizen]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_3_krammersluizen]
	elif(level1_dir == "4_bergsediepsluis"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_4_bergsediepsluis]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_4_bergsediepsluis]
	elif(level1_dir == "5_kreekraksluis"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_5_kreekraksluis]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_5_kreekraksluis]
	elif(level1_dir == "6_verdamping"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_6_verdamping]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_6_verdamping]
	elif(level1_dir == "7_kwel"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_7_kwel]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_7_kwel]
	elif(level1_dir == "8a_watervraag_hollandse_delta"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_8a_watervraag_hollandse_delta]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_8a_watervraag_hollandse_delta]
	elif(level1_dir == "8b_watervraag_schelde_stromen"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_8b_watervraag_schelde_stromen]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_8b_watervraag_schelde_stromen]
	elif(level1_dir == "8c_watervraag_brabantse_delta"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_8c_watervraag_brabantse_delta]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_8c_watervraag_brabantse_delta]
	elif(level1_dir == "9a_Dintel"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_9a_Dintel]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_9a_Dintel]
	elif(level1_dir == "9b_Steenbergse_Vliet"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_9b_Steenbergse_Vliet]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_9b_Steenbergse_Vliet]
	elif(level1_dir == "10_bathse_spuisluis"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_10_bathse_spuisluis]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_10_bathse_spuisluis]
	elif(level1_dir == "A_zeespiegelstijging"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_A_zeespiegelstijging]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_A_zeespiegelstijging]
	elif(level1_dir == "B_inlaatstop_volkeraksluizen"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_B_inlaatstop_volkeraksluizen]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[ categories_B_inlaatstop_volkeraksluizen]
	elif(level1_dir == "C1_waterstand_VZM_lowerlimit"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_C1_waterstand_VZM_lowerlimit]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_C1_waterstand_VZM_lowerlimit]
	elif(level1_dir == "C2_waterstand_VZM_upperlimit"):
		df_var_waterbalans_comp  = df_var_waterbalans_comp[categories_C2_waterstand_VZM_upperlimit]
		if(salt_present):
			df_var_saltbalans_comp = df_var_saltbalans_comp[categories_C2_waterstand_VZM_upperlimit]
	else:
		raise ValuError("Order for this input variable has not been given yet : " + str(level1_dir))

	#make graph of variantions
	lines_waterbalans = df_var_waterbalans_comp.plot.line()
	lines_waterbalans.set_xlabel("Time")
	lines_waterbalans.set_ylabel(unit_wb_comp)
	lines_waterbalans.set_title(level1_dir)
	lines_waterbalans.legend(loc='upper right')
	plt.rcParams["figure.figsize"] = (12,8)

	waterbalans_dict[level1_dir] = {"data" : df_var_waterbalans_comp, "unit" : unit_wb_comp}

	#create output image
	dir_wb_var = level1_dir 
	path_file_wb_var = os.path.join(path_input_overview_dir, dir_wb, dir_wb_var + ".PNG")
	lines_waterbalans.figure.savefig(path_file_wb_var, format = "png")
	plt.close()

	if(salt_present):
		lines_saltbalans = df_var_saltbalans_comp.plot.line()
		lines_saltbalans.set_xlabel("Time")
		lines_saltbalans.set_ylabel(unit_sb_comp)
		lines_saltbalans.set_title(level1_dir)
		lines_saltbalans.legend(loc='upper right')
		plt.rcParams["figure.figsize"] = (12,8)

		saltbalans_dict[level1_dir] = {"data" : df_var_saltbalans_comp, "unit" : unit_sb_comp}

		dir_sb_var = level1_dir 
		path_file_sb_var = os.path.join(path_input_overview_dir, dir_sb, dir_sb_var + ".PNG")
		lines_saltbalans.figure.savefig(path_file_sb_var, format = "png")
		plt.close()


#make potential scenarios
list_of_input = [value for key, value in input_dict.items()]
scenario_combinations = list(itertools.product(*list_of_input))

#remove impossible combinations
real_scenario_combinations = []
key_nr_zeespiegelstijging = [nr for nr, key in enumerate(input_dict.keys()) if(key == "A_zeespiegelstijging")][0]
key_nr_krammersluizen = [nr for nr, key in enumerate(input_dict.keys()) if(key == "3_krammersluizen")][0]
key_nr_neerslag = [nr for nr, key in enumerate(input_dict.keys()) if(key == "2_neerslag")][0]
key_nr_verdamping = [nr for nr, key in enumerate(input_dict.keys()) if(key == "6_verdamping")][0]
key_nr_dintel = [nr for nr, key in enumerate(input_dict.keys()) if(key == "9a_Dintel")][0]
key_nr_vliet = [nr for nr, key in enumerate(input_dict.keys()) if(key == "9b_Steenbergse_Vliet")][0]

for scen in scenario_combinations:
	
	#check for combinations Zeespiegelstijging en Krammersluizen
	if(scen[key_nr_zeespiegelstijging][0] == "1_waterstand_bath_2003" and scen[key_nr_krammersluizen][0] == "1_operatie_krammersluizen_met_zss_0cm"):
		pass
	elif(scen[key_nr_zeespiegelstijging][0] == "2_waterstand_bath_2003_plus_10_cm" and scen[key_nr_krammersluizen][0] == "2_operatie_krammersluizen_met_zss_10cm"):
		pass
	elif(scen[key_nr_zeespiegelstijging][0] == "3_waterstand_bath_2003_plus_20_cm" and scen[key_nr_krammersluizen][0] == "3_operatie_krammersluizen_met_zss_20cm"):
		pass
	elif(scen[key_nr_zeespiegelstijging][0] == "4_waterstand_bath_2003_plus_30_cm" and scen[key_nr_krammersluizen][0] == "4_operatie_krammersluizen_met_zss_30cm"):
		pass
	elif(scen[key_nr_zeespiegelstijging][0] == "5_waterstand_bath_2003_plus_40_cm" and scen[key_nr_krammersluizen][0] == "5_operatie_krammersluizen_met_zss_40cm"):
		pass
	elif(scen[key_nr_zeespiegelstijging][0] == "6_waterstand_bath_2003_plus_50_cm" and scen[key_nr_krammersluizen][0] == "6_operatie_krammersluizen_met_zss_50cm"):
		pass
	elif(scen[key_nr_zeespiegelstijging][0] == "7_waterstand_bath_2003_plus_60_cm" and scen[key_nr_krammersluizen][0] == "7_operatie_krammersluizen_met_zss_60cm"):
		pass
	elif(scen[key_nr_zeespiegelstijging][0] == "8_waterstand_bath_2003_plus_70_cm" and scen[key_nr_krammersluizen][0] == "8_operatie_krammersluizen_met_zss_70cm"):
		pass
	elif(scen[key_nr_zeespiegelstijging][0] == "9_waterstand_bath_2003_plus_80_cm" and scen[key_nr_krammersluizen][0] == "9_operatie_krammersluizen_met_zss_80cm"):
		pass
	elif(scen[key_nr_zeespiegelstijging][0] == "10_waterstand_bath_2003_plus_90_cm" and scen[key_nr_krammersluizen][0] == "10_operatie_krammersluizen_met_zss_90cm"):
		pass
	elif(scen[key_nr_zeespiegelstijging][0] == "11_waterstand_bath_2003_plus_100_cm" and scen[key_nr_krammersluizen][0] == "11_operatie_krammersluizen_met_zss_100cm"):
		pass
	else:
		continue


	#check for combinations Neerslag, afvoer Dintel en afvoer Vliet
	if(scen[key_nr_neerslag][0] == "1_KNMI_neerslag_geen_scenario" and\
		 scen[key_nr_verdamping][0] == "1_verdamping_wilhelminadorp2003"  and\
		 scen[key_nr_dintel][0] == "1_afvoer_2017_Dintelsas"  and\
		 scen[key_nr_vliet][0] == "1_afvoer_2017_Benedensas"):
		pass
	elif(scen[key_nr_neerslag][0] == "7_KNMI_neerslag_geen_scenario_2018" and\
		 scen[key_nr_verdamping][0] == "2_verdamping_GilzeRijen2018"  and\
		 scen[key_nr_dintel][0] == "4_afvoer_2018_Dintelsas"  and\
		 scen[key_nr_vliet][0] == "4_afvoer_2018_Benedensas"):
		pass
	elif(scen[key_nr_neerslag][0] == "8_KNMI_neerslag_vlak_2050_2018" and\
		scen[key_nr_verdamping][0] == "2_verdamping_GilzeRijen2018"  and\
		 scen[key_nr_dintel][0] == "5_afvoer_2018_Dintelsas_2050"  and\
		 scen[key_nr_vliet][0] == "5_afvoer_2018_Benedensas_2050" ):
		pass
	elif(scen[key_nr_neerslag][0] == "8_KNMI_neerslag_vlak_2050_2018" and\
		scen[key_nr_verdamping][0] == "2_verdamping_GilzeRijen2018"  and\
		 scen[key_nr_dintel][0] == "5_afvoer_2018_Dintelsas_2050_RV"  and\
		 scen[key_nr_vliet][0] == "5_afvoer_2018_Benedensas_2050" ):
		pass
	elif(scen[key_nr_neerslag][0] == "9_KNMI_neerslag_extreem_2085_2018" and\
		 scen[key_nr_verdamping][0] == "2_verdamping_GilzeRijen2018"  and\
		 scen[key_nr_dintel][0] == "6_afvoer_2018_Dintelsas_2085"  and\
		 scen[key_nr_vliet][0] == "6_afvoer_2018_Benedensas_2085" ):
		pass
	elif(scen[key_nr_neerslag][0] == "9_KNMI_neerslag_extreem_2085_2018" and\
		 scen[key_nr_verdamping][0] == "2_verdamping_GilzeRijen2018"  and\
		 scen[key_nr_dintel][0] == "6_afvoer_2018_Dintelsas_2085_RV"  and\
		 scen[key_nr_vliet][0] == "6_afvoer_2018_Benedensas_2085" ):
		pass
	else:
		continue

	real_scenario_combinations.append(scen)

log.append([""])
log.append([" - Total scenarios"])
log.append(["Scenarios : "+ str(len(real_scenario_combinations))])
log.append([""])
log.append(["END LOG"])



#write scenarios

scenario_overview = [["Scen_NR"] + [key for key, value in input_dict.items()]]
scen_nr = 0
for scen in real_scenario_combinations:
	scen_nr = scen_nr + 1
	scenario_overview.append([str(scen_nr)] + [value[0] for value in scen])

#write the scenario overview 
scenario_csv =  open("scenario_overview.csv","w")
scenario_csv.writelines("%s\n" % ";".join(line) for line in scenario_overview)
scenario_csv.close()

#write the log
log_txt =  open("log_create_iteration_overview.txt","w")
log_txt.writelines("%s\n" % line[0] for line in log)
log_txt.close()

print("Done.")	