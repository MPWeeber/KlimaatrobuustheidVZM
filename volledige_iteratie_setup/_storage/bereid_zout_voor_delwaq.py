'''
Voorbereiding input Simpel bakjesmodel Zout Volkerak-Zoommeer

Created by Arno Nolte & Marc Weeber (Deltares)


Balansen

I. Krammer-Volkerak Oost 			        = + Volkeraksluizen + Dintel + Neerslag - Verdamping + Waterstandsverschil - (I -> II) 
II. Krammer-Volkerak Midden			        = +(I -> II) + Vliet - Watervraag Hollandse Delta + Neerslag - Verdamping + Waterstandsverschil	- (II -> III) 
III. Krammer-Volkerak Ingang Eendracht     	= +(II -> III) + (IV -> III) + Neerslag - Verdamping + Waterstandsverschil - (III -> V)
IV. Krammer-Volkerak West			        = - Krammersluizen (water) + Krammersluizen (zout) + Neerslag - Verdamping + Waterstandsverschil– (IV -> III)
V. Eendracht Noord				            = +(III -> V) + Neerslag - Verdamping + Waterstandsverschil - Watervraag SchSt + Kwel - (V -> VI)
VI. Eendracht Zuid				            = +(V -> VI) + Neerslag - Verdamping + Waterstandsverschil - Watervraag SchSt + Kwel - (VI -> VII)
VII. Zoommeer				                = +(VI -> VII) - Bergse diepsluis (water) + Bergse diepsluis (zout) - Watervraag BD - Watervraag SchSt + Kwel - (VII -> VIII)
VIII. Zoommeer Zuid				            = +(VII -> VIII) - Kreekraksluizen + Neerslag - Verdamping + Waterstandsverschil + Kwel - (VIII -> IX)
IX. Bathse Spuikanaal				        = +(VIII -> IX) - Bathse spuisluis (water) + Bathse spuisluis (zout) + Neerslag - Verdamping + Waterstandsverschil






'''

import sys

import pandas as pd
import datetime
import dateutil

simulatie_dagen = 731


#lees automatisch het data format
dateparse = lambda x: datetime.datetime.strptime(x,"%Y-%m-%d %H:%M")

def read_file(file_path):
	#leeas de  csv file met pandas en converteer de datum
	df = pd.read_csv(file_path, sep = ";",\
		 parse_dates=['Tijdstip'], date_parser=dateparse, skiprows= [1])
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

(Invoer          , tijdstap_Invoer        ) = read_file("output/Invoer_bakjesmodel_VZM.csv")
(Invoer_Zout     , tijdstap_Invoer_Zout   ) = read_file("output/Invoer_zout_bakjesmodel_VZM.csv")
(Volumes_VZM     , tijdstap_Volumes_VZM   ) = read_file("output/Waterbalans_Volumes_bakjes_bakjesmodel_VZM.csv")
(Flow_VZM        , tijdstap_Flow_VZM      ) = read_file("output/Waterbalans_Debiet_uitwisseling_bakjesmodel_VZM.csv")
(Neerslag_VZM    , tijdstap_Neerslag_VZM  ) = read_file("output/Waterbalans_Debiet_Neerslag_bakjesmodel_VZM.csv")
(Verdamping_VZM  , tijdstap_Verdamping_VZM) = read_file("output/Waterbalans_Debiet_Verdamping_bakjesmodel_VZM.csv")

#Flow_bakjes.dat file
nr_of_time_points_flows_bakjes = int((simulatie_dagen * 1440) / tijdstap_Flow_VZM)
flows_bakjes_dat = []
flows_bakjes_dat.append(["   3  ; time dependent"])
flows_bakjes_dat.append([" 1 ; 1=block, 2=linear"])
flows_bakjes_dat.append(["    9   ; # of exchanges in this file"])
flows_bakjes_dat.append(["    1    2    3    4    5    6    7    8    9"])
flows_bakjes_dat.append(["   "+ str(nr_of_time_points_flows_bakjes) + "  ; nr. of time points"])
flows_bakjes_dat.append(["    1.0 ; scale factor"])

