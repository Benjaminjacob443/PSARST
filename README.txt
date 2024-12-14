Welcome to README file for PSARST!

***DISCLAIMER: This tool is only for practicing purposes and it is in no way recommended to deploy it as a trading strategy with real money.***

# DO NOT make changes to 'runner.py' unless you know exactly what you are doing. Otherwise, the executable may not work as expected.

# You can safely run the executable even after making changes to 'PSARST.py'

# If you are a beginner in python simply run 'run_psarst.exe' and the executable will take care of everything, including installing the required Python version and all the dependencies.

# If you want to set-up manually, here is what you do: (For Windows Only)

- Install Python 3.11.1
- Open a terminal in the same directory as 'PSARST.py'
- Run 'python -m venv psarst_env' to create a virtual environment *Changing the name of the virtual environment may result in issues when running 'psarst_run.exe')
- Run '.\psarst_env\Scripts\activate' to activate the virtual environment

# With the virtual environment now active:
- Run 'pip install -r psarst_requirements.txt' on the terminal to install all the dependencies for the program
- Run the program using 'psarst_run.exe' or directly from 'PSARST.py' with your virtual environment still active

# Disable Antivirus for the executable to run without interruptions.

# The executable and ta-lib wheel file only supports 64-bit architecture. You can download the ta-lib wheel file according to your system specs manually in case of any errors and run 'PSARST.py' from an IDE after installing the necessary packages