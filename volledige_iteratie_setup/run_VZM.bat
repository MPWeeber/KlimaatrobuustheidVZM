@echo "Prepare setup"

@echo "scenario"
@echo %1

@echo "clean up"
cd _run
del *.* /F /Q

cd ..\

@echo "create directories"
if not exist _run\\input mkdir _run\\input
if not exist _run\\input_delwaq mkdir _run\\input_delwaq
if not exist _run\\output mkdir _run\\output
if not exist _run\\Zout_Delwaq mkdir _run\\Zout_Delwaq

@echo "copy setup VZM model"
copy _storage\Zout_Delwaq\delwaq.inp                _run\Zout_Delwaq\delwaq.inp
copy _storage\Zout_Delwaq\dispersie_50constant.inc  _run\Zout_Delwaq\dispersie_50constant.inc
copy _storage\Zout_Delwaq\rundelwaq.bat             _run\Zout_Delwaq\rundelwaq.bat
copy _storage\bakjesmodel_VZM_V2.py                 _run\bakjesmodel_VZM_V2.py
copy _storage\bereid_zout_voor_delwaq.py            _run\bereid_zout_voor_delwaq.py

@echo "create copy batch"
call python create_copy_batch.py %1


cd _run

@echo "copy variables"
call copy_batch.bat

@echo "Preform VZM bakjes calculation"
call python bakjesmodel_VZM_V2.py

@echo "Preform preperation Delwaq"
call python bereid_zout_voor_delwaq.py

@echo "Run Delwaq"
cd Zout_Delwaq
call rundelwaq.bat
cd ..\


cd ..\


@echo "Save scenario"
if not exist output\\%1_scenario mkdir output\\%1_scenario

@echo "  clean up scenario"
del output\%1_scenario\*.* /F /Q

@echo "  copy VZM scenario results"
copy _run\bakjesmodel_VZM_V2.py             output\%1_scenario\bakjesmodel_VZM_V2.py
copy _run\bereid_zout_voor_delwaq.py        output\%1_scenario\bereid_zout_voor_delwaq.py
copy _run\copy_batch.bat                    output\%1_scenario\copy_batch.bat

@echo "  copy input variables scenario bakjes"
if not exist output\%1_scenario\input mkdir output\%1_scenario\input
copy _run\input\1_volkeraksluizen.csv	              output\%1_scenario\input\1_volkeraksluizen.csv
copy _run\input\2_neerslag.csv	                      output\%1_scenario\input\2_neerslag.csv
copy _run\input\3_krammersluizen.csv	              output\%1_scenario\input\3_krammersluizen.csv
copy _run\input\4_bergsediepsluis.csv	              output\%1_scenario\input\4_bergsediepsluis.csv
copy _run\input\5_kreekraksluis.csv	                  output\%1_scenario\input\5_kreekraksluis.csv
copy _run\input\6_verdamping.csv	                  output\%1_scenario\input\6_verdamping.csv
copy _run\input\7_kwel.csv	                          output\%1_scenario\input\7_kwel.csv
copy _run\input\8a_watervraag_hollandse_delta.csv     output\%1_scenario\input\8a_watervraag_hollandse_delta.csv
copy _run\input\8b_watervraag_schelde_stromen.csv     output\%1_scenario\input\8b_watervraag_schelde_stromen.csv
copy _run\input\8c_watervraag_brabantse_delta.csv     output\%1_scenario\input\8c_watervraag_brabantse_delta.csv
copy _run\input\9a_Dintel.csv                         output\%1_scenario\input\9a_Dintel.csv
copy _run\input\9b_Steenbergse_Vliet.csv              output\%1_scenario\input\9b_Steenbergse_Vliet.csv
copy _run\input\10_bathse_spuisluis.csv               output\%1_scenario\input\10_bathse_spuisluis.csv
copy _run\input\A_zeespiegelstijging.csv              output\%1_scenario\input\A_zeespiegelstijging.csv
copy _run\input\B_inlaatstop_volkeraksluizen.csv      output\%1_scenario\input\B_inlaatstop_volkeraksluizen.csv
copy _run\input\C1_waterstand_VZM_lowerlimit.csv      output\%1_scenario\input\C1_waterstand_VZM_lowerlimit.csv
copy _run\input\C2_waterstand_VZM_upperlimit.csv      output\%1_scenario\input\C2_waterstand_VZM_upperlimit.csv

