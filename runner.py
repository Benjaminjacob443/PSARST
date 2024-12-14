import os
import subprocess
from pathlib import Path
import sys
import shutil
import datetime
import re
import logging
import urllib.request
from colorama import init, Fore, Style

# Initialize colorama
init()

# Color constants
RED = Fore.RED
GREEN = Fore.GREEN
RESET = Style.RESET_ALL

# Configuration Constants
VENV_NAME = "psarst_env"
REQUIREMENTS_FILE = 'psarst_requirements.txt'
PYTHON_VERSION = "3.11.1"
LOGS_DIR = "logs"
PYTHON_INSTALLER = "python-installer.exe"
LOCAL_PYTHON_DIR = "local_python"
TA_LIB_URL = "https://github.com/mrjbq7/ta-lib/archive/refs/heads/master.zip"
TA_LIB_DIR = "ta-lib-master"


requirements_path = Path(REQUIREMENTS_FILE)
SCRIPT_PATH = "PSARST.py"

# Logging Setup
def setup_logging():
    try:
        base_log_dir = os.path.join(LOGS_DIR, 'Error Logs')
        os.makedirs(base_log_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file_path = os.path.join(base_log_dir, f"PSARST_{timestamp}.log")

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file_path)]
        )
        logging.info("Logging setup completed.")
    except Exception as e:
        print(f"[{RED}FAILED{RESET}] Could not set up logging: {e}")
        sys.exit(1)

# Command Runner
def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"[{RED}FAILED{RESET}] Error executing command: {command}\n{e}")
        logging.error(f"Error executing command: {command}\n{e}")
        sys.exit(1)

# Virtual Environment Validation
def venv_exists(venv_path):
    python_path = venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return python_path.exists()

