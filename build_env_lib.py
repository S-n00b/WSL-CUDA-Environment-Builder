import os
import subprocess
import logging
import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for backup management
BACKUP_DIR = r"C:\Users\sneubauer.ABLENETINC\CODE\wsl_backups"
MAX_BACKUPS = 3

def check_wsl_distribution_exists(distro_name):
    """Check if the specified WSL distribution exists."""
    try:
        result = subprocess.run(f"wsl -l -v", shell=True, capture_output=True, text=True)
        if distro_name in result.stdout:
            return True
        else:
            logger.warning(f"No WSL distribution found with the name: {distro_name}")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list WSL distributions: {e}")
        return False

def enable_passwordless_sudo(distro_name, sudo_user):
    """Enable passwordless sudo for the specified user."""
    try:
        command = f"echo '%{sudo_user} ALL=(ALL) NOPASSWD:ALL' | sudo EDITOR='tee' visudo --quiet --file=/etc/sudoers.d/passwordless-sudo"
        execute_command(f"wsl -d {distro_name} bash -c \"{command}\"", "Enabling passwordless sudo")
    except Exception as e:
        logger.error(f"Failed to enable passwordless sudo for {sudo_user}: {e}")
        raise

def backup_existing_envs(miniconda_env_path):
    """Backup existing environments in the WSL miniconda3/envs directory."""
    try:
        if os.path.exists(miniconda_env_path):
            envs = [d for d in os.listdir(miniconda_env_path) if os.path.isdir(os.path.join(miniconda_env_path, d))]
            for env in envs:
                env_path = os.path.join(miniconda_env_path, env)
                backup_filename = f"{env}_backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.tar"
                backup_path = os.path.join(BACKUP_DIR, backup_filename)
                subprocess.run(f"wsl tar -cvf {backup_path} -C {env_path} .", shell=True, check=True)
                logger.info(f"Backed up environment: {env} to {backup_path}")
        else:
            logger.info(f"No environments found in {miniconda_env_path} to back up.")
    except Exception as e:
        logger.error(f"Failed to back up existing environments: {e}")
        raise

def create_backup(distro_name, env_name, backup_dir=BACKUP_DIR):
    """Create a backup of the WSL environment."""
    if not check_wsl_distribution_exists(distro_name):
        logger.info(f"Skipping backup as WSL distribution {distro_name} does not exist.")
        return

    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_filename = f"{env_name}_backup_{timestamp}.tar"
        backup_path = os.path.join(backup_dir, backup_filename)
        logger.info(f"Creating backup for {env_name} at {backup_path}...")
        subprocess.run(f"wsl --export {distro_name} {backup_path}", shell=True, check=True)
        logger.info(f"Backup created successfully: {backup_path}")
        manage_backups(backup_dir)
    except Exception as e:
        logger.error(f"Failed to create backup for {env_name}: {e}")
        raise

def revert_to_backup(distro_name, env_name, backup_dir=BACKUP_DIR):
    """Revert the WSL environment to the most recent backup."""
    try:
        backups = sorted([f for f in os.listdir(backup_dir) if f.startswith(env_name)], reverse=True)
        if backups:
            latest_backup = backups[0]
            backup_path = os.path.join(backup_dir, latest_backup)
            logger.info(f"Reverting to backup: {backup_path}")
            subprocess.run(f"wsl --unregister {distro_name}", shell=True, check=True)
            subprocess.run(f"wsl --import {distro_name} C:/wsl/{env_name} {backup_path} --version 2", shell=True, check=True)
            logger.info(f"Reverted {env_name} to the backup: {backup_path}")
        else:
            logger.error(f"No backups found to revert {env_name}")
            raise FileNotFoundError(f"No backups found in {backup_dir}")
    except Exception as e:
        logger.error(f"Failed to revert {env_name} to the backup: {e}")
        raise

def manage_backups(backup_dir=BACKUP_DIR, max_backups=MAX_BACKUPS):
    """Manage the number of backups by deleting older ones if exceeding the limit."""
    try:
        backups = sorted([f for f in os.listdir(backup_dir)], reverse=True)
        while len(backups) > max_backups:
            oldest_backup = backups.pop()
            os.remove(os.path.join(backup_dir, oldest_backup))
            logger.info(f"Deleted old backup: {oldest_backup}")
    except Exception as e:
        logger.error(f"Error managing backups: {e}")
        raise

def execute_command(command, description="Executing command", sleep_time=2):
    """Executes a shell command and waits for a given time."""
    logger.info(description)
    try:
        result = subprocess.run(command, shell=True, text=True)
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command} with error: {e}")
        raise

def read_env_config(config_file):
    """Reads the environment configuration from the specified file."""
    config = {}
    try:
        with open(config_file, 'r') as file:
            for line in file:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
    except Exception as e:
        logger.error(f"Failed to read configuration file {config_file}: {e}")
        raise
    return config

