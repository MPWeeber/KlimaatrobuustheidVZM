'''
Simpel bakjesmodel Volkerak-Zoommeer

Created by Arno Nolte & Marc Weeber (Deltares)


Balansen

I. Krammer-Volkerak Oost 			        = + Volkeraksluizen + Dintel + Neerslag - Verdamping + Waterstandsverschil - (I -> II) 
II. Krammer-Volkerak Midden			        = +(I -> II) + Vliet - Watervraag Hollandse Delta + Neerslag - Verdamping + Waterstandsverschil	- (II -> III) 
III. Krammer-Volkerak Ingang Eendracht     	= +(II -> III) + (IV -> III) + Neerslag - Verdamping + Waterstandsverschil - (III -> V)
IV. Krammer-Volkerak West			        = + Neerslag - Verdamping + Waterstandsverschil– (IV -> III) -(IV -> X)
V. Eendracht Noord				            = +(III -> V) + Neerslag - Verdamping + Waterstandsverschil - Watervraag SchSt + Kwel - (V -> VI)
VI. Eendracht Zuid				            = +(V -> VI) + Neerslag - Verdamping + Waterstandsverschil - Watervraag SchSt + Kwel - (VI -> VII)
VII. Zoommeer				                = +(VI -> VII) - Bergse diepsluis (water) + Bergse diepsluis (zout) - Watervraag BD - Watervraag SchSt + Kwel - (VII -> VIII)
VIII. Zoommeer Zuid				            = +(VII -> VIII) - Kreekraksluizen + Neerslag - Verdamping + Waterstandsverschil + Kwel - (VIII -> IX)
IX. Bathse Spuikanaal				        = +(VIII -> IX) - Bathse spuisluis (water) + Bathse spuisluis (zout) + Neerslag - Verdamping + Waterstandsverschil
X. Voorhaven Krammersluizen 		        = Krammersluizen (water) + Krammersluizen (zout)




'''
import sys
import math

import pandas as pd
import datetime
import dateutil
import pytz

#settings

#tijdstap_model =     10  #minutes (10 min)
tijdstap_model =   1440  #minutes (dag)

tijdstap_output =  1440  #minutes (dag)
#tijdstap_output =   10  #minutes (10 min)

#configuratie VZM
waterstand_initeel = -0.10
waterstand_eerste_stap = -0.05

#Bathse spuisluis
breedte_koker_m = 2.85
hoogte_koker_m = 5
aantal_kokers = 6
doorstroomoppervlak_m2 = aantal_kokers * breedte_koker_m * hoogte_koker_m
afvoercoefficient = 0.65


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

#Kwel verdeling
#Locatie                          | Factor Kwel verdeling
Kwel_factor_Krammer_Volkerak_West = 0.30
Kwel_factor_Eendracht_Noord       = 0.10
Kwel_factor_Eendracht_Zuid        = 0.10
Kwel_factor_Zoommeer              = 0.25
Kwel_factor_Zoommeer_Zuid         = 0.25

#lees automatisch het data format
dateparse = lambda x: datetime.datetime.strptime(x,"%d-%m-%Y %H:%M")

def read_file(file_path):
	#leeas de  csv file met pandas en converteer de datum
	df = pd.read_csv(file_path, sep = ";",\
		 parse_dates=['Tijdstip'], date_parser=dateparse)
	#lees het meetjaar van de dataset
	jaar_collectie = pd.DatetimeIndex(df['Tijdstip']).year.values.tolist()
	jaar_dataset = max(set(jaar_collectie), key = jaar_collectie.count)
	#zet het jaar op 2018 (geen schikkeljaar) -> rekenjaar is 2019 (2018 opstart)
	if( (2018 - jaar_dataset) > 0 ):
		df['Tijdstip'] = df['Tijdstip'] + pd.DateOffset(years= (2018 - jaar_dataset))
	elif((2018 - jaar_dataset) < 0):
		df['Tijdstip'] = df['Tijdstip'] - pd.DateOffset(years= (jaar_dataset - 2018))
	else:
		pass
	#verkrijg de tijdstap van de data op basis van eerste twee regels
	tijdstap = int((df.loc[1,"Tijdstip"] - df.loc[0,'Tijdstip']).total_seconds() / 60)
 
	return( (df, tijdstap) )

#Input 

(Volkeraksluizen     , tijdstap_Volkeraksluizen ) = read_file("input/1_volkeraksluizen.csv")
(Neerslag_VZM        , tijdstap_Neerslag_VZM    ) = read_file("input/2_neerslag.csv")
(Krammersluizen      , tijdstap_Krammersluizen  ) = read_file("input/3_krammersluizen.csv")	
(Bergsediepsluis     , tijdstap_Bergsediepsluis ) = read_file("input/4_bergsediepsluis.csv")
(Kreekraksluis       , tijdstap_Kreekraksluis   ) = read_file("input/5_kreekraksluis.csv")
(Verdamping_VZM      , tijdstap_Verdamping_VZM  ) = read_file("input/6_verdamping.csv")
(Kwel_VZM            , tijdstap_Kwel_VZM        ) = read_file("input/7_kwel.csv")
(wvr_Hollandse_Delta , tijdstap_wvr_Hollandse_Delta ) = read_file("input/8a_watervraag_hollandse_delta.csv")
(wvr_Brabantse_Delta , tijdstap_wvr_Brabantse_Delta ) = read_file("input/8c_watervraag_brabantse_delta.csv")
(wvr_Scheldestromen  , tijdstap_wvr_Scheldestromen  ) = read_file("input/8b_watervraag_schelde_stromen.csv")
(Dintel    , tijdstap_Dintel ) = read_file("input/9a_Dintel.csv")
(Vliet     , tijdstap_Vliet  ) = read_file("input/9b_Steenbergse_Vliet.csv")
(Bathse_spuisluis    , tijdstap_Bathse_spuisluis) = read_file("input/10_bathse_spuisluis.csv")
(waterstand_Bath, tijdstap_waterstand_Bath)  = read_file("input/A_zeespiegelstijging.csv")
(inlaatstop_VKSL, tijdstap_inlaatstop_VKSL)  = read_file("input/B_inlaatstop_volkeraksluizen.csv")
(stuur_Waterstand_lowerlimit_VZM , tijdstap_stuur_Waterstand_lowerlimit_VZM ) = read_file("input/C1_waterstand_VZM_lowerlimit.csv")
(stuur_Waterstand_upperlimit_VZM , tijdstap_stuur_Waterstand_upperlimit_VZM ) = read_file("input/C2_waterstand_VZM_upperlimit.csv")