def check_python_version(venv_path):
    python_path = venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    result = subprocess.run([python_path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        python_version = result.stdout.decode().strip().split()[1]
        return python_version == PYTHON_VERSION
    return False

# def check_and_install_msvc():
#     try:
#         # Check if the Visual Studio version is installed by querying the registry (works for Windows)
#         result = subprocess.run(
#             ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\VisualStudio\\Setup\\VC'],
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE
#         )
#         if result.returncode == 0:
#             installed_versions = result.stdout.decode().splitlines()
#             for line in installed_versions:
#                 if "Version" in line:
#                     installed_version = float(line.split(":")[1].strip())
#                     if installed_version >= MSVC_VERSION_REQUIRED:
#                         print(f"[{GREEN} OK {RESET}] Microsoft Visual C++ version {installed_version} is installed.")
#                         logging.info(f"Microsoft Visual C++ version {installed_version} is installed.")
#                         return True

#         print(f"[{RED}INFO{RESET}] Visual C++ not found. Installing Visual Studio Build Tools...")
#         logging.info(f"Visual C++ not found. Installing Visual Studio Build Tools...")

#         # Download and install Visual Studio Build Tools if not found
#         visual_studio_installer_url = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
#         installer_path = Path("VS_Installer.exe")
#         with urllib.request.urlopen(visual_studio_installer_url) as response, open(installer_path, "wb") as out_file:
#             shutil.copyfileobj(response, out_file)
        
#         print(f"[{GREEN} -- {RESET}] Visual Studio Build Tools installer downloaded.")
#         logging.info(f"Visual Studio Build Tools installer downloaded to {installer_path}.")

#         # Run the Visual Studio Installer to install the required components
#         run_command(f"{installer_path} --quiet --wait --norestart --includeRecommended --add Microsoft.VisualC++BuildTools")
#         print(f"[{GREEN} OK {RESET}] Visual Studio Build Tools installed.")
#         logging.info("Visual Studio Build Tools installed.")

#         return True

#     except Exception as e:
#         print(f"[{RED}FAILED{RESET}] Failed to install Visual Studio Build Tools: {e}")
#         logging.error(f"Failed to install Visual Studio Build Tools: {e}")
#         return False

# def install_ta_lib():
#     try:
#         print(f"[{GREEN} -- {RESET}] Installing TA-Lib from source...")

#         # Download the TA-Lib source code
#         ta_lib_zip = "ta-lib.zip"
#         urllib.request.urlretrieve(TA_LIB_URL, ta_lib_zip)
#         print(f"[{GREEN} -- {RESET}] TA-Lib source code downloaded.")

#         # Unzip the downloaded TA-Lib source code
#         shutil.unpack_archive(ta_lib_zip, TA_LIB_DIR)
#         print(f"[{GREEN} -- {RESET}] TA-Lib source code extracted.")

#         # Build and install TA-Lib from source
#         ta_lib_path = Path(TA_LIB_DIR)
#         if os.name == "nt":
#             # For Windows, use the MSVC compiler if Visual Studio Build Tools are installed
#             if not check_and_install_msvc():
#                 print(f"[{RED}FAILED{RESET}] Could not install Visual Studio Build Tools. Exiting installation.")
#                 logging.error("Failed to install Visual Studio Build Tools.")
#                 sys.exit(1)

#             dev_cmd_prompt_path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat"
#             msbuild_command = f'"{dev_cmd_prompt_path}" && msbuild {ta_lib_path}\\ta-lib-python-master\\makefile.win /p:Configuration=Release'

#             # Run the MSBuild command through subprocess
#             run_command(msbuild_command)
#         else:
#             # For Unix-based systems, use the typical build process
#             run_command(f"cd {ta_lib_path} && ./configure && make && sudo make install")

#         print(f"[{GREEN} OK {RESET}] TA-Lib installed.")
#         logging.info("TA-Lib installed.")
        
#     except Exception as e:
#         print(f"[{RED}FAILED{RESET}] Error installing TA-Lib: {e}")
#         logging.error(f"Error installing TA-Lib: {e}")
#         sys.exit(1)

# Dependencies Check
def dependencies_installed(venv_path):
    pip_path = venv_path / "Scripts" / "pip" if os.name == "nt" else venv_path / "bin" / "pip"

    # Function to clean up version string to avoid issues with non-numeric characters
    def clean_version(version_str):
        return re.sub(r'[^0-9.]', '', version_str.strip())

    try:
        # Check if the requirements file exists
        if not requirements_path.exists():
            raise FileNotFoundError(f"Requirements file '{requirements_path}' not found.")
        
        # Open the requirements file
        with open(requirements_path, "r") as f:
            requirements = f.readlines()

        for req in requirements:
            req = req.strip()
            if req:  # Skip empty lines
                # Skip ta-lib dependency checking entirely
                if "ta-lib" in req.lower():
                    # print(f"[{GREEN} -- {RESET}] Installing TA-Lib requires Visual C++. Ensuring it's installed...")
                    # logging.info(f"Installing TA-Lib requires Visual C++. Ensuring it's installed...")
                    # install_ta_lib()
                    continue

                # Check if the package is already installed
                result = subprocess.run(
                    [pip_path, "show", req.split("==")[0]],  # Only check the package name
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if result.returncode != 0:  # If package not found
                    print(f"[{RED} MISSING {RESET}] {req} is not installed.")
                    logging.error(f"{req} is not installed.")
                    return False
                else:
                    # Get the installed version from the 'pip show' output
                    installed_version = subprocess.run(
                        [pip_path, "show", req.split("==")[0]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    installed_version = installed_version.stdout.decode().strip().split('\n')[1].split(': ')[1]
                    installed_version = clean_version(installed_version)  # Clean the version string
                    
                    # Compare with required version if specified
                    if "==" in req:
                        required_version = req.split("==")[1]
                        required_version = clean_version(required_version)  # Clean the required version string
                        
                        if installed_version != required_version:
                            print(f"[{RED} VERSION MISMATCH {RESET}] {req} installed version {installed_version} doesn't match required {required_version}.")
                            logging.error(f"{req} installed version {installed_version} doesn't match required {required_version}.")
                            return False
                        else:
                            print(f"[{GREEN} OK {RESET}] {req} is already installed and up-to-date.")
                            logging.info(f"{req} is already installed and up-to-date.")
                    else:
                        print(f"[{GREEN} OK {RESET}] {req} is already installed (latest version).")
                        logging.info(f"{req} is already installed (latest version).")
        return True

    except FileNotFoundError as e:
        print(f"[{RED} FAILED {RESET}] {e}")
        logging.error(e)
        sys.exit(1)

def install_requirements(venv_path):
    pip_path = venv_path / "Scripts" / "pip" if os.name == "nt" else venv_path / "bin" / "pip"
    print(f"[{GREEN} -- {RESET}] Installing dependencies from {REQUIREMENTS_FILE}...")
    logging.info(f"Installing dependencies from {REQUIREMENTS_FILE}...")
    run_command(f"{pip_path} install -r {REQUIREMENTS_FILE}")
    print(f"[{GREEN} OK {RESET}] All dependencies installed.")
    logging.info(f"All dependencies installed.")

# Virtual Environment Creation
def create_new_venv(venv_path):
    print(f"[{GREEN}--{RESET}] Creating a new virtual environment at {venv_path}...")
    logging.info(f"Creating a new virtual environment at {venv_path}...")
    run_command(f"python -m venv {venv_path}")
    print(f"[{GREEN}OK{RESET}] Virtual environment created.")
    logging.info("Virtual environment created.")

# Main Script Runner
def run_main_script(venv_path):
    python_path = venv_path / "Scripts" / "python" if os.name == "nt" else venv_path / "bin" / "python"
    print(f"[{GREEN} -- {RESET}] Running {SCRIPT_PATH}...")
    logging.info(f"Running {SCRIPT_PATH}...")
    run_command(f"{python_path} {SCRIPT_PATH}")

# Python Version Installer (placeholder for simplicity)
def check_or_install_python():
    local_python_path = Path(LOCAL_PYTHON_DIR) / f"python-{PYTHON_VERSION}"
    python_exe = local_python_path / "python.exe" if os.name == "nt" else local_python_path / "bin" / "python"

    # Check if Python version is already installed locally
    if python_exe.exists():
        result = subprocess.run([python_exe, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0 and PYTHON_VERSION in result.stdout.decode():
            print(f"[{GREEN} OK {RESET}] Python {PYTHON_VERSION} is already installed locally.")
            logging.info(f"Python {PYTHON_VERSION} is already installed locally.")
            return python_exe

    # If not, download and install Python locally
    print(f"[{GREEN} -- {RESET}] Python {PYTHON_VERSION} is not found. Downloading and installing locally...")
    python_installer_url = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe" if os.name == "nt" else f"https://www.python.org/ftp/python/{PYTHON_VERSION}/Python-{PYTHON_VERSION}.tgz"
    installer_path = Path(LOCAL_PYTHON_DIR) / PYTHON_INSTALLER
    os.makedirs(local_python_path, exist_ok=True)

    try:
        with urllib.request.urlopen(python_installer_url) as response, open(installer_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"[{GREEN} OK {RESET}] Python installer downloaded to {installer_path}.")
        logging.info(f"Python installer downloaded to {installer_path}.")
    except Exception as e:
        print(f"[{RED} FAILED {RESET}] Failed to download Python installer: {e}")
        logging.error(f"Failed to download Python installer: {e}")
        sys.exit(1)

    # Install Python locally
    if os.name == "nt":
        run_command(f"{installer_path} /quiet InstallAllUsers=0 TargetDir={local_python_path} SimpleInstall=1")
    else:
        run_command(f"tar -xvzf {installer_path} -C {local_python_path}")
        run_command(f"cd {local_python_path} && ./configure && make && make install")

    print(f"[{GREEN} OK {RESET}] Python {PYTHON_VERSION} installed locally.")
    logging.info(f"Python {PYTHON_VERSION} installed locally.")
    return python_exe

# Main Function
def main():
    setup_logging()
    venv_path = Path(VENV_NAME)

    # Ensure the requirements file exists
    if not requirements_path.exists():
        print(f"[{RED}FAILED{RESET}] Requirements file '{REQUIREMENTS_FILE}' not found.")
        logging.error(f"Requirements file '{REQUIREMENTS_FILE}' not found.")
        sys.exit(1)

    # Check Python version and create virtual environment
    python_exe = check_or_install_python()
    if not venv_exists(venv_path):
        print(f"[{RED}MISSING{RESET}] Virtual environment does not exist. Creating...")
        logging.info("Virtual environment does not exist. Creating a new one...")
        create_new_venv(venv_path)
        install_requirements(venv_path)
    else:
        print(f"[ {GREEN}OK{RESET} ] Virtual environment exists. Validating dependencies...")
        logging.info("Virtual environment exists. Validating dependencies...")
        if not dependencies_installed(venv_path):
            print(f"[{RED}MISSING{RESET}] Dependencies are missing or outdated. Installing...")
            logging.warning("Dependencies are missing or outdated. Installing...")
            install_requirements(venv_path)

    # Run the main script
    run_main_script(venv_path)

if __name__ == "__main__":
    main()