#Flow_kunstwerken.dat file
nr_of_time_points_flows_kunstwerken = int((simulatie_dagen * 1440) / tijdstap_Invoer)
flows_kunstwerken_dat = []
#flows_kunstwerken_dat.append(["   3  ; time dependent"])
flows_kunstwerken_dat.append([" 1 ; 1=block, 2=linear"])
flows_kunstwerken_dat.append(["   11   ; # of exchanges in this file"])
flows_kunstwerken_dat.append(["    10    11    12    13    14    15    16    17    18    19    20"])
flows_kunstwerken_dat.append(["   "+ str(nr_of_time_points_flows_kunstwerken) + "  ; nr. of time points"])
flows_kunstwerken_dat.append(["    1.0 ; scale factor"])

#Flow_neerslag.dat file
nr_of_time_points_flows_neerslag = int((simulatie_dagen * 1440) / tijdstap_Neerslag_VZM)
flows_neerslag_dat = []
#flows_neerslag_dat.append(["   3  ; time dependent"])
flows_neerslag_dat.append([" 1 ; 1=block, 2=linear"])
flows_neerslag_dat.append(["    9   ; # of exchanges in this file"])
flows_neerslag_dat.append(["    21    22    23    24    25    26    27    28    29"])
flows_neerslag_dat.append(["   "+ str(nr_of_time_points_flows_neerslag) + "  ; nr. of time points"])
flows_neerslag_dat.append(["    1.0 ; scale factor"])

#Flow_verdamping.dat file
nr_of_time_points_flows_verdamping = int((simulatie_dagen * 1440) / tijdstap_Verdamping_VZM)
flows_verdamping_dat = []
#flows_verdamping_dat.append(["   3  ; time dependent"])
flows_verdamping_dat.append([" 1 ; 1=block, 2=linear"])
flows_verdamping_dat.append(["    9   ; # of exchanges in this file"])
flows_verdamping_dat.append(["    30    31    32    33    34    35    36    37    38"])
flows_verdamping_dat.append(["   "+ str(nr_of_time_points_flows_verdamping) + "  ; nr. of time points"])
flows_verdamping_dat.append(["    1.0 ; scale factor"])

#Volumes.dat file
nr_of_time_points_volumes = int((simulatie_dagen * 1440) / tijdstap_Volumes_VZM)
vol_dat = []
vol_dat.append(["   3  ; time dependent"])
vol_dat.append([" 2 ; 1=block, 2=linear"])
vol_dat.append(["   10   ; # of segments in this file"])
vol_dat.append(["    1    2    3    4    5    6    7    8    9    10"])
vol_dat.append(["   "+ str(nr_of_time_points_volumes) + "  ; nr. of time points"])
vol_dat.append(["    1.0e7 ; scale factor"])

#; Zoutvracht_Bathse_spuisluis_IDxxx.inc
Bathse_spuisluis = []
Bathse_spuisluis.append(["; Zoutvracht_Bathse_spuisluis_IDxxx.inc"])

#; Zoutvracht_Bergse_diepsluis_IDxxx.inc
Bergse_diepsluis = []
Bergse_diepsluis.append(["; Zoutvracht_Bergse_diepsluis_IDxxx.inc"])

#; Zoutvracht_Krammersluizen_IDxxx.inc
Krammersluizen = []
Krammersluizen.append(["; Zoutvracht_Krammersluizen_IDxxx.inc"])

#; Zoutvracht_Kwel_IDxxx.inc
Kwel = []
Kwel.append(["; Zoutvracht_Kwel_IDxxx.inc"])