#bereken oppervlak totaal VZM (bakje X wordt niet meegenomen bij atmosfeer en waterstandverandering)
Totaal_oppv_m2 = (I_oppv_m2 + II_oppv_m2 + III_oppv_m2 + IV_oppv_m2 + V_oppv_m2 + VI_oppv_m2 +\
				  VII_oppv_m2 + VIII_oppv_m2 + IX_oppv_m2) 

#Results
#Bathsespuisluis

#aggregreer datatabellen waar nodig
if(tijdstap_Volkeraksluizen != 1440):
	raise ValueError("Dag tijdstap verwacht bij Volkeraksluizen")
if(tijdstap_Krammersluizen != 1440):
	raise ValueError("Dag tijdstap verwacht bij Krammersluizen")
if(tijdstap_Bergsediepsluis != 1440):
	raise ValueError("Dag tijdstap verwacht bij Bergsediepsluis")
if(tijdstap_Kreekraksluis != 1440):
	raise ValueError("Dag tijdstap verwacht bij Kreekraksluis")
if(tijdstap_Bathse_spuisluis != 1440):
	raise ValueError("Dag tijdstap verwacht bij Kreekraksluis")			
if(tijdstap_wvr_Hollandse_Delta != 1440):
	raise ValueError("Dag tijdstap verwacht bij wvr_Hollandse_Delta")
if(tijdstap_wvr_Brabantse_Delta != 1440):
	raise ValueError("Dag tijdstap verwacht bij wvr_Brabantse_Delta")
if(tijdstap_wvr_Scheldestromen != 1440):
	raise ValueError("Dag tijdstap verwacht bij wvr_Schelde_Stromen")
if(tijdstap_Dintel != 1440):
	raise ValueError("Dag tijdstap verwacht bij Dintel")
if(tijdstap_Vliet != 1440):
	raise ValueError("Dag tijdstap verwacht bij Vliet")
if(tijdstap_inlaatstop_VKSL != 1440):
	raise ValueError("Dag tijdstap verwacht bij inlaatstop_VKSL")
if(tijdstap_stuur_Waterstand_lowerlimit_VZM != 1440):
	raise ValueError("Dag tijdstap verwacht bij stuur_Waterstand_lowerlimit_VZM")
if(tijdstap_stuur_Waterstand_upperlimit_VZM != 1440):
	raise ValueError("Dag tijdstap verwacht bij stuur_Waterstand_upperlimit_VZM")
if(tijdstap_Neerslag_VZM != 60):
	raise ValueError("Uur tijdstap verwacht bij Neerslag_VZM")
if(tijdstap_Verdamping_VZM != 1440 and tijdstap_Verdamping_VZM != 60):
	raise ValueError("Dag of uur tijdstap verwacht bij Verdamping_VZM")
if(tijdstap_waterstand_Bath != 10):
	raise ValueError("10 minuten tijdstap verwacht bij waterstand_Bath")


#Bereken dag waarden Neerslag en Verdamping
Neerslag_VZM_mmd = Neerslag_VZM.groupby(Neerslag_VZM["Tijdstip"].dt.date, as_index=False).agg(["sum"], axis = 1).reset_index()
Neerslag_VZM_mmd.columns = Neerslag_VZM_mmd.columns.droplevel(1)
Neerslag_VZM_mmd["Tijdstip"] = Neerslag_VZM_mmd["Tijdstip"].astype('datetime64[ns]')
if(tijdstap_Verdamping_VZM == 60):
	Verdamping_VZM_mmd = Verdamping_VZM.groupby(Verdamping_VZM["Tijdstip"].dt.date, as_index=False).agg(["sum"], axis = 1).reset_index()
	Verdamping_VZM_mmd.columns = Verdamping_VZM_mmd.columns.droplevel(1)
elif(tijdstap_Verdamping_VZM == 1440):
	Verdamping_VZM_mmd = Verdamping_VZM
else:
	raise ValueError("Deze tijdstap van Verdamping is niet mogelijk gemaakt : " + str(tijdstap_Verdamping_VZM))
Verdamping_VZM_mmd["Tijdstip"] = Verdamping_VZM_mmd["Tijdstip"].astype('datetime64[ns]')


#Waterbalans input
wb_stuur_Waterstand_lowerlimit_VZM_mNAP = stuur_Waterstand_lowerlimit_VZM.iloc[:,[0,1]]
wb_stuur_Waterstand_upperlimit_VZM_mNAP = stuur_Waterstand_upperlimit_VZM.iloc[:,[0,1]]
wb_Volkeraksluizen_m3s = Volkeraksluizen.iloc[:,[0,1]].copy() 
wb_Dintel_m3s = Dintel.iloc[:,[0,1]]
wb_Vliet_m3s = Vliet.iloc[:,[0,1]]
wb_Krammersluizen_m3s = Krammersluizen.iloc[:,[0,1]]	
wb_Bergsediepsluis_m3s = Bergsediepsluis.iloc[:,[0,1]]
wb_Kreekraksluis_m3s = Kreekraksluis.iloc[:,[0,1]]
#wb_Bathse_spuisluis = Bathse_spuisluis.iloc[:,[0,1]]
wb_wvr_Hollandse_Delta_m3s = wvr_Hollandse_Delta.iloc[:,[0,1]]
wb_wvr_Brabantse_Delta_m3s = wvr_Brabantse_Delta.iloc[:,[0,1]]
wb_wvr_Scheldestromen_m3s = wvr_Scheldestromen.iloc[:,[0,1]]
wb_Neerslag_VZM_mmd = Neerslag_VZM_mmd.iloc[:,[0,1]]
wb_Verdamping_VZM_mmd = Verdamping_VZM_mmd.iloc[:,[0,1]]
wb_Kwel_VZM_m3s = Kwel_VZM.iloc[:,[0,1]]

