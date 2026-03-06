# UX PRO VIP V7 — Ultra Secure

[![Python](https://img.shields.io/badge/Python-3.10%2B-00d4ff?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-8b5cf6?style=for-the-badge&logo=linux&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-Premium-f59e0b?style=for-the-badge&logo=firebase&logoColor=white)](https://t.me/U9KNOWN_X)
[![Status](https://img.shields.io/badge/Status-Active-10b981?style=for-the-badge)](#)
[![Telegram](https://img.shields.io/badge/Contact-Telegram-00d4ff?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/U9KNOWN_X)

> **⚡ The most advanced AI-powered binary options signal bot for Quotex.**
> Built with a 3-model AI ensemble, real-time market regime detection, and military-grade license protection.

---

## 🧠 What Makes UX PRO Different?

Most bots use a single indicator. UX PRO uses **3 AI models + 31 technical features** working together to generate high-confidence signals — and it only trades when everything aligns.

```
Market Data  ──►  31+ Features  ──►  XGBoost  ──┐
                                     LightGBM ──┼──►  Ensemble Vote  ──►  Signal ✅
                                     CatBoost ──┘
```

---

## ✨ Features

### 🤖 AI Engine
- XGBoost + LightGBM + CatBoost ensemble
- Adaptive model weighting (last 50 trades)
- 31+ technical indicators (RSI, MACD, BB, CCI, Williams %R, Momentum...)
- Auto-adapts to live market performance

### 📊 Smart Analysis
- Market Regime Engine (Trending / Ranging / Volatile / Calm)
- Multi-Timeframe Confirmation (1m / 5m / 15m)
- Confidence scoring per signal
- Per-asset & per-timeframe performance analytics

### ⚙️ Trading Modes

| Mode | Risk | Best For |
|---|---|---|
| `SAFE` | 🟢 Low | Beginners |
| `NORMAL` | 🟡 Medium | Daily use |
| `AGGRESSIVE` | 🟠 High | Experienced |
| `ELITE` | 🔴 Max | Experts only |

### 🔒 Security
- Hardware-locked device binding
- Remote license validation via secure server
- Session token system (60s expiry, one-time use)
- Encrypted core — never stored on disk
- Anti-debug self-destruct system

---

## 📋 Requirements

- ✅ **Python 3.10+** installed
- ✅ A **Quotex** account (email + password)
- ✅ A **Telegram Bot Token** — get one from [@BotFather](https://t.me/BotFather)
- ✅ Your **Telegram Chat ID** — get it from [@userinfobot](https://t.me/userinfobot)
- ✅ A valid **UX PRO License Key** — contact [@U9KNOWN_X](https://t.me/U9KNOWN_X)

---

## 📦 Installation

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Mamun-404/ux-pro-v7-ultra.git
cd ux-pro-v7-ultra/uxpro
```

### Step 2 — Setup Environment & Dependencies

**Linux / VPS / Termux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r req.txt
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r req.txt
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r req.txt
```

### Step 3 — Run

**Linux / VPS / Termux / macOS:**
```bash
python3 ux.py
```

**Windows:**
```cmd
python ux.py
```

---

## 🎮 How It Works

```
python ux.py
🔑 License Key: _______________
🔍 Authenticating...
✅ Core Unlocked. Launching...
```

The bot securely fetches and loads the core from our server using your license key. Nothing sensitive is stored on your machine.

**You will be asked for:**

| # | Input | Description |
|---|---|---|
| 1 | Quotex Email | Your Quotex account email |
| 2 | Quotex Password | Your Quotex account password |
| 3 | Telegram Bot Token | From [@BotFather](https://t.me/BotFather) |
| 4 | Telegram Chat ID | From [@userinfobot](https://t.me/userinfobot) |
| 5 | Strategy | Choose `Ultra Hybrid` for best results |
| 6 | Timeframe | `1`, `2`, or `5` minutes |
| 7 | Trade Amount | Amount in USD per trade |
| 8 | Mode | `SAFE` recommended for beginners |

> 🔐 Your credentials are encrypted with a hardware-derived key and saved locally. You won't need to re-enter them next time.

---

## ⚡ Quick Run (One-Click Shortcut)

**Linux / VPS / Termux:**
```bash
echo "alias ux='cd $(pwd) && source .venv/bin/activate && python ux.py'" >> ~/.bashrc && source ~/.bashrc
```

Then just type `ux` to start.

---

## 💎 Pricing & Access

| Plan | Price | Duration |
|---|---|---|
| 🚀 **Starter** | **$2** | 1 Day |
| 🔥 **Popular** | **$5** | 3 Days |
| ⭐ **Weekly** | **$10** | 7 Days |
| 💎 **Monthly** | **$30** | 1 Month |

📌 Full features on all plans | 📌 Instant activation | 📌 Priority support on monthly

**📩 [Click here to get instant access → @U9KNOWN_X](https://t.me/U9KNOWN_X)**

---

## 📁 Project Structure

```
ux-pro-v7-ultra/
│
├── uxpro/
│   ├── ux.py                  # Secure loader (entry point)
│   ├── req.txt                # Python dependencies
│   │
│   ├── models/                # AI model files
│   │   ├── xgboost_model.pkl
│   │   ├── lightgbm_model.pkl
│   │   ├── catboost_model.pkl
│   │   ├── scalers.pkl
│   │   └── performance.json
│   │
│   └── pyquotex/              # Quotex WebSocket API
│
├── .gitignore
├── README.md
└── SETUP.md
```

---

## 🛠️ Troubleshooting

**❌ "Invalid or Expired License"**
Your license has expired or the key is wrong. Contact [@U9KNOWN_X](https://t.me/U9KNOWN_X) to renew.

**❌ "Auth Error: device_id mismatch"**
Your license is bound to a different machine. Contact the owner to reset your device binding.

**❌ "Server timeout"**
Server may be waking up (free tier). Wait 30 seconds and try again.

**❌ Missing packages / pip errors**
```bash
pip install -r req.txt --upgrade
```
Make sure you're using Python 3.10 or higher.

**❌ Bot keeps disconnecting on VPS**
Check that your VPS allows outbound traffic on ports `80` and `443`.

---

## 📞 Contact & Support

| | |
|---|---|
| 👨‍💻 **Developer** | Mamun Hasan (Unknown X) |
| 📱 **Telegram** | [@U9KNOWN_X](https://t.me/U9KNOWN_X) |
| 📢 **Channel** | [Unknown X Official](https://t.me/unknown_x_official) |

---

## ⚠️ Disclaimer

> Trading binary options involves **significant financial risk**. Past performance does not guarantee future results. This software is provided for **educational and research purposes only**. The developer is not responsible for any financial losses incurred through the use of this software. Always trade responsibly and never invest more than you can afford to lose.

---

**© 2025 Unknown X — UX PRO VIP Trading Bot · All Rights Reserved.**

---

## 🔗 Related Repositories

- [UX Pro License Server V2](https://github.com/Mamun-404/uxpro-license-server-v2) — Remote license validation backend.
- [UX Pro V7 Ultra](https://github.com/Mamun-404/ux-pro-v7-ultra) — Main trading bot repository.