for model_iteratie_tijd in Invoer_Zout.iloc[:,0]:
	#make a ddhhmmss (start jaar is in vorig script omgezet naar 2018)
	cur_time = (model_iteratie_tijd - datetime.datetime.strptime("2018-01-01 00:00", "%Y-%m-%d %H:%M"))
	seconds_time = cur_time.total_seconds()

	dd_time = cur_time.days
	dd_seconds = dd_time * (24*60*60)
	hh_time = int((seconds_time - dd_seconds) / (60*60))
	ddhh_seconds = dd_seconds + hh_time * (60*60)
	mm_time    = int((seconds_time - ddhh_seconds) / 60)
	ddhhmm_seconds = ddhh_seconds + mm_time * 60
	ss_time    = int((seconds_time - ddhhmm_seconds))

	#make time format
	dd_str = ""
	hh_str = ""
	mm_str = ""
	ss_str = ""
	if(not dd_time == 0):
		dd_str = str(dd_time)
	if(not hh_time == 0):
		if(hh_time < 10 & dd_time == 0):
			hh_str = str(hh_time)
		elif(hh_time < 10 & dd_time > 0):
			hh_str = "0" + str(hh_time)
		else:
			hh_str = str(hh_time)
	if(hh_time == 0 and (dd_time > 0)):
		hh_str = "00"

	if(not mm_time == 0):
		if(mm_time < 10 & hh_time == 0):
			mm_str = str(mm_time)
		elif(mm_time < 10 & hh_time > 0):
			mm_str = "0" + str(mm_time)
		else:
			mm_str = str(mm_time)

	if(mm_time == 0 and (hh_time > 0 or dd_time > 0)):
		mm_str = "00"

	if(not ss_time == 0 ):
		if(ss_time < 10 & mm_time == 0):
			ss_str = str(ss_time)
		elif(ss_time < 10 & mm_time > 0):
			ss_str = "0" + str(ss_time)
		else:
			ss_str = str(ss_time)

	if(ss_time == 0 and (mm_time > 0 or hh_time > 0 or dd_time > 0)):
		ss_str = "00"

	time_stamp = dd_str + hh_str +mm_str + ss_str
	if(time_stamp == ""):
		time_stamp = "0"

	vol_bakje_I    = Volumes_VZM.loc[Volumes_VZM["Tijdstip"] == model_iteratie_tijd, "I"].values[0] / 10000000
	vol_bakje_II   = Volumes_VZM.loc[Volumes_VZM["Tijdstip"] == model_iteratie_tijd, "II"].values[0] / 10000000
	vol_bakje_III  = Volumes_VZM.loc[Volumes_VZM["Tijdstip"] == model_iteratie_tijd, "III"].values[0] / 10000000
	vol_bakje_IV   = Volumes_VZM.loc[Volumes_VZM["Tijdstip"] == model_iteratie_tijd, "IV"].values[0] / 10000000
	vol_bakje_V    = Volumes_VZM.loc[Volumes_VZM["Tijdstip"] == model_iteratie_tijd, "V"].values[0] / 10000000
	vol_bakje_VI   = Volumes_VZM.loc[Volumes_VZM["Tijdstip"] == model_iteratie_tijd, "VI"].values[0] / 10000000
	vol_bakje_VII  = Volumes_VZM.loc[Volumes_VZM["Tijdstip"] == model_iteratie_tijd, "VII"].values[0] / 10000000
	vol_bakje_VIII = Volumes_VZM.loc[Volumes_VZM["Tijdstip"] == model_iteratie_tijd, "VIII"].values[0] / 10000000
	vol_bakje_IX   = Volumes_VZM.loc[Volumes_VZM["Tijdstip"] == model_iteratie_tijd, "IX"].values[0] / 10000000
	vol_bakje_X   = Volumes_VZM.loc[Volumes_VZM["Tijdstip"] == model_iteratie_tijd, "X"].values[0] / 10000000

	flow_bakje_I_II     = Flow_VZM.loc[Flow_VZM["Tijdstip"] == model_iteratie_tijd, "I -> II"].values[0]
	flow_bakje_II_III   = Flow_VZM.loc[Flow_VZM["Tijdstip"] == model_iteratie_tijd, "II -> III"].values[0]
	flow_bakje_III_V    = Flow_VZM.loc[Flow_VZM["Tijdstip"] == model_iteratie_tijd, "III -> V"].values[0]
	flow_bakje_IV_III   = Flow_VZM.loc[Flow_VZM["Tijdstip"] == model_iteratie_tijd, "IV -> III"].values[0]
	flow_bakje_V_VI     = Flow_VZM.loc[Flow_VZM["Tijdstip"] == model_iteratie_tijd, "V -> VI"].values[0]
	flow_bakje_VI_VII   = Flow_VZM.loc[Flow_VZM["Tijdstip"] == model_iteratie_tijd, "VI -> VII"].values[0]
	flow_bakje_VII_VIII = Flow_VZM.loc[Flow_VZM["Tijdstip"] == model_iteratie_tijd, "VII -> VIII"].values[0]
	flow_bakje_VIII_IX  = Flow_VZM.loc[Flow_VZM["Tijdstip"] == model_iteratie_tijd, "VIII -> IX"].values[0]
	flow_bakje_IV_X     = Flow_VZM.loc[Flow_VZM["Tijdstip"] == model_iteratie_tijd, "IV -> X"].values[0]

	flow_Volkeraksluizen               = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Volkeraksluizen"].values[0]
	flow_Dintel                        = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Dintel"].values[0]
	flow_Vliet                         = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Vliet"].values[0]
	flow_Krammersluizen                = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Krammersluizen (na correctie)"].values[0]
	flow_Bergse_diepsluis              = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Bergse diepsluis"].values[0]
	flow_Kreekraksluizen               = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Kreekraksluizen"].values[0]
	flow_Bathse_spuisluis              = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Bathse spuisluis"].values[0]
	flow_wvr_Hollandse_Delta           = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Watervraag Hollandse Delta"].values[0]
	flow_V_50perc_wvr_Scheldestromen   = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Watervraag Scheldestromen"].values[0] * 0.5
	flow_VII_50perc_wvr_Scheldestromen = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Watervraag Scheldestromen"].values[0] * 0.5
	flow_wvr_Brabantse_Delta           = Invoer.loc[Invoer["Tijdstip"] == model_iteratie_tijd, "Watervraag Brabantse Delta"].values[0] 

	flow_neerslag_bakje_I              = Neerslag_VZM.loc[Neerslag_VZM["Tijdstip"] == model_iteratie_tijd, "Neerslag_I"].values[0]  
	flow_neerslag_bakje_II             = Neerslag_VZM.loc[Neerslag_VZM["Tijdstip"] == model_iteratie_tijd, "Neerslag_II"].values[0]  
	flow_neerslag_bakje_III            = Neerslag_VZM.loc[Neerslag_VZM["Tijdstip"] == model_iteratie_tijd, "Neerslag_III"].values[0]  
	flow_neerslag_bakje_IV             = Neerslag_VZM.loc[Neerslag_VZM["Tijdstip"] == model_iteratie_tijd, "Neerslag_IV"].values[0]  
	flow_neerslag_bakje_V              = Neerslag_VZM.loc[Neerslag_VZM["Tijdstip"] == model_iteratie_tijd, "Neerslag_V"].values[0]  
	flow_neerslag_bakje_VI             = Neerslag_VZM.loc[Neerslag_VZM["Tijdstip"] == model_iteratie_tijd, "Neerslag_VI"].values[0]  
	flow_neerslag_bakje_VII            = Neerslag_VZM.loc[Neerslag_VZM["Tijdstip"] == model_iteratie_tijd, "Neerslag_VII"].values[0]  
	flow_neerslag_bakje_VIII           = Neerslag_VZM.loc[Neerslag_VZM["Tijdstip"] == model_iteratie_tijd, "Neerslag_VIII"].values[0]  
	flow_neerslag_bakje_IX             = Neerslag_VZM.loc[Neerslag_VZM["Tijdstip"] == model_iteratie_tijd, "Neerslag_IX"].values[0] 

	flow_verdamping_bakje_I              = Verdamping_VZM.loc[Verdamping_VZM["Tijdstip"] == model_iteratie_tijd, "Verdamping_I"].values[0]  
	flow_verdamping_bakje_II             = Verdamping_VZM.loc[Verdamping_VZM["Tijdstip"] == model_iteratie_tijd, "Verdamping_II"].values[0]  
	flow_verdamping_bakje_III            = Verdamping_VZM.loc[Verdamping_VZM["Tijdstip"] == model_iteratie_tijd, "Verdamping_III"].values[0]  
	flow_verdamping_bakje_IV             = Verdamping_VZM.loc[Verdamping_VZM["Tijdstip"] == model_iteratie_tijd, "Verdamping_IV"].values[0]  
	flow_verdamping_bakje_V              = Verdamping_VZM.loc[Verdamping_VZM["Tijdstip"] == model_iteratie_tijd, "Verdamping_V"].values[0]  
	flow_verdamping_bakje_VI             = Verdamping_VZM.loc[Verdamping_VZM["Tijdstip"] == model_iteratie_tijd, "Verdamping_VI"].values[0]  
	flow_verdamping_bakje_VII            = Verdamping_VZM.loc[Verdamping_VZM["Tijdstip"] == model_iteratie_tijd, "Verdamping_VII"].values[0]  
	flow_verdamping_bakje_VIII           = Verdamping_VZM.loc[Verdamping_VZM["Tijdstip"] == model_iteratie_tijd, "Verdamping_VIII"].values[0]  
	flow_verdamping_bakje_IX             = Verdamping_VZM.loc[Verdamping_VZM["Tijdstip"] == model_iteratie_tijd, "Verdamping_IX"].values[0] 

	Zout_Bathse_spuisluis           = Invoer_Zout.loc[Invoer_Zout["Tijdstip"] == model_iteratie_tijd, "Bathse spuisluis"].values[0]
	Zout_Bergse_diepsluis           = Invoer_Zout.loc[Invoer_Zout["Tijdstip"] == model_iteratie_tijd, "Bergse diepsluis"].values[0]
	Zout_Krammersluizen             = Invoer_Zout.loc[Invoer_Zout["Tijdstip"] == model_iteratie_tijd, "Krammersluizen"].values[0]
	Zout_Kwel_Krammer_Volkerak_West = Invoer_Zout.loc[Invoer_Zout["Tijdstip"] == model_iteratie_tijd, "Kwel_Krammer_Volkerak_West"].values[0]
	Zout_Kwel_Eendracht_Noord       = Invoer_Zout.loc[Invoer_Zout["Tijdstip"] == model_iteratie_tijd, "Kwel_Eendracht_Noord"].values[0]
	Zout_Kwel_Eendracht_Zuid        = Invoer_Zout.loc[Invoer_Zout["Tijdstip"] == model_iteratie_tijd, "Kwel_Eendracht_Zuid"].values[0]
	Zout_Kwel_Zoommeer              = Invoer_Zout.loc[Invoer_Zout["Tijdstip"] == model_iteratie_tijd, "Kwel_Zoommeer"].values[0]
	Zout_Kwel_Zoommeer_Zuid         = Invoer_Zout.loc[Invoer_Zout["Tijdstip"] == model_iteratie_tijd, "Kwel_Zoommeer_Zuid"].values[0]


	#update flows dat
	flows_bakjes_dat.append(["                   " + time_stamp + "   ; time in ddhhmmss"])
	flows_bakjes_dat.append(["   "+ str(float(flow_bakje_I_II))+" "+str(float(flow_bakje_II_III))+" "+str(float(flow_bakje_III_V))+" "+\
		str(float(flow_bakje_IV_III))+" "+str(float(flow_bakje_V_VI))+" "+str(float(flow_bakje_VI_VII))+" "+
		str(float(flow_bakje_VII_VIII))+" "+str(float(flow_bakje_VIII_IX))+" "+str(float(flow_bakje_IV_X))+" ; values"])

	#update flows kunstwerken dat
	flows_kunstwerken_dat.append(["                   " + time_stamp + "   ; time in ddhhmmss"])
	flows_kunstwerken_dat.append(["   "+ str(float(flow_Volkeraksluizen))+" "+str(float(flow_Dintel))+" "+str(float(flow_Vliet))+" "+\
		str(float(flow_Krammersluizen))+" "+str(float(flow_Bergse_diepsluis))+" "+str(float(flow_Kreekraksluizen))+" "+
		str(float(flow_Bathse_spuisluis))+" "+str(float(flow_wvr_Hollandse_Delta))+" "+str(float(flow_V_50perc_wvr_Scheldestromen))+" "+\
		str(float(flow_VII_50perc_wvr_Scheldestromen))+" "+str(float(flow_wvr_Brabantse_Delta))+" ; values"])

	#update flows neerslag dat
	flows_neerslag_dat.append(["                   " + time_stamp + "   ; time in ddhhmmss"])
	flows_neerslag_dat.append(["   "+ str(float(flow_neerslag_bakje_I))+" "+str(float(flow_neerslag_bakje_II))+" "+str(float(flow_neerslag_bakje_III))+" "+\
		str(float(flow_neerslag_bakje_IV))+" "+str(float(flow_neerslag_bakje_V))+" "+str(float(flow_neerslag_bakje_VI))+" "+
		str(float(flow_neerslag_bakje_VII))+" "+str(float(flow_neerslag_bakje_VIII))+" "+str(float(flow_neerslag_bakje_IX))+" ; values"])

	#update flows verdamping dat
	flows_verdamping_dat.append(["                   " + time_stamp + "   ; time in ddhhmmss"])
	flows_verdamping_dat.append(["   "+ str(float(flow_verdamping_bakje_I))+" "+str(float(flow_verdamping_bakje_II))+" "+str(float(flow_verdamping_bakje_III))+" "+\
		str(float(flow_verdamping_bakje_IV))+" "+str(float(flow_verdamping_bakje_V))+" "+str(float(flow_verdamping_bakje_VI))+" "+
		str(float(flow_verdamping_bakje_VII))+" "+str(float(flow_verdamping_bakje_VIII))+" "+str(float(flow_verdamping_bakje_IX))+" ; values"])

	#update volumes dat
	vol_dat.append(["                   " + time_stamp + "   ; time in ddhhmmss"])
	vol_dat.append(["   "+str(vol_bakje_I)+" "+str(vol_bakje_II)+" "+str(vol_bakje_III)+" "+\
		str(vol_bakje_IV)+" "+str(vol_bakje_V)+" "+str(vol_bakje_VI)+" "+str(vol_bakje_VII)+" "+\
		str(vol_bakje_VIII)+" "+str(vol_bakje_IX)+" "+str(vol_bakje_X)+"    ; values"])

	#update Bathse spuisluis
	Bathse_spuisluis.append([time_stamp+"  "+str(Zout_Bathse_spuisluis)])

	#update Bergse diepsluis
	Bergse_diepsluis.append([time_stamp+"  "+str(Zout_Bergse_diepsluis)])

	#update Krammersluizen
	Krammersluizen.append([time_stamp+"  "+str(Zout_Krammersluizen)])

	#update Kwel (   'Kwel Eendracht Noord', 'Kwel Eendracht Zuid', 'Kwel Zoommeer', 'Kwel Zoommeer Zuid')
	Kwel.append([time_stamp+"  "+str(Zout_Kwel_Krammer_Volkerak_West)+"  "+str(Zout_Kwel_Eendracht_Noord)+"  "+str(Zout_Kwel_Eendracht_Zuid)+"  "+\
		str(Zout_Kwel_Zoommeer)+" "+str(Zout_Kwel_Zoommeer_Zuid)])