#Zoutbalans input
#zb_stuur_Waterstand_lowerlimit_VZM_CLmgL = stuur_Waterstand_lowerlimit_VZM.iloc[:,[0,2]]
#zb_stuur_Waterstand_upperlimit_VZM_CLmgL = stuur_Waterstand_upperlimit_VZM.iloc[:,[0,2]]
zb_Volkeraksluizen_KGS = Volkeraksluizen.iloc[:,[0,2]].copy()
zb_Dintel_KGS = Dintel.iloc[:,[0,2]]
zb_Vliet_KGS = Vliet.iloc[:,[0,2]]
zb_Krammersluizen_KGS = Krammersluizen.iloc[:,[0,2]]	
zb_Bergsediepsluis_KGS = Bergsediepsluis.iloc[:,[0,2]]
zb_Kreekraksluis_KGS = Kreekraksluis.iloc[:,[0,2]]
zb_Bathse_spuisluis_KGS = Bathse_spuisluis.iloc[:,[0,2]]
zb_wvr_Hollandse_Delta_KGS = wvr_Hollandse_Delta.iloc[:,[0,2]]
zb_wvr_Brabantse_Delta_KGS = wvr_Brabantse_Delta.iloc[:,[0,2]]
zb_wvr_Scheldestromen_KGS = wvr_Scheldestromen.iloc[:,[0,2]]
zb_Neerslag_VZM_KGS = Neerslag_VZM_mmd.iloc[:,[0,2]]
zb_Verdamping_VZM_KGS = Verdamping_VZM_mmd.iloc[:,[0,2]]
zb_Kwel_VZM_KGS = Kwel_VZM.iloc[:,[0,2]]


#Corrigeer voor inlaatstop VolkerakSluizen
comb_VolkerakSluizen = Volkeraksluizen.merge(inlaatstop_VKSL, on = "Tijdstip")
wb_Volkeraksluizen_m3s.loc[wb_Volkeraksluizen_m3s.columns[1]] = comb_VolkerakSluizen[comb_VolkerakSluizen.columns[1]] * comb_VolkerakSluizen[comb_VolkerakSluizen.columns[3]]
zb_Volkeraksluizen_KGS.loc[zb_Volkeraksluizen_KGS.columns[1]] = comb_VolkerakSluizen[comb_VolkerakSluizen.columns[2]] * comb_VolkerakSluizen[comb_VolkerakSluizen.columns[3]]

#------------------------Bepaal iteratie stappen bakjes model--------------------------------#
start_tijd = datetime.datetime.strptime("01-01-2018 00:00","%d-%m-%Y %H:%M")
eind_tijd  = datetime.datetime.strptime("01-01-2020 00:00","%d-%m-%Y %H:%M") 
tijdstappen =  ((eind_tijd + datetime.timedelta(days = 1)) - start_tijd) / datetime.timedelta(hours=0, minutes=tijdstap_model)

#check of het een heel nummer is (deelbaar door tijdstappen)
if(not tijdstappen.is_integer()):
	raise ValueError("Jaar is niet deelbaar door tijdstap, zorg voor een consistente tijdstap")

model_iteratie_momenten = [start_tijd + datetime.timedelta(minutes = i * tijdstap_model) for i in range(0,int(tijdstappen))]
nr_model_iteratie_momenten = len(model_iteratie_momenten)
#--------------------------------Zet bestanden op--------------------------------------------#
invoer_bestand = [["Tijdstip","Waterstand streefwaarde","Waterstand werkelijk",\
	"Volkeraksluizen","Dintel","Vliet","Krammersluizen","Krammersluizen (na correctie)", "Bergse diepsluis",\
	"Kreekraksluizen", "Bathse spuisluis (voor correctie)", "Bathse spuisluis",\
	"Watervraag Hollandse Delta", "Watervraag Brabantse Delta", "Watervraag Scheldestromen",\
	"Neerslag","Verdamping","Kwel"]]
invoer_bestand.append(["","m NAP","m NAP","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s",\
	"m3/s","m3/s","m3/s","m3/s","mm/d","mm/d","mm/d"])

invoer_zout_bestand = [["Tijdstip","Bathse spuisluis", "Bergse diepsluis", "Krammersluizen",\
	"Kwel_Krammer_Volkerak_West", "Kwel_Eendracht_Noord", "Kwel_Eendracht_Zuid", "Kwel_Zoommeer", "Kwel_Zoommeer_Zuid"]]
invoer_zout_bestand.append(["","g NaCL/s","g NaCL / S","g NaCL / S","g NaCL / S",\
	"g NaCL / S", "g NaCL / S","g NaCL / S","g NaCL / S"])

balans_bestand = [["Tijdstip","IN_DEBIET","UIT_DEBIET","ATMOSFEER_DEBIET","WATERSTAND_VERANDERING_DEBIET", "BALANS"]]
balans_bestand.append(["","m3/s","m3/s","m3/s","m3/s","m3/s"])

overzicht_bestand = [["Tijdstip","I -> II","II -> III","III -> V","IV -> III","V -> VI","VI -> VII","VII -> VIII","VIII -> IX","IV -> X"]]
overzicht_bestand.append(["","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s"])

overzicht_debiet_KSL_mogelijk_bestand = [["Tijdstip", "Waterstand_Bath", "Waterstand_VZM", "Debiet_KSL_mogelijk"]]
overzicht_debiet_KSL_mogelijk_bestand.append(["", "m NAP", "m NAP", "m3/s"])

overzicht_neerslag_bestand = [["Tijdstip","Neerslag_I","Neerslag_II","Neerslag_III","Neerslag_IV","Neerslag_V",\
								"Neerslag_VI","Neerslag_VII","Neerslag_VIII","Neerslag_IX"]]
overzicht_neerslag_bestand.append(["","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s"])

overzicht_verdamping_bestand = [["Tijdstip","Verdamping_I","Verdamping_II","Verdamping_III","Verdamping_IV","Verdamping_V",\
								"Verdamping_VI","Verdamping_VII","Verdamping_VIII","Verdamping_IX"]]
overzicht_verdamping_bestand.append(["","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s","m3/s"])

overzicht_volumes_bestand = [["Tijdstip", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]]
overzicht_volumes_bestand.append(["", "m3", "m3", "m3", "m3", "m3", "m3", "m3", "m3", "m3"])

log_bestand = [["PROGRESS LOG"]]

#-----------------------------------RUN het bakjes model-------------------------------------#

