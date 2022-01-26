'''
Make runall.bat
'''

import pandas

#Read from excel
df_variables = pandas.read_csv("scenario_overview.csv", sep = ";")

all_scenarios = df_variables.Scen_NR.values.tolist()

batch_file = open("1_runall.bat","w")
batch_script = '@echo "run all scenarios"\n'
batch_file.write(batch_script)
for scenario_nr in all_scenarios:
	dict_bat = {}
	dict_bat["scenarionr"] = str(scenario_nr)
	batch_repeat = "call run_VZM.bat {scenarionr}\n"
	batch_line = batch_repeat.format(**dict_bat)
	batch_file.write(batch_line)

batch_file.close()
print("Done.")