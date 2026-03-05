# 🚀 UX PRO VIP Setup Guide

This guide provides comprehensive instructions to set up your environment for UX PRO VIP, covering Python installation, Quotex account creation, Telegram bot setup, and Git usage across various operating systems.

---

## 1. Python Installation (Python 3.10+)

UX PRO VIP requires Python 3.10 or newer. Follow the instructions below based on your operating system.

### 🐍 Windows

1.  **Download Python**: Go to the official Python website: [python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2.  Download the latest Python 3.10.x or newer installer (e.g., "Windows installer (64-bit)").
3.  **Run Installer**: Double-click the downloaded `.exe` file.
4.  **Important**: On the first screen, **check "Add Python X.Y to PATH"** before clicking "Install Now". This ensures Python is accessible from your command line.
5.  Follow the on-screen prompts to complete the installation.
6.  **Verify Installation**: Open Command Prompt or PowerShell and type:
    ```bash
    python --version
    pip --version
    ```
    You should see Python 3.10.x or higher and pip versions.

### 🐧 Linux (Ubuntu/Debian)

Most modern Linux distributions come with Python pre-installed. Ensure it's version 3.10+.

1.  **Update System**: 
    ```bash
    sudo apt update
    sudo apt upgrade -y
    ```
2.  **Install Python 3.11 (if not present or older)**:
    ```bash
    sudo apt install software-properties-common -y
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install python3.11 python3.11-venv python3.11-dev -y
    ```
3.  **Set as Default (Optional but Recommended)**:
    ```bash
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
    ```
4.  **Verify Installation**: Open your terminal and type:
    ```bash
    python3 --version
    pip3 --version
    ```
    You should see Python 3.11.x or higher and pip versions.

### 🍎 macOS

macOS usually has Python 2 pre-installed. You need Python 3.10+.

1.  **Install Homebrew (if not installed)**:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
2.  **Install Python 3.11 (or newer)**:
    ```bash
    brew install python@3.11
    ```
3.  **Verify Installation**: Open Terminal and type:
    ```bash
    python3 --version
    pip3 --version
    ```
    You should see Python 3.11.x or higher and pip versions.

---

## 2. Quotex Account Creation

UX PRO VIP interacts with the Quotex trading platform. You need an active Quotex account.

1.  **Register**: Visit the official Quotex website: [quotex.com](https://quotex.com)
2.  Click on "Sign Up" or "Registration".
3.  Fill in the required details (email, password, currency).
4.  **Verify Email**: Check your email for a verification link from Quotex and click it to activate your account.
5.  **Fund Account (Optional)**: To trade with real money, you'll need to deposit funds. For testing, a demo account is sufficient.

---

## 3. Telegram Bot Setup
UX PRO VIP uses Telegram for notifications and interaction. You need a Telegram Bot Token and your Chat ID.

### 🤖 Get a Telegram Bot Token

1.  **Open Telegram**: Search for `@BotFather` in Telegram and start a chat.
2.  **Create New Bot**: Send the command `/newbot`.
3.  **Name Your Bot**: Follow the instructions to choose a name and a username for your bot. The username must end with `bot` (e.g., `MyAwesomeBot`).
4.  **Save Token**: BotFather will provide you with an HTTP API token (e.g., `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`). **Keep this token secure and private.**

### 🆔 Get Your Telegram Chat ID

1.  **Open Telegram**: Search for `@userinfobot` in Telegram and start a chat.
2.  **Get ID**: Send the command `/start` or any message. The bot will reply with your Chat ID (a numerical value).
3.  **Save Chat ID**: Note down this Chat ID.

---

## 4. Git Installation and Usage

Git is essential for cloning the UX PRO VIP repository. Instructions vary slightly by OS.

### 💻 Windows

1.  **Download Git**: Go to [git-scm.com/download/win](https://git-scm.com/download/win)
2.  Download the latest version of Git for Windows.
3.  **Run Installer**: Double-click the downloaded `.exe` file.
4.  **Installation Options**: During installation, you can generally accept the default options. Ensure "Git Bash Here" and "Git GUI Here" are selected for easy access.
5.  **Verify Installation**: Open Command Prompt or PowerShell and type:
    ```bash
    git --version
    ```
    You should see the installed Git version.

### 🐧 Linux (Ubuntu/Debian)

1.  **Install Git**: Open your terminal and run:
    ```bash
    sudo apt update
    sudo apt install git -y
    ```
2.  **Verify Installation**: 
    ```bash
    git --version
    ```

### 🍎 macOS

Git is often pre-installed or can be installed via Xcode Command Line Tools.

1.  **Install Git (via Homebrew)**:
    ```bash
    brew install git
    ```
    (If Homebrew is not installed, see Python installation section)
2.  **Verify Installation**: Open Terminal and type:
    ```bash
    git --version
    ```

### 📥 Cloning the Repository

Once Git is installed, you can clone the UX PRO VIP repository:

```bash
git clone https://github.com/Mamun-404/ux-pro-v7-ultra.git
cd ux-pro-v7-ultra/uxpro
```

---

## 5. Virtual Environment (Recommended)

Using a virtual environment isolates your project's dependencies from other Python projects.

### 💻 Windows (CMD)

```cmd
# Navigate to your project directory
cd /d "C:\path\to\ux-pro-v7-ultra\uxpro"
python -m venv .venv
.venv\Scripts\activate
```

### 💻 Windows (PowerShell)

```powershell
# Navigate to your project directory
cd "C:\path\to\ux-pro-v7-ultra\uxpro"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 🐧 Linux / macOS / VPS

```bash
# Navigate to your project directory
cd /home/youruser/ux-pro-v7-ultra/uxpro
python3 -m venv .venv
source .venv/bin/activate
```

---

## 6. Install Project Dependencies

After activating your virtual environment, install the required Python packages:

```bash
pip install -r req.txt
```

---

## 7. Set FERNET_KEY

This key is crucial for the bot to function. Set it as an environment variable.

### 💻 Windows (CMD)

```cmd
set FERNET_KEY=tZcmnUPBtWCI7vzLFMowpZjwm4uG_icBYo72y1p6dRQ=
```

### 💻 Windows (PowerShell)

```powershell
$env:FERNET_KEY="tZcmnUPBtWCI7vzLFMowpZjwm4uG_icBYo72y1p6dRQ="
```

### 🐧 Linux / macOS / VPS

```bash
export FERNET_KEY="tZcmnUPBtWCI7vzLFMowpZjwm4uG_icBYo72y1p6dRQ="
```

> 💡 **Tip for VPS:** To make the `FERNET_KEY` persistent across reboots, add the `export` command to your shell profile (e.g., `~/.bashrc` or `~/.zshrc`):

```bash
echo 'export FERNET_KEY="tZcmnUPBtWCI7vzLFMowpZjwm4uG_icBYo72y1p6dRQ="' >> ~/.bashrc && source ~/.bashrc
```

---

## 8. Run the Bot

Finally, with all dependencies installed and the `FERNET_KEY` set, you can run the bot:

```bash
python ux.py
```

This will start the UX PRO VIP bot, and it will guide you through the remaining setup steps (Quotex credentials, Telegram details, etc.).

---

**© 2025 Unknown X — UX PRO VIP Trading Bot · All Rights Reserved.**