@echo "  copy variables scenario bakjes results"
if not exist output\%1_scenario\output mkdir output\%1_scenario\output
copy _run\output\Controle_overzicht_bakjesmodel_VZM.csv	                             output\%1_scenario\output\Controle_overzicht_bakjesmodel_VZM.csv
copy _run\output\Invoer_bakjesmodel_VZM.csv	                                         output\%1_scenario\output\Invoer_bakjesmodel_VZM.csv
copy _run\output\Invoer_zout_bakjesmodel_VZM.csv	                                 output\%1_scenario\output\Invoer_zout_bakjesmodel_VZM.csv
copy _run\output\Waterbalans_Debiet_mogelijk_bij_Krammersluizen_bakjesmodel_VZM.csv	 output\%1_scenario\output\Waterbalans_Debiet_mogelijk_bij_Krammersluizen_bakjesmodel_VZM.csv
copy _run\output\Waterbalans_Debiet_Neerslag_bakjesmodel_VZM.csv	                 output\%1_scenario\output\Waterbalans_Debiet_Neerslag_bakjesmodel_VZM.csv
copy _run\output\Waterbalans_Debiet_Verdamping_bakjesmodel_VZM.csv	                 output\%1_scenario\output\Waterbalans_Debiet_Verdamping_bakjesmodel_VZM.csv
copy _run\output\Waterbalans_Debiet_uitwisseling_bakjesmodel_VZM.csv	             output\%1_scenario\output\Waterbalans_Debiet_uitwisseling_bakjesmodel_VZM.csv
copy _run\output\Waterbalans_Volumes_bakjes_bakjesmodel_VZM.csv	                     output\%1_scenario\output\Waterbalans_Volumes_bakjes_bakjesmodel_VZM.csv
copy _run\output\log_bakjesmodel_VZM.txt	                                         output\%1_scenario\output\log_bakjesmodel_VZM.txt

@echo "  copy input variables scenario DELWAQ"
if not exist output\%1_scenario\input_delwaq mkdir output\%1_scenario\input_delwaq
copy _run\input_delwaq\flows.dat	                            output\%1_scenario\input_delwaq\flows.dat
copy _run\input_delwaq\flows_kunstwerken.dat	                output\%1_scenario\input_delwaq\flows_kunstwerken.dat
copy _run\input_delwaq\flows_neerslag.dat	                    output\%1_scenario\input_delwaq\flows_neerslag.dat
copy _run\input_delwaq\flows_verdamping.dat	                    output\%1_scenario\input_delwaq\flows_verdamping.dat
copy _run\input_delwaq\volumes.dat	                            output\%1_scenario\input_delwaq\volumes.dat
copy _run\input_delwaq\Zoutvracht_Bathse_spuisluis_IDxxx.inc	output\%1_scenario\input_delwaq\Zoutvracht_Bathse_spuisluis_IDxxx.inc
copy _run\input_delwaq\Zoutvracht_Bergse_diepsluis_IDxxx.inc	output\%1_scenario\input_delwaq\Zoutvracht_Bergse_diepsluis_IDxxx.inc
copy _run\input_delwaq\Zoutvracht_Krammersluizen_IDxxx.inc	    output\%1_scenario\input_delwaq\Zoutvracht_Krammersluizen_IDxxx.inc
copy _run\input_delwaq\Zoutvracht_Kwel_IDxxx.inc	            output\%1_scenario\input_delwaq\Zoutvracht_Kwel_IDxxx.inc

@echo "  copy variables scenario DELWAQ results"
if not exist output\%1_scenario\Zout_Delwaq mkdir output\%1_scenario\Zout_Delwaq
copy _run\Zout_Delwaq\delwaq.inp	             output\%1_scenario\Zout_Delwaq\delwaq.inp
copy _run\Zout_Delwaq\dispersie_50constant.inc	 output\%1_scenario\Zout_Delwaq\dispersie_50constant.inc
copy _run\Zout_Delwaq\rundelwaq.bat         	 output\%1_scenario\Zout_Delwaq\rundelwaq.bat
copy _run\Zout_Delwaq\delwaq-initials.map	     output\%1_scenario\Zout_Delwaq\delwaq-initials.map
copy _run\Zout_Delwaq\delwaq.lsp             	 output\%1_scenario\Zout_Delwaq\delwaq.lsp
copy _run\Zout_Delwaq\delwaq.lst	             output\%1_scenario\Zout_Delwaq\delwaq.lst
copy _run\Zout_Delwaq\memory_map.out	         output\%1_scenario\Zout_Delwaq\memory_map.out
copy _run\Zout_Delwaq\delwaq-bal.his        	 output\%1_scenario\Zout_Delwaq\delwaq-bal.his
copy _run\Zout_Delwaq\delwaq.his	             output\%1_scenario\Zout_Delwaq\delwaq.his
copy _run\Zout_Delwaq\delwaq-bal.prn         	 output\%1_scenario\Zout_Delwaq\delwaq-bal.prn
copy _run\Zout_Delwaq\delwaq_res.map	         output\%1_scenario\Zout_Delwaq\delwaq_res.map
copy _run\Zout_Delwaq\delwaq-timers.out	         output\%1_scenario\Zout_Delwaq\delwaq-timers.out
copy _run\Zout_Delwaq\delwaq.mon	             output\%1_scenario\Zout_Delwaq\delwaq.mon
copy _run\Zout_Delwaq\delwaq.rtn	             output\%1_scenario\Zout_Delwaq\delwaq.rtn
copy _run\Zout_Delwaq\delwaq_user_wasteloads.mon	 output\%1_scenario\Zout_Delwaq\delwaq_user_wasteloads.mon


@echo "Done.