#--------------Schrijf de bestanden weg--------------------------------------------------------------#

#schrijf flow bestand
flows_bakjes_dat_file =  open("input_delwaq/flows.dat","w")
flows_bakjes_dat_file.writelines("%s\n" % line[0] for line in flows_bakjes_dat)
flows_bakjes_dat_file.close()

#schrijf flow kunstwerken bestand
flows_kunstwerken_dat_file =  open("input_delwaq/flows_kunstwerken.dat","w")
flows_kunstwerken_dat_file.writelines("%s\n" % line[0] for line in flows_kunstwerken_dat)
flows_kunstwerken_dat_file.close()

#schrijf flow neerslag bestand
flows_neerslag_dat_file =  open("input_delwaq/flows_neerslag.dat","w")
flows_neerslag_dat_file.writelines("%s\n" % line[0] for line in flows_neerslag_dat)
flows_neerslag_dat_file.close()

#schrijf flow verdamping bestand
flows_verdamping_dat_file =  open("input_delwaq/flows_verdamping.dat","w")
flows_verdamping_dat_file.writelines("%s\n" % line[0] for line in flows_verdamping_dat)
flows_verdamping_dat_file.close()

#schrijf volumes bestand
vol_dat_file =  open("input_delwaq/volumes.dat","w")
vol_dat_file.writelines("%s\n" % line[0] for line in vol_dat)
vol_dat_file.close()

