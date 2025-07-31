#!/data/data/com.termux/files/usr/bin/bash

clear

echo -e "\e[1;36mWelcome to the Harbinger setup screen :)\e[0m"
echo "Checking if Python is installed..."
sleep 1

# Check for Python
if ! command -v python >/dev/null 2>&1; then
  echo -e "\e[33mPython is not installed.\e[0m"
  sleep 1
  echo -e "\e[34mInstalling Python...\e[0m"
  sleep 1
  pkg install python -y
  echo -e "\e[32mPython installation complete!\e[0m"
else
  echo -e "\e[32mPython is already installed, proceeding...\e[0m"
  sleep 1
fi

# Install requirements
echo
echo "Checking for requirements.txt..."
if [ -f "requirements.txt" ]; then
  echo -e "\e[34mInstalling required Python packages...\e[0m"
  sleep 1
  pip install -r requirements.txt
  echo -e "\e[32mPython packages installed.\e[0m"
else
  echo -e "\e[31mrequirements.txt not found! Skipping Python package installation.\e[0m"
fi

# Install termux-api
echo
echo -e "\e[34mInstalling termux-api...\e[0m"
sleep 1
pkg install termux-api -y
echo -e "\e[32mtermux-api installed.\e[0m"

# Setup storage
echo
echo -e "\e[34mSetting up Termux storage (you may get a prompt)...\e[0m"
termux-setup-storage
sleep 1

# Trigger location permission prompt
echo
echo -e "\e[34mTriggering location permission setup...\e[0m"
termux-wifi-scaninfo >/dev/null 2>&1
echo -e "\e[32mLocation setup done.\e[0m"

# Finish
echo
echo -e "\e[1;35mAll done! Harbinger is ready to use.\e[0m"

echo "Now run: python main.py (ensure you are in the same path as the python source code)"
