# WSL-CUDA-Environment-Builder
Automatically builds WSL-CUDA-RAPIDS env for machine learning development with GPUs on Windows systems

### **Complete User Documentation for `build_env_lib` Module**

This comprehensive guide provides detailed instructions and reference material for using the `build_env_lib` module to set up a RAPIDS and CUDA environment in WSL2 on Windows. It includes user-friendly steps, troubleshooting tips, and an expanded FAQ section for common issues related to Nvidia GPUs and WSL2. The guide also integrates support for managing existing project directories and user settings.

---

### **Table of Contents**

1. **Overview**
2. **Prerequisites**
3. **Configuration Files**
    - Latest Configuration
    - Stable Configuration
4. **Setting Up the Environment**
5. **Using Your Existing WSL Password**
6. **Integration with Nvidia RTX Experience Application**
7. **Automatic Backup and Reversion Features**
8. **Managing Existing Projects and User Settings**
9. **Troubleshooting and Tips**
10. **Frequently Asked Questions (FAQs)**
11. **Appendices**
    - A. References and Source Links
    - B. Known Issues and Workarounds

---

### **1. Overview**

The `build_env_lib` module automates the setup of a RAPIDS environment in WSL2, ensuring compatibility with your Nvidia GPU. It supports two configurations: one with the latest Nvidia drivers and CUDA versions, and a stable configuration with older versions known to work well with WSL2. This module is particularly useful for users who need a robust environment for GPU-accelerated tasks, such as data science and machine learning, within the WSL2 framework on Windows.

### **2. Prerequisites**

