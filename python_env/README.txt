#Installing the Anaconda PythonVZMBakjesmodel environment
Author : M.P. Weeber (Deltares)
Date : 23 - 11 -2021

#Benefits of Python environments#
Code produced for Python is transferable and will be executed in the same way as on the original machine.
All required libraries, versions of libraries and python version will be installed, so 
there is no cause of mismatch based on newer developments. Also this saves the hassle of installing all 
the required libraries yourself manually. In this way multiple versions of Python can exist on the same machine without
 interference.


#Installing MiniConda#
Download MiniConda here:
https://docs.conda.io/en/latest/miniconda.html
Install accordingly and make sure to add the folder of installation to your environmental paths:
for example : "c:\ProgramData\Miniconda3\condabin\"

#Installing the environment#
The python library is developed using a specific set of libraries and python installation. To ensure good 
results you should try to recreate this environment. In the folder “envs” you will find the file “PyKRWV.yml”. 
With this file you can install the required Python environment through Anaconda.

Environment installation and use for Windows: 
- Start the command prompt (CMD). Make sure your CMD is in the folder "python_env". 
- Type "conda" and enter. Now you should see the help menu.
- Type "conda env create -f PythonVZMBakjesmodel.yml". Now the environment is installed on your computer.
- To start an environment, type "activate PythonVZMBakjesmodel.yml" and enter.
- To use the Spyder IDE in the environment, first you have to install spyder through "conda install -c anaconda spyder" in the CMD environment
	You can than start spyder by typing "spyder" and enter in the CMD environment .

#Run a script#
For running the existing scripts you can use the following actions after installing Anaconda and the environment. 

Running scripts for Windows: 
- Start the command prompt(CMD) and navigate to the folder containing the scripts.
- Type "activate PythonVZMBakjesmodel" and enter (to start the environment).
- Type "python [name of the script]" (to execute the script in the command promt using Python).
- The script will now generate the output in the folder output.