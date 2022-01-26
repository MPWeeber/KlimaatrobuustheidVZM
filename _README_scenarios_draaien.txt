#Scenario's draaien voor het VZM Bakjesmodel

Gemaakt door Marc Weeber
Datum : 26 januari 2022


Deze input setup en scripts zijn ontworpen om de combinatie aan scenario's door 
te kunnen rekenen die van toepassing zijn op het Volkerak-Zoommeer (VZM).

De werkwijze is als volgt:
In de input Folder zijn de varianten aan input variabelen weergegeven.
Elke folder staat hier voor een afzonderelijke input variabele die gevarieerd zal worden.
Per folder kunnen er meerdere varianten worden aangeleverd in CSV formaat.
De bijgevoegde python scripts werken alleen wanneer de "PythonVZMBakjesmodel" geactiveerd is (zie folder python_env).

Met het script "A_create_iteration_overview.py"(Python3) wordt het overzicht "scenario_overview.csv" gegenereerd
 waarin de verschillende combinaties worden getoond. Combinaties die niet gewenst zijn kunnen met behulp van het script
 worden uitgesloten. In het "log_create_iteration_overview.txt" wordt een overzicht gegeven van de verschillende variabelen en
 input CSV's en wordt het aantal scenario's weergegeven. Gelijktijdig worden in de folder "input_overview" de combinaties 
per variabele in grafieken getoond. Deze worden bij het herdraaien van het script geupdate.

Met het script "B_create_scenario_batch.py"(Python3) wordt een batch file gegenereerd die alle scenario's zal gaan berekenen.
De batch file heet "1_runall.bat".
In deze batch file wordt per scenario een andere batch file aangeroepen, namelijk "run_VZM.bat", waarin het model
 en de benodigde bestanden worden klaargezet voor een run en waarbij de resultaten naar de output folder worden
 gekopieerd. Deze batch file moet ingericht worden naar de betreffende input, model en resultaten.

In de batch file "run_VZM.bat" wordt het python script "create_copy_batch.py" aangeroepen die een batch file zal maken voor het klaarzetten
 van de juiste input files voor het specifieke scenario. In "scenario_overview.csv" is terug te zien welke input dit betreft.

Met script "D_postprocessing.py"(Python3) wordt de scenario data in output verwerkt naar de afbeeldingen die getoond worden
 in de folder "overzicht_resultaat". In dit script is specifieke configuratie voor het VZM opgenomen.


LET OP 1: De python module voor de Zeesluisformulering, waarmee de input voor de Krammersluizen is gecreeërd is niet meegeleverd!
Dit is vervangen in de folder "_storage" met de file "ZSF_Krammersluizen_v2000501.placehold"
LET OP 2: De DELWAQ executabels voor het berekenen van zoutgehaltes in het VZM (delwaq1.exe, delwaq2.exe) zijn niet meegeleverd.
In onze berekeningen is gebruik gemaakt van "delwaq_5.08.00.64083". in de het bestand "_storage/Zout_Delwaq/rundelwaq.bat" staat
 de verwijzing naar beide delwaq executabels.   
LET OP 3: Vanwege dat er 1408 scenario's zijn gedraaid en dit relatief groot wordt is in de folder "output" alleen de
 uitvoer van scenario1 weergegeven.