#zet initele waterstand op bij model
waterstand_VZM_nieuw = waterstand_initeel

#Zet eerste model stap
eerste_model_stap = True

for nr, model_iteratie_tijd in enumerate(model_iteratie_momenten):

	print("Model progress = date : " + model_iteratie_tijd.strftime(format = "%Y-%m-%d %H:%M") +\
	 " , percentage : " + str(int((nr / nr_model_iteratie_momenten) * 100)) + "%")

	#toekomsttijd
	volgende_model_iteratie_tijd = model_iteratie_tijd + datetime.timedelta(minutes = tijdstap_model)

	#maak een start op jaar (2018) en daarna het rekenjaar (2019) en gebruik hiervoor de zelfde vaste IN en UIT
	# debieten. Laatste tijdstap is net in 2020
	if(model_iteratie_tijd.year == 2019):
		mod_model_iteratie_tijd = model_iteratie_tijd - datetime.timedelta(days = 365)
	elif(model_iteratie_tijd.year == 2020):
		mod_model_iteratie_tijd = model_iteratie_tijd - datetime.timedelta(days = 730)
	else:
		mod_model_iteratie_tijd = model_iteratie_tijd

	#toekomsttijd
	volgende_mod_model_iteratie_tijd = mod_model_iteratie_tijd + datetime.timedelta(minutes = tijdstap_model)

	#bewaar waterstand en huidige Volumes
	waterstand_VZM_huidig = waterstand_VZM_nieuw

	#laat de waterstand voor de eerste model stap inspelen op een andere streefwaarden
	if(eerste_model_stap):
		waterstand_VZM_streefwaarde = waterstand_eerste_stap
		eerste_model_stap = False
	else:
		waterstand_VZM_streefwaarde = wb_stuur_Waterstand_lowerlimit_VZM_mNAP.loc[wb_stuur_Waterstand_lowerlimit_VZM_mNAP["Tijdstip"] == mod_model_iteratie_tijd,\
			wb_stuur_Waterstand_lowerlimit_VZM_mNAP.columns[1]].values[0]

	#Debiet_IN
	Debiet_Volkeraksluizen = wb_Volkeraksluizen_m3s.loc[wb_Volkeraksluizen_m3s["Tijdstip"] == mod_model_iteratie_tijd,\
		wb_Volkeraksluizen_m3s.columns[1]].values[0]
	Debiet_Dintel = wb_Dintel_m3s.loc[wb_Dintel_m3s["Tijdstip"] == mod_model_iteratie_tijd,\
		wb_Dintel_m3s.columns[1]].values[0]
	Debiet_Vliet = wb_Vliet_m3s.loc[wb_Vliet_m3s["Tijdstip"] == mod_model_iteratie_tijd,\
		wb_Vliet_m3s.columns[1]].values[0]

	#Debiet_UIT
	Debiet_Krammersluizen = wb_Krammersluizen_m3s.loc[wb_Krammersluizen_m3s["Tijdstip"] == mod_model_iteratie_tijd,\
	 	wb_Krammersluizen_m3s.columns[1]].values[0]
	Debiet_Bergsediepsluis = wb_Bergsediepsluis_m3s.loc[wb_Bergsediepsluis_m3s["Tijdstip"] == mod_model_iteratie_tijd,\
		wb_Bergsediepsluis_m3s.columns[1]].values[0]
	Debiet_Kreekraksluis = wb_Kreekraksluis_m3s.loc[wb_Kreekraksluis_m3s["Tijdstip"] == mod_model_iteratie_tijd,\
		wb_Kreekraksluis_m3s.columns[1]].values[0]
	Debiet_wvr_Hollandse_Delta = wb_wvr_Hollandse_Delta_m3s.loc[wb_wvr_Hollandse_Delta_m3s["Tijdstip"] == mod_model_iteratie_tijd,\
		wb_wvr_Hollandse_Delta_m3s.columns[1]].values[0]
	Debiet_wvr_Brabantse_Delta = wb_wvr_Brabantse_Delta_m3s.loc[wb_wvr_Brabantse_Delta_m3s["Tijdstip"] == mod_model_iteratie_tijd,\
		wb_wvr_Brabantse_Delta_m3s.columns[1]].values[0]
	Debiet_wvr_Scheldestromen = wb_wvr_Scheldestromen_m3s.loc[wb_wvr_Scheldestromen_m3s["Tijdstip"] == mod_model_iteratie_tijd,\
		wb_wvr_Scheldestromen_m3s.columns[1]].values[0]


	#Neerslag en verdamping in MM
	Neerslag_VZM_mmd = wb_Neerslag_VZM_mmd.loc[wb_Neerslag_VZM_mmd["Tijdstip"] == mod_model_iteratie_tijd,\
						wb_Neerslag_VZM_mmd.columns[1]].values[0]
	Verdamping_VZM_mmd = wb_Verdamping_VZM_mmd.loc[wb_Verdamping_VZM_mmd["Tijdstip"] == mod_model_iteratie_tijd,\
						wb_Verdamping_VZM_mmd.columns[1]].values[0]
	Kwel_VZM_mmd       = 0
	
	#Debiet_compl
	Debiet_IN = Debiet_Volkeraksluizen + Debiet_Dintel + Debiet_Vliet
	Debiet_UIT_zonder_BSS_vc = Debiet_Krammersluizen + Debiet_Bergsediepsluis + Debiet_Kreekraksluis +\
			Debiet_wvr_Hollandse_Delta + Debiet_wvr_Brabantse_Delta + Debiet_wvr_Scheldestromen

	#Limiet Bathse Spuisluis
	#Selecteer de waterstanden van toepassing voor die dag
	tijd_mask_dag = (waterstand_Bath["Tijdstip"] >= mod_model_iteratie_tijd) &\
					(waterstand_Bath["Tijdstip"] < volgende_mod_model_iteratie_tijd)
	waterstanden_tussentijdstappen_Bath =  waterstand_Bath.loc[tijd_mask_dag, waterstand_Bath.columns[1]].values.tolist()
	#loop over deze waterstanden
	Alle_debieten_afvoer_mogelijk_KSL = []
	tussentijdstap = mod_model_iteratie_tijd
	for huidige_waterstand_Bath in waterstanden_tussentijdstappen_Bath:
		huidige_waterstand_Bath_m = huidige_waterstand_Bath / 100.0
		lager_dan_VZM = huidige_waterstand_Bath_m < waterstand_VZM_huidig
		Debiet_afvoer_mogelijk_KSL = lager_dan_VZM * (doorstroomoppervlak_m2 * afvoercoefficient *\
			 math.sqrt(2.0*9.81* abs(huidige_waterstand_Bath_m - waterstand_VZM_huidig))) 
		Alle_debieten_afvoer_mogelijk_KSL.append(Debiet_afvoer_mogelijk_KSL)
		overzicht_debiet_KSL_mogelijk_bestand.append([tussentijdstap.strftime("%Y-%m-%d %H:%M"), str(huidige_waterstand_Bath_m),\
		 	str(waterstand_VZM_huidig), str(Debiet_afvoer_mogelijk_KSL)])

		#volgende tijdstap
		tussentijdstap = tussentijdstap + datetime.timedelta(minutes = tijdstap_waterstand_Bath)

	Debiet_Bathse_Spuisluis_mogelijk = sum(Alle_debieten_afvoer_mogelijk_KSL) / len(waterstanden_tussentijdstappen_Bath)


	#Bathse spuisluis
	Debiet_Bathse_Spuisluis = Debiet_IN -	Debiet_UIT_zonder_BSS_vc +\
			(Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * Totaal_oppv_m2 / 86400

	if((waterstand_VZM_streefwaarde - waterstand_VZM_huidig) < -0.05):
		Debiet_Bathse_Spuisluis_vc = Debiet_Bathse_Spuisluis - -0.05 * Totaal_oppv_m2 / 86400
	elif((waterstand_VZM_streefwaarde - waterstand_VZM_huidig) > 0.05):
		Debiet_Bathse_Spuisluis_vc = Debiet_Bathse_Spuisluis - 0.05 * Totaal_oppv_m2 / 86400
	else: 
		Debiet_Bathse_Spuisluis_vc = Debiet_Bathse_Spuisluis - (waterstand_VZM_streefwaarde - waterstand_VZM_huidig) *\
									Totaal_oppv_m2 / 86400

	Debiet_Bathse_Spuisluis = max(0, min(Debiet_Bathse_Spuisluis_mogelijk, Debiet_Bathse_Spuisluis_vc))

	#Krammersluizen
	#Correctie voor waterafvoer Krammersluizen bij te lage waterstand
	Debiet_Krammersluizen_zonder_spui = Debiet_Krammersluizen - 9.0
	inv_Debiet_Bathse_Spuisluis_vc = -1.0 * Debiet_Bathse_Spuisluis_vc
	if(Debiet_Bathse_Spuisluis_vc < 0):
		# als het debiet dat te weinig is bij de Bathse Spuisluis (uitzaking waterpeil), kleiner is dan het debiet gebruikt voor sluisoperatie krammersluis
		# dan wordt dit geminderd op de sluisoperatie, anders stopt de sluisoperatie. Spuien bij de Krammersluizen blijft doorgaan.
		Debiet_Krammersluizen_nc = min(Debiet_Krammersluizen, (Debiet_Krammersluizen - min(inv_Debiet_Bathse_Spuisluis_vc, Debiet_Krammersluizen_zonder_spui)))
	else:
		Debiet_Krammersluizen_nc = Debiet_Krammersluizen


	#Berekening Debiet_Uit en waterstanden adhv correcties
	Debiet_UIT = Debiet_Krammersluizen_nc + Debiet_Bergsediepsluis + Debiet_Kreekraksluis +\
			Debiet_wvr_Hollandse_Delta + Debiet_wvr_Brabantse_Delta + Debiet_wvr_Scheldestromen +\
			Debiet_Bathse_Spuisluis

	waterstand_VZM_nieuw =  waterstand_VZM_huidig + (Debiet_IN - Debiet_UIT) * 86400 / Totaal_oppv_m2 +\
								(Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001

	waterstand_verandering = waterstand_VZM_nieuw - waterstand_VZM_huidig



	#bereken bakje I. Krammer-Volkerak Oost 			       
	# Krammer-Volkerak Oost = + Volkeraksluizen + Dintel + Neerslag - Verdamping + Waterstandsverschil - (I -> II) 
	atmosferische_verandering_I_m3s = (Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * I_oppv_m2 / 86400
	waterstandberging_I_m3s = waterstand_verandering * I_oppv_m2 / 86400
	Debiet_Bakje_I_to_II = Debiet_Volkeraksluizen + Debiet_Dintel + atmosferische_verandering_I_m3s - waterstandberging_I_m3s
	#bereken bakje II. Krammer-Volkerak Midden	
	# Krammer-Volkerak Midden = +(I -> II) + Vliet - Watervraag Hollandse Delta + Neerslag - Verdamping + Waterstandsverschil	- (II -> III) 
	atmosferische_verandering_II_m3s = (Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * II_oppv_m2 / 86400	
	waterstandberging_II_m3s = waterstand_verandering * II_oppv_m2 / 86400
	Debiet_Bakje_II_to_III = Debiet_Bakje_I_to_II + Debiet_Vliet - Debiet_wvr_Hollandse_Delta + atmosferische_verandering_II_m3s - waterstandberging_II_m3s
	
	#bereken bakje IV. Krammer-Volkerak West
	#Krammer-Volkerak West = - Krammersluizen (water) + Krammersluizen (zout) + Neerslag - Verdamping + Waterstandsverschil– (IV -> III)
	atmosferische_verandering_IV_m3s = (Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * IV_oppv_m2 / 86400	
	waterstandberging_IV_m3s = waterstand_verandering * IV_oppv_m2 / 86400
	Debiet_Bakje_IV_to_X   = Debiet_Krammersluizen_nc
	Debiet_Bakje_IV_to_III = - Debiet_Bakje_IV_to_X + atmosferische_verandering_IV_m3s - waterstandberging_IV_m3s

	#bereken bakje III. Krammer-Volkerak Ingang Eendracht 
	# Krammer-Volkerak Ingang Eendracht = +(II -> III) + (IV -> III) + Neerslag - Verdamping + Waterstandsverschil - (III -> V)
	atmosferische_verandering_III_m3s = (Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * III_oppv_m2 / 86400	
	waterstandberging_III_m3s = waterstand_verandering * III_oppv_m2 / 86400
	Debiet_Bakje_III_to_V = Debiet_Bakje_II_to_III + Debiet_Bakje_IV_to_III + atmosferische_verandering_III_m3s - waterstandberging_III_m3s

	#bereken bakje V. Eendracht Noord
	# Eendracht Noord = +(III -> V) + Neerslag - Verdamping + Waterstandsverschil - 1/3 * Watervraag SchSt + Kwel - (V -> VI)
	# NB. KWEL ZIT NOG NIET IN HUIDIG MODEL
	atmosferische_verandering_V_m3s = (Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * V_oppv_m2 / 86400
	waterstandberging_V_m3s = waterstand_verandering * V_oppv_m2 / 86400
	Debiet_Bakje_V_to_VI = Debiet_Bakje_III_to_V - 0.5 * Debiet_wvr_Scheldestromen + atmosferische_verandering_V_m3s - waterstandberging_V_m3s

	#bereken bakje VI. Eendracht Zuid	
	# Eendracht Zuid = +(V -> VI) + Neerslag - Verdamping + Waterstandsverschil - 1/3 * Watervraag SchSt + Kwel - (VI -> VII)
	# NB. KWEL ZIT NOG NIET IN HUIDIG MODEL
	atmosferische_verandering_VI_m3s = (Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * VI_oppv_m2 / 86400
	waterstandberging_VI_m3s = waterstand_verandering * VI_oppv_m2 / 86400
	Debiet_Bakje_VI_to_VII = Debiet_Bakje_V_to_VI - 0.5 * Debiet_wvr_Scheldestromen + atmosferische_verandering_VI_m3s - waterstandberging_VI_m3s 
	
	#bereken bakje VII. Zoommeer
	# Zoommeer = +(VI -> VII) - Bergse diepsluis (water) + Bergse diepsluis (zout) - Watervraag BD - 1/3 * Watervraag SchSt + Kwel - (VII -> VIII)
	# NB. KWEL ZIT NOG NIET IN HUIDIG MODEL
	atmosferische_verandering_VII_m3s = (Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * VII_oppv_m2 / 86400
	waterstandberging_VII_m3s = waterstand_verandering * VII_oppv_m2 / 86400
	Debiet_Bakje_VII_to_VIII = Debiet_Bakje_VI_to_VII - Debiet_Bergsediepsluis - Debiet_wvr_Brabantse_Delta +\
		 atmosferische_verandering_VII_m3s - waterstandberging_VII_m3s

	#bereken bakje VIII. Zoommeer Zuid
	# Zoommeer Zuid	= +(VII -> VIII) - Kreekraksluizen + Neerslag - Verdamping + Waterstandsverschil + Kwel - (VIII -> IX)
	# NB. KWEL ZIT NOG NIET IN HUIDIG MODEL
	atmosferische_verandering_VIII_m3s = (Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * VIII_oppv_m2 / 86400
	waterstandberging_VIII_m3s = waterstand_verandering * VIII_oppv_m2 / 86400
	Debiet_Bakje_VIII_to_IX = Debiet_Bakje_VII_to_VIII - Debiet_Kreekraksluis +\
								atmosferische_verandering_VIII_m3s - waterstandberging_VIII_m3s
	

	#bereken bakje IX. Bathse Spuikanaal
	# Bathse Spuikanaal = +(VIII -> IX) - Bathse spuisluis (water) + Bathse spuisluis (zout) + Neerslag - Verdamping + Waterstandsverschil
	atmosferische_verandering_IX_m3s = (Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * VII_oppv_m2 / 86400
	waterstandberging_IX_m3s = waterstand_verandering * IX_oppv_m2 / 86400
	
	#bereken bakje X. Voorhaven Krammersluizen
	# Voorhaven Krammersluizen 	= Krammersluizen (water) + Krammersluizen (zout)
	#atmosferische_verandering_X_m3s = (Neerslag_VZM_mmd - Verdamping_VZM_mmd) * 0.001 * X_oppv_m2 / 86400
	#waterstandberging_X_m3s = waterstand_verandering * X_oppv_m2 / 86400
	
	#maak een overzicht voor snelle controle balansen
	Debiet_IN             = Debiet_Volkeraksluizen + Debiet_Dintel + Debiet_Vliet

	Debiet_UIT            = Debiet_Krammersluizen_nc + Debiet_Bergsediepsluis + Debiet_Kreekraksluis +\
				              Debiet_Bathse_Spuisluis + Debiet_wvr_Hollandse_Delta + Debiet_wvr_Brabantse_Delta + Debiet_wvr_Scheldestromen
	
	Debiet_ATMOSFEER      = atmosferische_verandering_I_m3s + atmosferische_verandering_II_m3s + atmosferische_verandering_III_m3s +\
							atmosferische_verandering_IV_m3s + atmosferische_verandering_V_m3s + atmosferische_verandering_VI_m3s +\
							atmosferische_verandering_VII_m3s + atmosferische_verandering_VIII_m3s + atmosferische_verandering_IX_m3s

	Debiet_Waterstand_VERANDERING = waterstandberging_I_m3s + waterstandberging_II_m3s + waterstandberging_III_m3s +\
							 waterstandberging_IV_m3s +  waterstandberging_V_m3s +  waterstandberging_VI_m3s +\
							 waterstandberging_VII_m3s + waterstandberging_VIII_m3s + waterstandberging_IX_m3s
	
	BALANS = Debiet_IN - Debiet_UIT + Debiet_ATMOSFEER - Debiet_Waterstand_VERANDERING

	#Maak een overzicht van de Volumes
	Volume_Bakje_I    = (I_diepte_m + waterstand_VZM_huidig)    *    I_oppv_m2
	Volume_Bakje_II   = (II_diepte_m + waterstand_VZM_huidig)   *   II_oppv_m2
	Volume_Bakje_III  = (III_diepte_m + waterstand_VZM_huidig)  *  III_oppv_m2
	Volume_Bakje_IV   = (IV_diepte_m + waterstand_VZM_huidig)   *   IV_oppv_m2
	Volume_Bakje_V    = (V_diepte_m + waterstand_VZM_huidig)    *    V_oppv_m2
	Volume_Bakje_VI   = (VI_diepte_m + waterstand_VZM_huidig)   *   VI_oppv_m2
	Volume_Bakje_VII  = (VII_diepte_m + waterstand_VZM_huidig)  *  VII_oppv_m2
	Volume_Bakje_VIII = (VIII_diepte_m + waterstand_VZM_huidig) * VIII_oppv_m2
	Volume_Bakje_IX   = (IX_diepte_m + waterstand_VZM_huidig)   *   IX_oppv_m2
	Volume_Bakje_X    = (X_diepte_m + waterstand_initeel)       *    X_oppv_m2   #Constant volume voor Bakje X

	#bereken Neerslag
	Neerslag_Bakje_I    = Neerslag_VZM_mmd * 0.001 * I_oppv_m2 / 86400
	Neerslag_Bakje_II   = Neerslag_VZM_mmd * 0.001 * II_oppv_m2 / 86400
	Neerslag_Bakje_III  = Neerslag_VZM_mmd * 0.001 * III_oppv_m2 / 86400
	Neerslag_Bakje_IV   = Neerslag_VZM_mmd * 0.001 * IV_oppv_m2 / 86400
	Neerslag_Bakje_V    = Neerslag_VZM_mmd * 0.001 * V_oppv_m2 / 86400
	Neerslag_Bakje_VI   = Neerslag_VZM_mmd * 0.001 * VI_oppv_m2 / 86400
	Neerslag_Bakje_VII  = Neerslag_VZM_mmd * 0.001 * VII_oppv_m2 / 86400
	Neerslag_Bakje_VIII = Neerslag_VZM_mmd * 0.001 * VIII_oppv_m2 / 86400
	Neerslag_Bakje_IX   = Neerslag_VZM_mmd * 0.001 * IX_oppv_m2 / 86400

	#bereken Verdamping
	Verdamping_Bakje_I    = Verdamping_VZM_mmd * 0.001 * I_oppv_m2 / 86400
	Verdamping_Bakje_II   = Verdamping_VZM_mmd * 0.001 * II_oppv_m2 / 86400
	Verdamping_Bakje_III  = Verdamping_VZM_mmd * 0.001 * III_oppv_m2 / 86400
	Verdamping_Bakje_IV   = Verdamping_VZM_mmd * 0.001 * IV_oppv_m2 / 86400
	Verdamping_Bakje_V    = Verdamping_VZM_mmd * 0.001 * V_oppv_m2 / 86400
	Verdamping_Bakje_VI   = Verdamping_VZM_mmd * 0.001 * VI_oppv_m2 / 86400
	Verdamping_Bakje_VII  = Verdamping_VZM_mmd * 0.001 * VII_oppv_m2 / 86400
	Verdamping_Bakje_VIII = Verdamping_VZM_mmd * 0.001 * VIII_oppv_m2 / 86400
	Verdamping_Bakje_IX   = Verdamping_VZM_mmd * 0.001 * IX_oppv_m2 / 86400


	#Maak zout overzicht (van kg/s in g/s en kwel in gelijke delen verdeeld over deel bakjes)
	#"Bathse spuisluis", "Bergse diepsluis", "Krammersluizen",	"Kwel (Eendracht Nood, Eendracht Zuid, Zoommeer, Zoommeer Zuid)"
	Zout_Bathse_spuisluis = zb_Bathse_spuisluis_KGS.loc[zb_Bathse_spuisluis_KGS["Tijdstip"] == mod_model_iteratie_tijd,\
		zb_Bathse_spuisluis_KGS.columns[1]].values[0] * 1000.0
	Zout_Bergse_diepsluis = zb_Bergsediepsluis_KGS.loc[zb_Bergsediepsluis_KGS["Tijdstip"] == mod_model_iteratie_tijd,\
		zb_Bergsediepsluis_KGS.columns[1]].values[0] * 1000.0
	Zout_Krammersluizen = zb_Krammersluizen_KGS.loc[zb_Krammersluizen_KGS["Tijdstip"] == mod_model_iteratie_tijd,\
	 	zb_Krammersluizen_KGS.columns[1]].values[0]  * 1000.0
	
	Zout_Kwel_Krammer_Volkerak_West = zb_Kwel_VZM_KGS.loc[zb_Kwel_VZM_KGS["Tijdstip"] == mod_model_iteratie_tijd,\
	 	zb_Kwel_VZM_KGS.columns[1]].values[0]  * Kwel_factor_Krammer_Volkerak_West * 1000.0
	Zout_Kwel_Eendracht_Noord = zb_Kwel_VZM_KGS.loc[zb_Kwel_VZM_KGS["Tijdstip"] == mod_model_iteratie_tijd,\
	 	zb_Kwel_VZM_KGS.columns[1]].values[0]  * Kwel_factor_Eendracht_Noord * 1000.0
	Zout_Kwel_Eendracht_Zuid = zb_Kwel_VZM_KGS.loc[zb_Kwel_VZM_KGS["Tijdstip"] == mod_model_iteratie_tijd,\
	 	zb_Kwel_VZM_KGS.columns[1]].values[0]  * Kwel_factor_Eendracht_Zuid * 1000.0
	Zout_Kwel_Zoommeer = zb_Kwel_VZM_KGS.loc[zb_Kwel_VZM_KGS["Tijdstip"] == mod_model_iteratie_tijd,\
		zb_Kwel_VZM_KGS.columns[1]].values[0]  * Kwel_factor_Zoommeer  * 1000.0
	Zout_Kwel_Zoommeer_Zuid = zb_Kwel_VZM_KGS.loc[zb_Kwel_VZM_KGS["Tijdstip"] == mod_model_iteratie_tijd,\
	 	zb_Kwel_VZM_KGS.columns[1]].values[0]  * Kwel_factor_Zoommeer_Zuid * 1000.0


	#BEWAAR RESULTATEN
	invoer_bestand.append([model_iteratie_tijd.strftime("%Y-%m-%d %H:%M"), str(waterstand_VZM_streefwaarde), str(waterstand_VZM_huidig),\
		str(Debiet_Volkeraksluizen), str(Debiet_Dintel), str(Debiet_Vliet), str(Debiet_Krammersluizen), str(Debiet_Krammersluizen_nc),\
		str(Debiet_Bergsediepsluis), str(Debiet_Kreekraksluis), str(Debiet_Bathse_Spuisluis_vc), str(Debiet_Bathse_Spuisluis),\
		str(Debiet_wvr_Hollandse_Delta), str(Debiet_wvr_Brabantse_Delta), str(Debiet_wvr_Scheldestromen), \
		str(Neerslag_VZM_mmd),str(Verdamping_VZM_mmd), str(Kwel_VZM_mmd)])
	invoer_zout_bestand.append([model_iteratie_tijd.strftime("%Y-%m-%d %H:%M"), str(Zout_Bathse_spuisluis),\
		str(Zout_Bergse_diepsluis), str(Zout_Krammersluizen), str(Zout_Kwel_Krammer_Volkerak_West), str(Zout_Kwel_Eendracht_Noord),\
		str(Zout_Kwel_Eendracht_Zuid), str(Zout_Kwel_Zoommeer), str(Zout_Kwel_Zoommeer_Zuid)])
	balans_bestand.append([model_iteratie_tijd.strftime("%Y-%m-%d %H:%M"), str(Debiet_IN),\
		str(Debiet_UIT), str(Debiet_ATMOSFEER),str(Debiet_Waterstand_VERANDERING), str(BALANS)])
	overzicht_bestand.append([model_iteratie_tijd.strftime("%Y-%m-%d %H:%M"), str(Debiet_Bakje_I_to_II),\
					 str(Debiet_Bakje_II_to_III), str(Debiet_Bakje_III_to_V), str(Debiet_Bakje_IV_to_III), str(Debiet_Bakje_V_to_VI),\
					 str(Debiet_Bakje_VI_to_VII), str(Debiet_Bakje_VII_to_VIII), str(Debiet_Bakje_VIII_to_IX), str(Debiet_Bakje_IV_to_X)])
	overzicht_neerslag_bestand.append([model_iteratie_tijd.strftime("%Y-%m-%d %H:%M"), str(Neerslag_Bakje_I),\
					 str(Neerslag_Bakje_II), str(Neerslag_Bakje_III), str(Neerslag_Bakje_IV), str(Neerslag_Bakje_V),\
					 str(Neerslag_Bakje_VI), str(Neerslag_Bakje_VII), str(Neerslag_Bakje_VIII), str(Neerslag_Bakje_IX)])
	overzicht_verdamping_bestand.append([model_iteratie_tijd.strftime("%Y-%m-%d %H:%M"), str(Verdamping_Bakje_I),\
					 str(Verdamping_Bakje_II), str(Verdamping_Bakje_III), str(Verdamping_Bakje_IV), str(Verdamping_Bakje_V),\
					 str(Verdamping_Bakje_VI), str(Verdamping_Bakje_VII), str(Verdamping_Bakje_VIII), str(Verdamping_Bakje_IX)])

	overzicht_volumes_bestand.append([model_iteratie_tijd.strftime("%Y-%m-%d %H:%M"), str(Volume_Bakje_I), str(Volume_Bakje_II),\
					 str(Volume_Bakje_III), str(Volume_Bakje_IV), str(Volume_Bakje_V), str(Volume_Bakje_VI),\
					 str(Volume_Bakje_VII), str(Volume_Bakje_VIII), str(Volume_Bakje_IX), str(Volume_Bakje_X)])
	#log_bestand


#--------------Schrijf de bestanden weg--------------------------------------------------------------#

#schrijf invoer bestand
invoer_bestand_file =  open("output/Invoer_bakjesmodel_VZM.csv","w")
invoer_bestand_file.writelines("%s\n" % ";".join(line) for line in invoer_bestand)
invoer_bestand_file.close()

#schrijf invoer zout bestand
invoer_bestand_file =  open("output/Invoer_zout_bakjesmodel_VZM.csv","w")
invoer_bestand_file.writelines("%s\n" % ";".join(line) for line in invoer_zout_bestand)
invoer_bestand_file.close()

#schrijf balans bestand
balans_bestand_file =  open("output/Controle_overzicht_bakjesmodel_VZM.csv","w")
balans_bestand_file.writelines("%s\n" % ";".join(line) for line in balans_bestand)
balans_bestand_file.close()

#schrijf overzicht bestand
overzicht_bestand_file =  open("output/Waterbalans_Debiet_uitwisseling_bakjesmodel_VZM.csv","w")
overzicht_bestand_file.writelines("%s\n" % ";".join(line) for line in overzicht_bestand)
overzicht_bestand_file.close()

#schrijf overzicht debiet mogelijk bij Krammersluizen bestand
overzicht_debiet_KSL_mogelijk_bestand
overzicht_debiet_KSL_mogelijk_bestand_file =  open("output/Waterbalans_Debiet_mogelijk_bij_Krammersluizen_bakjesmodel_VZM.csv","w")
overzicht_debiet_KSL_mogelijk_bestand_file.writelines("%s\n" % ";".join(line) for line in overzicht_debiet_KSL_mogelijk_bestand)
overzicht_debiet_KSL_mogelijk_bestand_file.close()

#schrijf overzicht neerslag bestand
overzicht_neerslag_bestand_file =  open("output/Waterbalans_Debiet_Neerslag_bakjesmodel_VZM.csv","w")
overzicht_neerslag_bestand_file.writelines("%s\n" % ";".join(line) for line in overzicht_neerslag_bestand)
overzicht_neerslag_bestand_file.close()

#schrijf overzicht neerslag bestand
overzicht_verdamping_bestand_file =  open("output/Waterbalans_Debiet_Verdamping_bakjesmodel_VZM.csv","w")
overzicht_verdamping_bestand_file.writelines("%s\n" % ";".join(line) for line in overzicht_verdamping_bestand)
overzicht_verdamping_bestand_file.close()

#schrijf overzicht volumes bestand
overzicht_volumes_bestand_file =  open("output/Waterbalans_Volumes_bakjes_bakjesmodel_VZM.csv","w")
overzicht_volumes_bestand_file.writelines("%s\n" % ";".join(line) for line in overzicht_volumes_bestand)
overzicht_volumes_bestand_file.close()

#schrijf overzicht bestand
log_file =  open("output/log_bakjesmodel_VZM.txt","w")
log_file.writelines("%s\n" % line[0] for line in log_bestand)
log_file.close()

print("Done.")