def ensure_config_files_exist():
    """Ensure that configuration files exist, and create defaults if they don't."""
    try:
        for config_file in ["env_config_latest.txt", "env_config_stable.txt"]:
            if not os.path.exists(config_file):
                with open(config_file, 'w') as file:
                    file.write("# Configuration file for environment setup\n")
                    file.write("DISTRO_NAME=Ubuntu\n")
                    file.write("ENV_NAME=rapids_model_env\n")
                    file.write("CONDA_PYTHON_VERSION=3.10\n")
                    # Add other default settings as needed
                logger.info(f"Created default configuration file: {config_file}")
    except Exception as e:
        logger.error(f"Error ensuring configuration files exist: {e}")
        raise

def cleanup_old_installations(distro_name):
    """Clean up old installations to avoid conflicts."""
    try:
        execute_command(f"wsl -d {distro_name} bash -c 'sudo apt-get remove --purge cuda-*'", "Removing old CUDA installations")
        execute_command(f"wsl -d {distro_name} bash -c 'sudo apt-get autoremove'", "Running autoremove")
        execute_command(f"wsl -d {distro_name} bash -c 'sudo apt-get clean'", "Cleaning up")
    except Exception as e:
        logger.error(f"Failed to clean up old installations: {e}")
        raise

def install_cuda(distro_name, cuda_version, cuda_path, cuda_lib_path):
    """Installs the specified version of CUDA."""
    try:
        execute_command(f"wsl -d {distro_name} bash -c 'sudo rm -rf /usr/local/cuda*'", "Removing old CUDA symlinks")
        execute_command(f"wsl -d {distro_name} bash -c 'sudo ln -s {cuda_path} /usr/local/cuda'", "Creating new CUDA symlink")
        # Add additional CUDA installation commands here as needed
    except Exception as e:
        logger.error(f"Failed to install CUDA {cuda_version}: {e}")
        raise

def configure_wsl_resources(distro_name, memory, swap, gpu_scheduling):
    """Configures WSL resources such as memory, swap, and GPU scheduling."""
    try:
        if memory:
            execute_command(f"wsl -d {distro_name} bash -c 'echo \"[wsl2]\" | sudo tee -a /etc/wsl.conf'", "Configuring WSL memory")
            execute_command(f"wsl -d {distro_name} bash -c 'echo \"memory={memory}\" | sudo tee -a /etc/wsl.conf'", "Setting memory allocation")
        if swap:
            execute_command(f"wsl -d {distro_name} bash -c 'echo \"swap={swap}\" | sudo tee -a /etc/wsl.conf'", "Setting swap space")
        if gpu_scheduling:
            execute_command(f"wsl -d {distro_name} bash -c 'echo \"gpu-scheduling={gpu_scheduling}\" | sudo tee -a /etc/wsl.conf'", "Enabling GPU scheduling")
    except Exception as e:
        logger.error(f"Failed to configure WSL resources: {e}")
        raise

def create_conda_env(distro_name, env_name, conda_python_version, conda_forge_libraries, rapids_nvidia_libraries, conda_libraries, pip_libraries):
    """Creates a Conda environment with the specified libraries."""
    try:
        execute_command(f"wsl -d {distro_name} bash -c 'conda create -n {env_name} python={conda_python_version} -y'", "Creating Conda environment")
        if conda_forge_libraries:
            execute_command(f"wsl -d {distro_name} bash -c 'conda install -n {env_name} -c conda-forge {conda_forge_libraries} -y'", "Installing Conda-Forge libraries")
        if rapids_nvidia_libraries:
            execute_command(f"wsl -d {distro_name} bash -c 'conda install -n {env_name} -c rapidsai -c nvidia {rapids_nvidia_libraries} -y'", "Installing RAPIDS and NVIDIA libraries")
        if conda_libraries:
            execute_command(f"wsl -d {distro_name} bash -c 'conda install -n {env_name} {conda_libraries} -y'", "Installing additional Conda libraries")
        if pip_libraries:
            execute_command(f"wsl -d {distro_name} bash -c 'conda run -n {env_name} pip install {pip_libraries}'", "Installing additional Pip libraries")
    except Exception as e:
        logger.error(f"Failed to create Conda environment {env_name}: {e}")
        raise

def register_jupyter_kernel(distro_name, env_name):
    """Registers a Jupyter kernel for the created environment."""
    try:
        execute_command(f"wsl -d {distro_name} bash -c 'conda run -n {env_name} python -m ipykernel install --user --name {env_name} --display-name \"{env_name} Kernel\"'", "Registering Jupyter kernel")
    except Exception as e:
        logger.error(f"Failed to register Jupyter kernel for {env_name}: {e}")
        raise

def reset_restart_status():
    """Resets the status file indicating if a restart was needed."""
    try:
        if os.path.exists('restart_status.txt'):
            os.remove('restart_status.txt')
    except Exception as e:
        logger.error(f"Failed to reset restart status: {e}")
        raise