#schrijf Zoutvracht_Bathse_spuisluis_IDxxx.inc bestand
Bathse_spuisluis_file =  open("input_delwaq/Zoutvracht_Bathse_spuisluis_IDxxx.inc","w")
Bathse_spuisluis_file.writelines("%s\n" % line[0] for line in Bathse_spuisluis)
Bathse_spuisluis_file.close()

#schrijf Zoutvracht_Bergse_diepsluis_IDxxx.inc bestand
Bergse_diepsluis_file =  open("input_delwaq/Zoutvracht_Bergse_diepsluis_IDxxx.inc","w")
Bergse_diepsluis_file.writelines("%s\n" % line[0] for line in Bergse_diepsluis)
Bergse_diepsluis_file.close()

#schrijf Zoutvracht_Krammersluizen_IDxxx.inc bestand
Krammersluizen_file =  open("input_delwaq/Zoutvracht_Krammersluizen_IDxxx.inc","w")
Krammersluizen_file.writelines("%s\n" % line[0] for line in Krammersluizen)
Krammersluizen_file.close()

#schrijf Zoutvracht_Kwel_IDxxx.inc bestand
Kwel_file =  open("input_delwaq/Zoutvracht_Kwel_IDxxx.inc","w")
Kwel_file.writelines("%s\n" % line[0] for line in Kwel)
Kwel_file.close()

print("Done.")