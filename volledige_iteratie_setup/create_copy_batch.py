'''
Create a batch script to run the model
'''

import sys
import math
import pandas
import numpy

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def isNaN(num):
    return num != num

scenario_nr = int(sys.argv[1])

#Read from excel
df_variables = pandas.read_csv("scenario_overview.csv", sep = ";")

#Get column values 
exclude_list = ["Scen_NR"]
variable_names = [x for x in list(df_variables.columns.values) if x not in exclude_list]

scenario_subset = df_variables.loc[(df_variables.Scen_NR == scenario_nr)].copy()


#ISSUE gemixte colomen. Will spaties en empty vervangen voor NAN maar overige data types in orginele staat behouden.
#vervolgens moet de nan herkent worden, strings herkent worden en floats.

#Replace blanks with NaN
scenario_subset = scenario_subset.astype(str).replace(r'\s+', numpy.NaN, regex=True)
scenario_subset = scenario_subset.astype(str).replace('', numpy.NaN, regex=True)

#Open a batch file
batch_file = open("_run\\copy_batch.bat","w")

batch_script = '@echo "preform copy of variables to run"\n'
batch_file.write(batch_script)

for variable in variable_names:

	dict_bat = {}
	dict_bat["variable"] = variable

	#get variable value
	variable_value = scenario_subset[variable]

	#If it is a nan, fill it with central, else the scenario estimate
	if(isinstance(variable_value.values.tolist()[0], str)):
		if(variable_value.values.tolist()[0] == "nan"):
			dict_bat["estimate"] = "Central"
		else:	
			dict_bat["estimate"] = variable_value.tolist()[0]
	elif(isNaN(variable_value.values)):
		dict_bat["estimate"] = "Central"
	elif(isinstance(variable_value.values.tolist()[0], float) or isinstance(variable_value.values.tolist()[0], int)):
		dict_bat["estimate"] = scenario_subset["Estimate"].values.tolist()[0]
	else:
		raise ValueError("incorrect data parsed for scenario csv : " +str(variable_value))

	#create the copy line
	batch_repeat = "copy ..\\input\\{variable}\\{estimate}.csv      input\\{variable}.csv\n"
	batch_line = batch_repeat.format(**dict_bat)
	batch_file.write(batch_line)

batch_file.close()