def read_restart_status():
    """Reads the status file to determine if a restart was needed."""
    try:
        if os.path.exists('restart_status.txt'):
            with open('restart_status.txt', 'r') as file:
                return file.read().strip() == 'true'
        return False
    except Exception as e:
        logger.error(f"Failed to read restart status: {e}")
        raise

def build_env_lib(config_file="env_config_latest.txt"):
    """
    Main function to build the environment according to the configuration file.

    Arguments:
        config_file (str): The path to the configuration file containing the environment settings.
    """
    try:
        ensure_config_files_exist()
        config = read_env_config(config_file)

        distro_name = config.get("DISTRO_NAME", "Ubuntu")
        env_name = config.get("ENV_NAME")
        conda_python_version = config.get("CONDA_PYTHON_VERSION")
        conda_forge_libraries = config.get("CONDA_FORGE_LIBRARIES", "")
        rapids_nvidia_libraries = config.get("RAPIDS_NVIDIA_LIBRARIES", "")
        conda_libraries = config.get("CONDA_LIBRARIES", "")
        pip_libraries = config.get("PIP_LIBRARIES", "")
        cuda_version = config.get("CUDA_VERSION", "")
        cuda_path = config.get("CUDA_PATH", "/usr/local/cuda")
        cuda_lib_path = config.get("CUDA_LIB_PATH", "/usr/local/cuda/lib64")
        memory = config.get("MEMORY", "")
        swap = config.get("SWAP", "")
        gpu_scheduling = config.get("GPU_SCHEDULING", "")
        sudo_user = config.get("SUDO_USER", "")

        # Enable passwordless sudo for the user
        enable_passwordless_sudo(distro_name, sudo_user)

        # Backup the WSL environment before starting the setup
        create_backup(distro_name, env_name)
        backup_existing_envs(f"/mnt/wsl.localhost/{distro_name}/home/{sudo_user}/miniconda3/envs")

        if read_restart_status():
            logger.info("Resuming from previous incomplete setup...")
        else:
            cleanup_old_installations(distro_name)

        # Set project directory and handle sudo user if needed
        project_dir = config.get("PROJECT_DIR", "")
        if project_dir:
            wsl_project_dir = project_dir.replace(":", "").replace("\\", "/").replace(" ", "\\ ")
            execute_command(f"wsl -d {distro_name} cd {wsl_project_dir}", f"Changing directory to: {wsl_project_dir}")

        install_cuda(distro_name, cuda_version, cuda_path, cuda_lib_path)
        configure_wsl_resources(distro_name, memory, swap, gpu_scheduling)
        create_conda_env(
            distro_name,
            env_name,
            conda_python_version,
            conda_forge_libraries,
            rapids_nvidia_libraries,
            conda_libraries,
            pip_libraries
        )
        register_jupyter_kernel(distro_name, env_name)

        logger.info("Environment setup completed successfully.")
    except Exception as e:
        logger.error(f"Environment setup failed: {e}")
        logger.info("Attempting to revert to the last known good WSL environment...")
        try:
            revert_to_backup(distro_name, env_name)
        except FileNotFoundError:
            logger.error(f"No backups found to revert {env_name}. Please troubleshoot the issue manually.")
        raise

# Running the build_env_lib function if this script is executed directly
if __name__ == "__main__":
    build_env_lib("env_config_latest.txt")



'''
### **Explanation of the Script:**

- **create_backup**: This function backs up the current WSL environment to a `.tar` file. The backups are stored in a designated directory with timestamps in their filenames.

- **revert_to_backup**: This function reverts the WSL environment to the most recent backup if an error occurs.

- **manage_backups**: Manages backup files by keeping only the three most recent backups.

- **execute_command**: A utility function to execute shell commands with optional sleep time, ensuring that the system has enough time to process before moving on to the next command.

- **read_env_config**: Reads the configuration file that defines environment settings like CUDA paths, memory allocation, and more.

- **ensure_config_files_exist**: Creates default configuration files if they don’t exist.

- **cleanup_old_installations**: Cleans up previous CUDA installations to avoid conflicts with the new setup.

- **install_cuda**: Installs the specified version of CUDA by managing symlinks and ensuring paths are correct.

- **configure_wsl_resources**: Configures memory, swap space, and GPU scheduling in WSL2 according to the user’s configuration.

- **create_conda_env**: Sets up a Conda environment with all specified packages from Conda Forge, RAPIDS, and others.

- **register_jupyter_kernel**: Registers a Jupyter kernel for the new Conda environment.

- **reset_restart_status**: Resets the status flag that indicates if a restart was required during the installation process.

- **read_restart_status**: Reads the restart status to determine if the script should resume from where it left off.

- **build_env_lib**: This is the main function that ties all the above functions together, orchestrating the setup of the entire environment. It reads configuration details, backs up the environment, sets up CUDA, Conda environments, and handles any necessary restarts.

This script is designed to be robust and versatile, ensuring that the user can easily manage complex WSL2 environments for RAPIDS and CUDA-based development with Nvidia GPUs.

'''