Before you begin, ensure you have the following:
- **Windows 10 or 11** with WSL2 enabled. You can install WSL2 by following [Microsoft’s official guide](https://docs.microsoft.com/en-us/windows/wsl/install).
- An **Nvidia GPU** that supports CUDA, such as the Nvidia A1000.
- **Python 3.9 or later** installed on your system.
- **Administrator privileges** on your Windows machine to allow the script to configure system settings and install necessary software.

### **3. Configuration Files**

The module uses two primary configuration files to manage the environment setup:

1. **Latest Configuration (`env_config_latest.txt`)**
    - This file sets up an environment using the latest Nvidia driver and CUDA version, offering access to the latest features. However, using this setup may cause `nvidia-smi` to produce segmentation faults in WSL2. 

2. **Stable Configuration (`env_config_stable.txt`)**
    - This file sets up an environment using an older Nvidia driver (537.58) and CUDA version (12.2). This setup is more stable and less prone to issues but may lack the latest features.

Both configuration files are created automatically by the script if they do not exist, ensuring that the user has a starting point for customization.

### **4. Setting Up the Environment**

To set up your environment, follow these steps:

1. **Run the Script:**
   - Open your command line interface (PowerShell recommended) and navigate to the directory containing the `build_env_lib` module.
   - Run the script using the appropriate configuration file:
     - For the latest setup: `python build_env_lib.py --config env_config_latest.txt`
     - For the stable setup: `python build_env_lib.py --config env_config_stable.txt`

2. **Monitor the Installation:**
   - The script will automatically install all necessary dependencies, configure WSL2 resources, and set up your CUDA environment.

3. **Handling Restarts:**
   - If a restart is required during the setup, the script will log this and pause execution. After restarting your machine, re-run the script, and it will resume where it left off.

### **5. Using Your Existing WSL Password**

The script requires sudo access to execute certain commands within WSL. If you already have a WSL instance with a password, you can use it by following these steps:

1. **Edit the Configuration File:**
   - Open the configuration file you plan to use (`env_config_latest.txt` or `env_config_stable.txt`).
   - Find the `PASSWORD` field and replace `your_password` with your WSL password.

2. **Secure Password Handling:**
   - For better security, consider prompting the user for the password at runtime or using environment variables to store it securely.

3. **Running the Script:**
   - When running the script, it will automatically use your provided password to execute any necessary `sudo` commands.

### **6. Integration with Nvidia RTX Experience Application**

If you are using the Nvidia RTX Experience application to manage your drivers, here’s how to integrate it with the `build_env_lib` module:

1. **Driver Management:**
   - The script automatically handles the installation of Nvidia drivers compatible with WSL2. **It is recommended not to update drivers manually via the RTX Experience application** while using this script to avoid conflicts.

2. **Switching Between Configurations:**
   - To use the Nvidia RTX Experience application for a specific driver, you may switch to the stable configuration provided by the module. This uses the 537.58 driver, which is compatible with WSL2 and less prone to issues.

3. **Manual Driver Installation:**
   - If you prefer to manage drivers manually via Nvidia RTX Experience, you can disable driver installation in the script by commenting out the relevant lines in the configuration file.

### **7. Automatic Backup and Reversion Features**

The `build_env_lib` module now includes an automatic backup and reversion mechanism to safeguard your WSL environments:

1. **Automatic Backup:**
   - Before making any changes to the WSL environment, the script will create a backup. This backup is stored in a designated directory (`wsl_backups`), with the backup files named according to the environment name and timestamp.

2. **Error Handling and Automatic Reversion:**
   - If an error occurs during the WSL-related steps, the script will automatically attempt to revert to the most recent backup. This ensures that your environment remains stable and operational.

3. **Backup Management:**
   - The script automatically manages backups by keeping only the three most recent backups, deleting older ones to conserve disk space.

4. **Logging and Notifications:**
   - The script logs all backup and reversion actions, informing you of any issues and the actions taken to resolve them.

### **8. Managing Existing Projects and User Settings**

To integrate your existing projects and user-specific settings into the environment setup, the configuration files now include the following fields:

- **PROJECT_DIR:** Specifies the directory path for your existing projects. This path is used to set the working directory during the environment setup. Example: `\\wsl.localhost\Ubuntu\home\sneubauer\code\`.
- **SUDO_USER:** Specifies the sudo username under the Home folder. The script uses this username to manage permissions and execute sudo commands within the WSL environment. Example: `sneubauer`.
- **PASSWORD:** The sudo password for the specified user. This password is used automatically for any sudo operations required during the environment setup.

These additions make it easier to integrate the `build_env_lib` module with your existing WSL projects and configurations, ensuring a seamless setup experience.

### **9. Troubleshooting and Tips**

- **nvidia-smi Segmentation Fault:**
  - If you encounter a segmentation fault with `nvidia-smi`, ensure you are using the latest drivers supported by WSL2 or switch to the stable configuration. Refer to the [NVIDIA WSL documentation](https://docs.nvidia.com/cuda/wsl-user-guide/index.html) for more details.

- **Driver Conflicts:**
  - Avoid installing or updating drivers through Nvidia RTX Experience while the script is running to prevent conflicts.

- **Script Execution Issues:**
  - If the script fails to execute commands or times out, try increasing the `sleep_time` parameter in the `execute_command` function to allow more time for each step.

### **10. Frequently Asked Questions (FAQs)**

**Q1. Can I use this script if my WSL2 instance is already set up with a different configuration?**
- Yes, the script is designed to integrate with your current WSL2 setup. It will attempt to merge configurations where possible, but it is recommended to back up existing configuration files and data before running the script. For more on WSL2 configuration management, visit [Microsoft’s WSL documentation](https://docs.microsoft.com/en-us/windows/wsl/).

**Q2. What should I do if `nvidia-smi` fails with a segmentation fault in WSL2?**
- This is a known issue when using certain versions of the NVIDIA driver with WSL2. The segmentation fault typically occurs with `nvidia-smi`, but CUDA operations continue to function correctly. Consider using the stable configuration (`env_config_stable.txt`) or refer to the [relevant GitHub issue](https://github.com/microsoft/WSL/issues/11277) for more information.

**Q3. How do I troubleshoot installation issues with the RAPIDS libraries in WSL2?**
- Ensure you are using compatible versions of CUDA and RAPIDS as outlined in the [RAPIDS installation documentation](https://docs.rapids.ai/install). If issues persist, clean up previous installations by running the `cleanup_old_installations()` function in the script, then attempt the installation again.

**Q4. Can I manually update the NVIDIA driver after setting up the environment?**

- While the script handles driver installation automatically, you can manually update the driver using the Nvidia RTX Experience application or by downloading the latest driver from the [NVIDIA website](https://www.nvidia.com/Download/index.aspx). However, manual updates may cause conflicts with WSL2. If you choose to manually update the driver, make sure it’s compatible with the versions of CUDA and RAPIDS used in your setup. The script includes automatic backup and reversion features that can help you recover the environment if issues arise after a manual update.

**Q5. How do I handle errors related to CUDA compatibility in WSL2?**

- Ensure that the CUDA version installed is compatible with your NVIDIA driver version. The [CUDA Compatibility Guide](https://docs.nvidia.com/deploy/cuda-compatibility/index.html) provides a detailed compatibility matrix. If compatibility issues persist, consider reverting to a stable setup using the configuration provided in `env_config_stable.txt`. Also, make sure that any installed libraries are compatible with the chosen CUDA version.

**Q6. Is it possible to run multiple configurations (latest and stable) on the same machine?**

- Yes, you can run both configurations by switching between `env_config_latest.txt` and `env_config_stable.txt`. Ensure that you clean up any conflicting installations before switching to avoid issues. The script’s automatic backup and reversion features can be helpful when managing multiple configurations, allowing you to revert to a known working state if something goes wrong during the switch.

**Q7. Why does the script require sudo access in WSL2, and how secure is it?**

- Sudo access is necessary for administrative tasks such as installing packages and configuring system resources. The script uses your WSL password securely, but for added security, you can prompt for the password at runtime or use environment variables to store it securely. The configuration files allow you to store the password directly, which can streamline the setup process but should be handled carefully.

**Q8. How do I resolve conflicts between the Nvidia RTX Experience application and this script?**

- To avoid conflicts, use either the script or the Nvidia RTX Experience for driver management, not both. If you prefer manual management, disable the script’s driver installation feature by commenting out the relevant lines in the configuration file. If conflicts arise after using Nvidia RTX Experience, the script’s backup and reversion features can help restore your environment.

**Q9. What should I do if WSL2 fails to recognize my GPU after running the script?**

- If WSL2 fails to recognize your GPU, ensure your distribution is up to date and the GPU is properly configured in the settings. You may also use the script’s reversion feature to restore the environment to its previous state before the changes were made. For more detailed guidance, consult the [Microsoft WSL GPU documentation](https://docs.microsoft.com/en-us/windows/wsl/tutorials/gpu-compute).

**Q10. Can I customize the memory and swap allocation for WSL2?**

- Yes, memory and swap allocations can be customized in the configuration files (`env_config_latest.txt` and `env_config_stable.txt`) under the `MEMORY` and `SWAP` parameters. This feature allows fine-tuning of your WSL2 environment’s performance, especially for resource-intensive tasks. For additional tips on configuring WSL2, refer to [Microsoft’s WSL configuration guide](https://docs.microsoft.com/en-us/windows/wsl/wsl-config).

**Q11. How does the script handle restarts, and what should I do after a restart?**

- The script logs when a restart is necessary due to configuration changes or driver updates. After the restart, simply re-run the script, and it will pick up where it left off, ensuring a smooth and uninterrupted setup process.

**Q12. What do I do if I encounter a “command not found” error during script execution?**

- A “command not found” error typically indicates that the required tools are either not installed or not properly configured in your PATH. The script attempts to install all necessary tools, but if this error occurs, manually install the missing tools and verify your PATH configuration. Additional help can be found in [WSL2 setup documentation](https://docs.microsoft.com/en-us/windows/wsl/install).

**Q13. Can I use this script with non-Nvidia GPUs?**

- The `build_env_lib` module is specifically designed for Nvidia GPUs that support CUDA. If you are using a non-Nvidia GPU, you will need alternative tools designed for your GPU brand, such as AMD’s ROCm. For Nvidia GPU setups, this script ensures optimal configuration and support for CUDA operations.

**Q14. How do I switch between different Python versions within the environment?**

- The Python version used in the environment is specified in the configuration files under the `CONDA_PYTHON_VERSION` parameter. You can switch versions by editing this value and re-running the script. Ensure the selected Python version is compatible with other libraries and tools in your environment. The [Python documentation](https://www.python.org/doc/) provides more information on version compatibility.

**Q15. How do I add additional libraries or tools to the environment setup?**

- To add libraries or tools, edit the configuration file and include the required libraries in the relevant sections (`CONDA_FORGE_LIBRARIES`, `RAPIDS_NVIDIA_LIBRARIES`, `CONDA_LIBRARIES`, `PIP_LIBRARIES`). The script will install these during the environment setup. Ensure that new libraries are compatible with your existing setup. Refer to [Conda documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html) for more guidance.

---

### **11. Appendices**

**A. References and Source Links**

1. [Microsoft WSL Installation Guide](https://docs.microsoft.com/en-us/windows/wsl/install)
2. [NVIDIA WSL User Guide](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)
3. [RAPIDS Installation Documentation](https://docs.rapids.ai/install)
4. [NVIDIA CUDA Compatibility Guide](https://docs.nvidia.com/deploy/cuda-compatibility/index.html)
5. [Python Official Documentation](https://www.python.org/doc/)
6. [Conda Package Management](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html)

**B. Known Issues and Workarounds**

1. **nvidia-smi Segmentation Fault:**
   - This issue is discussed in [GitHub Issue #11277](https://github.com/microsoft/WSL/issues/11277). The segmentation fault occurs in WSL2 with certain NVIDIA driver versions but typically does not affect CUDA operations. If this issue arises, consider using the stable configuration (`env_config_stable.txt`) or consult the issue thread for potential fixes.

2. **WSL2 GPU Recognition:**
   - If WSL2 fails to recognize your GPU after setup, check the [Microsoft WSL GPU Compute documentation](https://docs.microsoft.com/en-us/windows/wsl/tutorials/gpu-compute) for troubleshooting tips. The automatic backup and reversion features of the script can also help recover from such issues.

This comprehensive documentation, complete with FAQs and appendices, should provide a robust reference for users of the `build_env_lib` module, helping ensure a smooth setup and maintenance of their GPU-accelerated WSL2 environments.
