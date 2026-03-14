#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║              SIYAM BOT — Quotex AI Trading Bot              ║
║          pyquotex • XGBoost • LightGBM • CatBoost          ║
╚══════════════════════════════════════════════════════════════╝
  Balance Check · Trade Execution · Win/Loss Monitor
  Real-time signals · Martingale · Telegram Alerts
"""

import os
import sys
import json
import time
import asyncio
import logging
import hashlib
import platform
import traceback
from datetime import datetime, timezone
from pathlib import Path

# ── Optional coloured output ──────────────────────────────────
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
    GREEN   = Fore.GREEN
    RED     = Fore.RED
    YELLOW  = Fore.YELLOW
    CYAN    = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    WHITE   = Fore.WHITE
    BLUE    = Fore.BLUE
    RESET   = Style.RESET_ALL
    BRIGHT  = Style.BRIGHT
except ImportError:
    GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = BLUE = RESET = BRIGHT = ""

# ── Optional ML / numeric libs ────────────────────────────────
try:
    import numpy as np
    import pandas as pd
    import joblib
    HAS_ML = True
except ImportError:
    HAS_ML = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False

# ─────────────────────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
MODELS_DIR    = BASE_DIR / "models"
CONFIG_FILE   = BASE_DIR / ".siyam_config.json"
MTG_FILE      = BASE_DIR / ".mtg_config.json"
STATS_FILE    = BASE_DIR / ".siyam_stats.json"
LOG_FILE      = BASE_DIR / "siyam_activity.log"

# ─────────────────────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("siyam")


# ═════════════════════════════════════════════════════════════
#  UTILITY HELPERS
# ═════════════════════════════════════════════════════════════

def clr(text: str, color: str = WHITE, bold: bool = False) -> str:
    b = BRIGHT if bold else ""
    return f"{b}{color}{text}{RESET}"

def banner():
    os.system("cls" if platform.system() == "Windows" else "clear")
    print(clr("""
╔══════════════════════════════════════════════════════════════╗
║          💎  SIYAM BOT  —  Quotex AI Trading Bot            ║
║          ✦  XGBoost + LightGBM + CatBoost Ensemble ✦        ║
╚══════════════════════════════════════════════════════════════╝""", CYAN, True))

def divider(char="─", width=62):
    print(clr(char * width, CYAN))

def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

# ─────────────────────────────────────────────────────────────
#  CONFIG  (load / save)
# ─────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "email": "",
    "password": "",
    "telegram_token": "",
    "telegram_chat_id": "",
    "timeframe": 1,
    "trade_amount": 1.0,
    "mode": "NORMAL",
    "account_type": "PRACTICE",
    "domain": "global",
    "timezone_offset": 6,
    "target_profit": 0.0,
    "stop_loss": 0.0,
    "signal_style": 1,
    "telegram_channel": "",
    "ai_learning": True,
}

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return {**DEFAULT_CONFIG, **json.loads(CONFIG_FILE.read_text())}
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)

def save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

DEFAULT_MTG = {
    "enabled": True,
    "multiplier": 2.0,
    "max_levels": 3,
    "wait_seconds": 60,
}

def load_mtg() -> dict:
    if MTG_FILE.exists():
        try:
            return {**DEFAULT_MTG, **json.loads(MTG_FILE.read_text())}
        except Exception:
            pass
    return dict(DEFAULT_MTG)

def save_mtg(mtg: dict):
    MTG_FILE.write_text(json.dumps(mtg, indent=2))

DEFAULT_STATS = {
    "total_trades": 0,
    "wins": 0,
    "losses": 0,
    "profit": 0.0,
    "session_profit": 0.0,
    "history": [],
}

def load_stats() -> dict:
    if STATS_FILE.exists():
        try:
            return {**DEFAULT_STATS, **json.loads(STATS_FILE.read_text())}
        except Exception:
            pass
    return dict(DEFAULT_STATS)

def save_stats(st: dict):
    if len(st.get("history", [])) > 200:
        st["history"] = st["history"][-200:]
    STATS_FILE.write_text(json.dumps(st, indent=2))


# ═════════════════════════════════════════════════════════════
#  TELEGRAM ALERT
# ═════════════════════════════════════════════════════════════

def send_telegram(token: str, chat_id: str, message: str) -> bool:
    if not HAS_REQUESTS or not token or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={"chat_id": chat_id, "text": message,
                                        "parse_mode": "HTML"}, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.warning(f"Telegram error: {e}")
        return False


# ═════════════════════════════════════════════════════════════
#  TECHNICAL INDICATORS  (pure-Python / numpy)
# ═════════════════════════════════════════════════════════════

def _ema(prices, period):
    if len(prices) < period:
        return []
    k = 2 / (period + 1)
    ema = [sum(prices[:period]) / period]
    for p in prices[period:]:
        ema.append(p * k + ema[-1] * (1 - k))
    return ema

def _rsi(prices, period=14):
    if not HAS_ML or len(prices) < period + 1:
        return None
    deltas = np.diff(prices)
    gain = np.where(deltas > 0, deltas, 0.0)
    loss = np.where(deltas < 0, -deltas, 0.0)
    ag = np.mean(gain[:period])
    al = np.mean(loss[:period])
    for i in range(period, len(gain)):
        ag = (ag * (period - 1) + gain[i]) / period
        al = (al * (period - 1) + loss[i]) / period
    rs = ag / (al if al != 0 else 1e-10)
    return round(100 - 100 / (1 + rs), 2)

def _macd(prices, fast=12, slow=26, signal=9):
    fast_ema = _ema(prices, fast)
    slow_ema = _ema(prices, slow)
    if not fast_ema or not slow_ema:
        return None, None, None
    diff = len(fast_ema) - len(slow_ema)
    macd_line = [fast_ema[i + diff] - slow_ema[i] for i in range(len(slow_ema))]
    sig_line   = _ema(macd_line, signal)
    if not sig_line:
        return macd_line[-1], None, None
    hist = macd_line[-1] - sig_line[-1]
    return round(macd_line[-1], 5), round(sig_line[-1], 5), round(hist, 5)

def _bollinger(prices, period=20, std_dev=2):
    if len(prices) < period:
        return None, None, None
    window = prices[-period:]
    mid = sum(window) / period
    if HAS_ML:
        sd = float(np.std(window))
    else:
        mean = mid
        sd = (sum((x - mean) ** 2 for x in window) / period) ** 0.5
    return round(mid + std_dev * sd, 5), round(mid, 5), round(mid - std_dev * sd, 5)

def _stoch(highs, lows, closes, k=14, d=3):
    if len(closes) < k:
        return None, None
    lo = min(lows[-k:]);  hi = max(highs[-k:])
    if hi == lo:
        return 50.0, 50.0
    k_val = round((closes[-1] - lo) / (hi - lo) * 100, 2)
    d_val = round(sum(
        (closes[-(k - i)] - min(lows[-(k - i):-(i) if i else None])) /
        (max(highs[-(k - i):-(i) if i else None]) - min(lows[-(k - i):-(i) if i else None]) + 1e-10) * 100
        for i in range(d)
    ) / d, 2)
    return k_val, d_val

def _williams_r(highs, lows, closes, period=14):
    if len(closes) < period:
        return None
    hi = max(highs[-period:]);  lo = min(lows[-period:])
    if hi == lo:
        return -50.0
    return round((hi - closes[-1]) / (hi - lo) * -100, 2)

def _cci(highs, lows, closes, period=20):
    if len(closes) < period:
        return None
    tp = [(highs[i] + lows[i] + closes[i]) / 3 for i in range(-period, 0)]
    mean_tp = sum(tp) / period
    mad = sum(abs(x - mean_tp) for x in tp) / period
    return round((tp[-1] - mean_tp) / (0.015 * mad + 1e-10), 2)

def _atr(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return None
    trs = [max(highs[i] - lows[i],
               abs(highs[i] - closes[i - 1]),
               abs(lows[i] - closes[i - 1])) for i in range(-period, 0)]
    return round(sum(trs) / period, 5)

def _momentum(prices, period=10):
    if len(prices) < period:
        return None
    return round(prices[-1] - prices[-period], 5)

def build_features(candles: list) -> dict:
    """Extract 31+ indicator features from raw candle list."""
    if len(candles) < 30:
        return {}
    closes = [c["close"] for c in candles]
    highs  = [c["high"]  for c in candles]
    lows   = [c["low"]   for c in candles]

    rsi    = _rsi(closes)
    macd, macd_sig, macd_hist = _macd(closes)
    bb_up, bb_mid, bb_low = _bollinger(closes)
    stk, std  = _stoch(highs, lows, closes)
    willr = _williams_r(highs, lows, closes)
    cci   = _cci(highs, lows, closes)
    atr   = _atr(highs, lows, closes)
    mom   = _momentum(closes)
    ema5  = (_ema(closes, 5) or [None])[-1]
    ema10 = (_ema(closes, 10) or [None])[-1]
    ema20 = (_ema(closes, 20) or [None])[-1]
    ema50 = (_ema(closes, 50) or [None])[-1]
    sma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None

    return {
        "rsi": rsi,
        "macd": macd,
        "macd_signal": macd_sig,
        "macd_hist": macd_hist,
        "bb_upper": bb_up,
        "bb_mid": bb_mid,
        "bb_lower": bb_low,
        "stoch_k": stk,
        "stoch_d": std,
        "williams_r": willr,
        "cci": cci,
        "atr": atr,
        "momentum": mom,
        "ema5": ema5,
        "ema10": ema10,
        "ema20": ema20,
        "ema50": ema50,
        "sma20": sma20,
        "close": closes[-1],
        "prev_close": closes[-2],
        "high": highs[-1],
        "low": lows[-1],
        "price_change": closes[-1] - closes[-2],
        "price_change_pct": ((closes[-1] - closes[-2]) / closes[-2]) * 100 if closes[-2] else 0,
        "candle_range": highs[-1] - lows[-1],
        "body_size": abs(closes[-1] - candles[-1]["open"]),
        "upper_wick": highs[-1] - max(closes[-1], candles[-1]["open"]),
        "lower_wick": min(closes[-1], candles[-1]["open"]) - lows[-1],
        "volume_ratio": 1.0,  # placeholder if volume unavailable
    }


# ═════════════════════════════════════════════════════════════
#  AI MODEL MANAGER
# ═════════════════════════════════════════════════════════════

FEATURE_COLS = [
    "rsi", "macd", "macd_signal", "macd_hist",
    "bb_upper", "bb_mid", "bb_lower",
    "stoch_k", "stoch_d", "williams_r", "cci", "atr",
    "momentum", "ema5", "ema10", "ema20", "ema50", "sma20",
    "close", "prev_close", "high", "low",
    "price_change", "price_change_pct", "candle_range",
    "body_size", "upper_wick", "lower_wick", "volume_ratio",
]

class AIEngine:
    """Loads XGBoost / LightGBM / CatBoost from models/ and runs ensemble voting."""

    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.xgb = None
        self.lgb = None
        self.cat = None
        self.scaler = None
        self.weights = {"xgb": 1.0, "lgb": 1.0, "cat": 1.0}
        self._load()

    def _load(self):
        if not HAS_ML:
            return
        try:
            xgb_path = self.models_dir / "xgboost_model.pkl"
            lgb_path  = self.models_dir / "lightgbm_model.pkl"
            cat_path  = self.models_dir / "catboost_model.pkl"
            scl_path  = self.models_dir / "scalers.pkl"
            perf_path = self.models_dir / "performance.json"

            if xgb_path.exists(): self.xgb = joblib.load(xgb_path)
            if lgb_path.exists():  self.lgb = joblib.load(lgb_path)
            if cat_path.exists():  self.cat = joblib.load(cat_path)
            if scl_path.exists():  self.scaler = joblib.load(scl_path)
            if perf_path.exists():
                perf = json.loads(perf_path.read_text())
                # use model accuracy as weight
                self.weights["xgb"] = perf.get("xgb_accuracy", 1.0)
                self.weights["lgb"] = perf.get("lgb_accuracy", 1.0)
                self.weights["cat"] = perf.get("cat_accuracy", 1.0)
            logger.info("AI models loaded successfully.")
        except Exception as e:
            logger.warning(f"Model load warning: {e}")

    def predict(self, features: dict):
        """Returns (direction, confidence) or (None, 0)."""
        if not HAS_ML or not features:
            return self._heuristic_signal(features)

        # Build feature vector
        row = [features.get(c, 0.0) or 0.0 for c in FEATURE_COLS]
        try:
            X = pd.DataFrame([row], columns=FEATURE_COLS)
            if self.scaler:
                X_sc = self.scaler.transform(X)
            else:
                X_sc = X.values

            votes = []
            probs = []

            for name, model, w in [("xgb", self.xgb, self.weights["xgb"]),
                                    ("lgb", self.lgb, self.weights["lgb"]),
                                    ("cat", self.cat, self.weights["cat"])]:
                if model is None:
                    continue
                try:
                    p = model.predict_proba(X_sc)[0]
                    # assume class 1 = CALL, 0 = PUT
                    prob_call = p[1] if len(p) > 1 else p[0]
                    votes.append((prob_call - 0.5) * w)
                    probs.append(prob_call)
                except Exception:
                    pass

            if not votes:
                return self._heuristic_signal(features)

            score = sum(votes) / sum(self.weights.values())
            avg_prob = sum(probs) / len(probs)
            confidence = round(abs(avg_prob - 0.5) * 200, 1)  # 0–100 %

            direction = "CALL" if score > 0 else "PUT"
            return direction, confidence

        except Exception as e:
            logger.warning(f"Predict error: {e}")
            return self._heuristic_signal(features)

    def _heuristic_signal(self, features: dict):
        """Fallback rule-based signal when models unavailable."""
        if not features:
            return None, 0

        score = 0
        # RSI
        rsi = features.get("rsi")
        if rsi is not None:
            if rsi < 30:  score += 2
            elif rsi > 70: score -= 2

        # MACD histogram
        hist = features.get("macd_hist")
        if hist is not None:
            score += 1 if hist > 0 else -1

        # Bollinger
        close = features.get("close", 0)
        bb_lower = features.get("bb_lower")
        bb_upper = features.get("bb_upper")
        if bb_lower and close < bb_lower: score += 1
        if bb_upper and close > bb_upper: score -= 1

        # EMA trend
        ema5  = features.get("ema5")
        ema20 = features.get("ema20")
        if ema5 and ema20:
            score += 1 if ema5 > ema20 else -1

        # Stochastic
        stk = features.get("stoch_k")
        if stk is not None:
            if stk < 20: score += 1
            elif stk > 80: score -= 1

        if score == 0:
            return None, 0
        direction = "CALL" if score > 0 else "PUT"
        confidence = min(abs(score) * 10, 90)
        return direction, confidence


# ═════════════════════════════════════════════════════════════
#  MARKET REGIME DETECTOR
# ═════════════════════════════════════════════════════════════

def detect_regime(candles: list) -> str:
    """Trending / Ranging / Volatile."""
    if len(candles) < 20:
        return "UNKNOWN"
    closes = [c["close"] for c in candles[-20:]]
    atr = _atr(
        [c["high"]  for c in candles[-20:]],
        [c["low"]   for c in candles[-20:]],
        closes, 14
    ) or 0
    if HAS_ML:
        std_close = float(np.std(closes))
    else:
        mean = sum(closes) / len(closes)
        std_close = (sum((x - mean) ** 2 for x in closes) / len(closes)) ** 0.5

    ema10_list = _ema(closes, 10)
    trend = abs(ema10_list[-1] - ema10_list[0]) if len(ema10_list) >= 2 else 0

    if atr > std_close * 1.5:
        return "VOLATILE"
    if trend > std_close:
        return "TRENDING"
    return "RANGING"


# ═════════════════════════════════════════════════════════════
#  STATS TRACKER
# ═════════════════════════════════════════════════════════════

class StatsTracker:
    def __init__(self):
        self.data = load_stats()
        self.data["session_profit"] = 0.0

    def record(self, asset: str, direction: str, amount: float,
               win: bool, payout: float = 0.0):
        profit = payout - amount if win else -amount
        self.data["total_trades"] += 1
        if win:
            self.data["wins"] += 1
        else:
            self.data["losses"] += 1
        self.data["profit"] += profit
        self.data["session_profit"] += profit
        self.data["history"].append({
            "time": ts(),
            "asset": asset,
            "direction": direction,
            "amount": amount,
            "win": win,
            "profit": round(profit, 2),
        })
        save_stats(self.data)

    @property
    def win_rate(self) -> float:
        t = self.data["total_trades"]
        return round(self.data["wins"] / t * 100, 1) if t else 0.0

    @property
    def session_profit(self) -> float:
        return round(self.data["session_profit"], 2)

    @property
    def total_profit(self) -> float:
        return round(self.data["profit"], 2)

    def summary(self) -> str:
        d = self.data
        return (
            f"  📊 Trades : {d['total_trades']}  |  "
            f"✅ Wins: {d['wins']}  |  ❌ Losses: {d['losses']}\n"
            f"  📈 Win Rate : {self.win_rate}%\n"
            f"  💰 Session P/L : ${self.session_profit:+.2f}\n"
            f"  💎 Total P/L   : ${self.total_profit:+.2f}"
        )


# ═════════════════════════════════════════════════════════════
#  MARTINGALE MANAGER
# ═════════════════════════════════════════════════════════════

class MartingaleManager:
    def __init__(self, base_amount: float, mtg_cfg: dict):
        self.base       = base_amount
        self.cfg        = mtg_cfg
        self.level      = 0
        self.current    = base_amount

    def reset(self):
        self.level   = 0
        self.current = self.base

    def next_amount(self) -> float:
        if not self.cfg["enabled"] or self.level == 0:
            return self.current
        if self.level >= self.cfg["max_levels"]:
            self.reset()
            return self.base
        self.current = round(self.current * self.cfg["multiplier"], 2)
        return self.current

    def on_loss(self):
        self.level += 1
        if self.level > self.cfg["max_levels"]:
            self.reset()

    def on_win(self):
        self.reset()


# ═════════════════════════════════════════════════════════════
#  QUOTEX CONNECTOR  (wraps pyquotex stable_api)
# ═════════════════════════════════════════════════════════════

class QuotexConnector:
    """Thin async wrapper around pyquotex Quotex class."""

    def __init__(self, cfg: dict):
        self.cfg  = cfg
        self.api  = None
        self._connected = False

    async def connect(self) -> bool:
        try:
            # dynamic import so the script works even if pyquotex not installed
            sys.path.insert(0, str(BASE_DIR))
            from pyquotex.stable_api import Quotex
            self.api = Quotex(
                email=self.cfg["email"],
                password=self.cfg["password"],
                root_path=str(BASE_DIR),
            )
            # account type
            mode = "PRACTICE" if self.cfg["account_type"] == "PRACTICE" else "REAL"
            self.api.set_account_mode(mode)
            ok, _ = await self.api.connect()
            self._connected = bool(ok)
            return self._connected
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    async def get_balance(self) -> float:
        try:
            return await self.api.get_balance()
        except Exception:
            return 0.0

    async def get_profile(self) -> dict:
        try:
            return await self.api.get_profile()
        except Exception:
            return {}

    async def get_candles(self, asset: str, period_min: int = 1, count: int = 100) -> list:
        """Return list of {open,high,low,close,time} dicts."""
        try:
            period_sec = period_min * 60
            end = time.time()
            offset = count * period_sec
            raw = await self.api.get_candles(asset, end, offset, period_sec)
            if not raw:
                return []
            result = []
            for c in raw:
                if isinstance(c, dict):
                    result.append({
                        "open":  c.get("open",  c.get("o", 0)),
                        "high":  c.get("high",  c.get("h", 0)),
                        "low":   c.get("low",   c.get("l", 0)),
                        "close": c.get("close", c.get("c", 0)),
                        "time":  c.get("time",  c.get("t", 0)),
                    })
            return result
        except Exception as e:
            logger.warning(f"get_candles error: {e}")
            return []

    async def buy(self, amount: float, asset: str,
                  direction: str, duration_min: int) -> tuple:
        """Returns (trade_id, success_bool)."""
        try:
            direction_str = direction.lower()  # "call" or "put"
            status, trade_id = await self.api.buy(amount, asset, direction_str,
                                                   duration_min * 60)
            return trade_id, bool(status)
        except Exception as e:
            logger.error(f"Buy error: {e}")
            return None, False

    async def check_win(self, trade_id) -> tuple:
        """Returns (win_bool, payout)."""
        try:
            result = await self.api.check_win(trade_id)
            if result is None:
                return None, 0.0
            if isinstance(result, dict):
                win  = result.get("win", False) or result.get("result") == "win"
                pay  = float(result.get("payout", 0) or result.get("profit", 0))
                return win, pay
            return bool(result), 0.0
        except Exception as e:
            logger.warning(f"check_win error: {e}")
            return None, 0.0

    async def disconnect(self):
        try:
            if self.api:
                await self.api.close()
        except Exception:
            pass


# ═════════════════════════════════════════════════════════════
#  SIGNAL GENERATOR
# ═════════════════════════════════════════════════════════════

MODE_CONF_THRESHOLD = {
    "SAFE":       70,
    "NORMAL":     55,
    "AGGRESSIVE": 40,
    "ELITE":      30,
    "CUSTOM":     50,
}

ASSETS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
    "EURJPY", "GBPJPY", "EURGBP", "NZDUSD", "USDCHF",
    "EURAUD", "Bitcoin (OTC)", "Ethereum (OTC)",
]

class SignalGenerator:
    def __init__(self, connector: QuotexConnector, ai: AIEngine,
                 cfg: dict, stats: StatsTracker, mtg: MartingaleManager):
        self.conn  = connector
        self.ai    = ai
        self.cfg   = cfg
        self.stats = stats
        self.mtg   = mtg
        self.running = False
        self.threshold = MODE_CONF_THRESHOLD.get(cfg.get("mode", "NORMAL"), 55)

    async def scan_asset(self, asset: str) -> dict | None:
        """Scan one asset and return signal dict or None."""
        candles = await self.conn.get_candles(
            asset, period_min=self.cfg.get("timeframe", 1), count=100
        )
        if len(candles) < 30:
            return None
        features = build_features(candles)
        regime   = detect_regime(candles)
        direction, confidence = self.ai.predict(features)
        if direction is None or confidence < self.threshold:
            return None
        return {
            "asset":      asset,
            "direction":  direction,
            "confidence": confidence,
            "regime":     regime,
            "features":   features,
        }

    def format_signal(self, sig: dict, style: int = 1) -> str:
        icon = "🟢" if sig["direction"] == "CALL" else "🔴"
        arrow = "⬆️ CALL" if sig["direction"] == "CALL" else "⬇️ PUT"
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if style == 1:
            return (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  SIYAM BOT  |  Signal Alert\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  {icon} Asset      : {sig['asset']}\n"
                f"  📌 Direction  : {arrow}\n"
                f"  🧠 Confidence : {sig['confidence']}%\n"
                f"  📊 Regime     : {sig['regime']}\n"
                f"  ⏱ Timeframe  : {self.cfg.get('timeframe', 1)}m\n"
                f"  🕐 Time       : {t}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
        else:
            return (
                f"[SIYAM] {sig['asset']} {arrow} | Conf: {sig['confidence']}% | {t}"
            )

    async def execute_trade(self, sig: dict):
        amount = self.mtg.next_amount()
        print(clr(f"\n  💸 Placing trade: {sig['asset']} {sig['direction']} "
                  f"${amount:.2f}  [{self.cfg.get('timeframe',1)}m]", YELLOW))
        logger.info(f"Trade: {sig['asset']} {sig['direction']} ${amount}")

        trade_id, ok = await self.conn.buy(
            amount, sig["asset"], sig["direction"],
            self.cfg.get("timeframe", 1)
        )
        if not ok or trade_id is None:
            print(clr("  ⚠️  Trade placement failed.", RED))
            return

        print(clr(f"  ✅ Trade placed! ID: {trade_id}", GREEN))

        # Wait for result
        wait = self.cfg.get("timeframe", 1) * 60 + 5
        print(clr(f"  ⏳ Waiting {wait}s for result...", CYAN))
        await asyncio.sleep(wait)

        win, payout = await self.conn.check_win(trade_id)
        if win is None:
            print(clr("  ❓ Result pending.", YELLOW))
            return

        self.stats.record(sig["asset"], sig["direction"], amount, win, payout)

        if win:
            self.mtg.on_win()
            profit = payout - amount
            msg = f"  ✅ WIN  +${profit:.2f}  (Payout: ${payout:.2f})"
            print(clr(msg, GREEN, True))
            logger.info(f"WIN {sig['asset']} +${profit:.2f}")
        else:
            self.mtg.on_loss()
            msg = f"  ❌ LOSS  -${amount:.2f}"
            print(clr(msg, RED, True))
            logger.info(f"LOSS {sig['asset']} -${amount:.2f}")

        # Martingale wait
        if not win and self.cfg.get("mtg_enabled", True) and self.mtg.level > 0:
            wt = load_mtg()["wait_seconds"]
            print(clr(f"\n  🎰 MTG Recovery in {wt}s ...", MAGENTA))
            for remaining in range(wt, 0, -1):
                print(f"\r  ⏱ {remaining:3d}s ", end="", flush=True)
                await asyncio.sleep(1)
            print()

        # Telegram alert
        token   = self.cfg.get("telegram_token", "")
        chat_id = self.cfg.get("telegram_chat_id", "")
        result_msg = (
            self.format_signal(sig, self.cfg.get("signal_style", 1)) +
            f"\n\n{'✅ WIN' if win else '❌ LOSS'}  "
            f"{'+ $' + str(round(payout - amount, 2)) if win else '- $' + str(amount)}"
        )
        send_telegram(token, chat_id, result_msg)

        # TP / SL check
        sp = self.stats.session_profit
        tp = float(self.cfg.get("target_profit", 0))
        sl = float(self.cfg.get("stop_loss", 0))
        if tp > 0 and sp >= tp:
            print(clr(f"\n  🎯 Target Profit ${tp} reached! Stopping.", GREEN, True))
            self.running = False
        if sl > 0 and sp <= -sl:
            print(clr(f"\n  🛑 Stop Loss -${sl} hit! Stopping.", RED, True))
            self.running = False

    async def run(self):
        self.running = True
        print(clr(f"\n  🚀 Signal Generator started  [Mode: {self.cfg.get('mode','NORMAL')}]", GREEN, True))
        print(clr(f"  📊 Scanning assets every 30s | Confidence threshold: {self.threshold}%\n", CYAN))
        logger.info("Signal generator started.")

        scan_assets = ASSETS[:8]  # default scan list

        while self.running:
            balance = await self.conn.get_balance()
            print(clr(f"\n[{ts()}] 💰 Balance: ${balance:.2f}", CYAN))

            for asset in scan_assets:
                if not self.running:
                    break
                sig = await self.scan_asset(asset)
                if sig:
                    print(clr(
                        f"  ✨ SIGNAL  {asset}  {sig['direction']}  "
                        f"({sig['confidence']}%)  [{sig['regime']}]", YELLOW, True
                    ))
                    # Send to Telegram
                    send_telegram(
                        self.cfg.get("telegram_token", ""),
                        self.cfg.get("telegram_chat_id", ""),
                        self.format_signal(sig, self.cfg.get("signal_style", 1))
                    )
                    await self.execute_trade(sig)
                    break  # one trade per scan cycle
                else:
                    print(f"  → {asset:<22}  No signal", end="\r")
                await asyncio.sleep(1)

            if self.running:
                print(clr(f"\n  📊 Session P/L: ${self.stats.session_profit:+.2f}  "
                           f"| Win Rate: {self.stats.win_rate}%", CYAN))
                print(clr("  ⏸  Next scan in 30s... (Ctrl+C to stop)\n", WHITE))
                await asyncio.sleep(30)

        print(clr("\n  ⛔ Signal Generator stopped.\n", RED))


# ═════════════════════════════════════════════════════════════
#  FIRST-RUN SETUP
# ═════════════════════════════════════════════════════════════

def first_run_setup(cfg: dict) -> dict:
    banner()
    print(clr("\n  🔧 FIRST-TIME SETUP\n", YELLOW, True))
    divider()

    def ask(prompt, default="", secret=False):
        import getpass
        d = f" [{default}]" if default else ""
        if secret:
            val = getpass.getpass(f"  {prompt}{d}: ")
        else:
            val = input(f"  {prompt}{d}: ").strip()
        return val if val else default

    cfg["email"]            = ask("Quotex Email")
    cfg["password"]         = ask("Quotex Password", secret=True)
    cfg["telegram_token"]   = ask("Telegram Bot Token (optional)")
    cfg["telegram_chat_id"] = ask("Telegram Chat ID  (optional)")
    cfg["timeframe"]        = int(ask("Timeframe minutes [1/2/5]", "1") or 1)
    cfg["trade_amount"]     = float(ask("Trade Amount (USD)", "1") or 1)
    print("\n  Mode options: SAFE / NORMAL / AGGRESSIVE / ELITE")
    cfg["mode"]             = ask("Trading Mode", "NORMAL").upper()
    print("\n  Account options: PRACTICE / REAL")
    cfg["account_type"]     = ask("Account Type", "PRACTICE").upper()

    save_config(cfg)
    print(clr("\n  ✅ Config saved!\n", GREEN))
    return cfg


# ═════════════════════════════════════════════════════════════
#  MENU SYSTEM
# ═════════════════════════════════════════════════════════════

def print_main_menu(cfg: dict):
    banner()
    print(clr(f"""
╔══════════════════════════════════════════════════════════════╗
║              💎  SIYAM BOT  —  Main Menu                    ║
╠══════════════════════════════════════════════════════════════╣
║  1)  🚀  Start Signal Generator                             ║
║  2)  💰  Check Balance                                      ║
║  3)  📊  View Statistics                                    ║
║  4)  📤  Send Test Signal (Telegram)                        ║
║  5)  🧠  Toggle AI Learning  [{('ON' if cfg.get('ai_learning') else 'OFF'):3}]                     ║
║  6)  📋  View Last Trades                                   ║
╠══════════════════════════════════════════════════════════════╣
║  7)  ⚙️   Configuration                                     ║
╠══════════════════════════════════════════════════════════════╣
║  0)  ❌  Exit                                               ║
╚══════════════════════════════════════════════════════════════╝
""", CYAN))

def print_config_menu(cfg: dict):
    banner()
    print(clr(f"""
╔══════════════════════════════════════════════════════════════╗
║                  ⚙️   CONFIGURATION                         ║
╠══════════════════════════════════════════════════════════════╣
║  1)  🌐  Domain         : {cfg.get('domain','global'):<32} ║
║  2)  💳  Account        : {cfg.get('account_type','PRACTICE'):<32} ║
║  3)  🔐  Change Credentials                                 ║
║  4)  🎨  Signal Style   : {cfg.get('signal_style',1):<32} ║
║  5)  ⏰  Timezone UTC   : +{cfg.get('timezone_offset',6):<31} ║
║  6)  🎯  Mode           : {cfg.get('mode','NORMAL'):<32} ║
║  7)  💰  Target Profit  : ${cfg.get('target_profit',0):<31.2f} ║
║  8)  🛑  Stop Loss      : ${cfg.get('stop_loss',0):<31.2f} ║
║  9)  🎰  MTG Settings                                       ║
║  A)  📱  Telegram Channel: {cfg.get('telegram_channel',''):<30} ║
╠══════════════════════════════════════════════════════════════╣
║  0)  🔙  Back                                               ║
╚══════════════════════════════════════════════════════════════╝
""", CYAN))

def print_mtg_menu(mtg: dict):
    banner()
    print(clr(f"""
╔══════════════════════════════════════════════════════════════╗
║               🎰  MARTINGALE SETTINGS                       ║
╠══════════════════════════════════════════════════════════════╣
║  1)  Enable/Disable     : {'✅ ENABLED' if mtg['enabled'] else '❌ DISABLED':<28} ║
║  2)  Multiplier         : {mtg['multiplier']:<32.1f} ║
║  3)  Max Levels         : {mtg['max_levels']:<32} ║
║  4)  Wait Seconds       : {mtg['wait_seconds']:<32} ║
╠══════════════════════════════════════════════════════════════╣
║  0)  🔙  Back                                               ║
╚══════════════════════════════════════════════════════════════╝
""", MAGENTA))

def config_submenu(cfg: dict) -> dict:
    while True:
        print_config_menu(cfg)
        ch = input(clr("  Choice: ", YELLOW)).strip().upper()
        if ch == "0":
            break
        elif ch == "1":
            print("  Domains: global / bd")
            cfg["domain"] = input("  New domain: ").strip() or cfg["domain"]
        elif ch == "2":
            print("  Account: PRACTICE / REAL / TOURNAMENT")
            cfg["account_type"] = input("  New account type: ").strip().upper() or cfg["account_type"]
        elif ch == "3":
            import getpass
            cfg["email"]    = input(f"  Email [{cfg['email']}]: ").strip() or cfg["email"]
            cfg["password"] = getpass.getpass("  Password: ") or cfg["password"]
            cfg["telegram_token"]   = input("  Telegram Token: ").strip() or cfg["telegram_token"]
            cfg["telegram_chat_id"] = input("  Chat ID: ").strip() or cfg["telegram_chat_id"]
        elif ch == "4":
            cfg["signal_style"] = int(input("  Style [1/2]: ").strip() or cfg["signal_style"])
        elif ch == "5":
            cfg["timezone_offset"] = int(input("  UTC Offset (e.g. 6): ").strip() or cfg["timezone_offset"])
        elif ch == "6":
            print("  Modes: SAFE / NORMAL / AGGRESSIVE / ELITE / CUSTOM")
            cfg["mode"] = input("  New mode: ").strip().upper() or cfg["mode"]
        elif ch == "7":
            cfg["target_profit"] = float(input("  Target Profit (0=off): ").strip() or 0)
        elif ch == "8":
            cfg["stop_loss"] = float(input("  Stop Loss (0=off): ").strip() or 0)
        elif ch == "9":
            mtg = load_mtg()
            while True:
                print_mtg_menu(mtg)
                mc = input(clr("  Choice: ", YELLOW)).strip()
                if mc == "0":
                    break
                elif mc == "1":
                    mtg["enabled"] = not mtg["enabled"]
                elif mc == "2":
                    mtg["multiplier"] = float(input("  Multiplier (e.g. 2.0): ").strip() or mtg["multiplier"])
                elif mc == "3":
                    mtg["max_levels"] = int(input("  Max levels (e.g. 3): ").strip() or mtg["max_levels"])
                elif mc == "4":
                    mtg["wait_seconds"] = int(input("  Wait seconds (e.g. 60): ").strip() or mtg["wait_seconds"])
                save_mtg(mtg)
        elif ch == "A":
            cfg["telegram_channel"] = input("  Telegram channel ID: ").strip() or cfg["telegram_channel"]
        save_config(cfg)
    return cfg

def view_last_trades(stats: StatsTracker):
    history = stats.data.get("history", [])[-20:]
    banner()
    print(clr("\n  📋 LAST 20 TRADES\n", CYAN, True))
    divider()
    if not history:
        print("  No trades yet.")
    for t in reversed(history):
        icon  = "✅" if t.get("win") else "❌"
        pl    = f"${t.get('profit', 0):+.2f}"
        print(f"  {icon}  {t.get('time',''):<9}  {t.get('asset',''):<22}  "
              f"{t.get('direction',''):<5}  ${t.get('amount',0):.2f}  {pl}")
    divider()
    input(clr("\n  Press Enter to go back...", WHITE))


# ═════════════════════════════════════════════════════════════
#  MAIN ASYNC ENTRY
# ═════════════════════════════════════════════════════════════

async def main():
    cfg = load_config()

    # First run
    if not cfg.get("email"):
        cfg = first_run_setup(cfg)

    # Load AI engine
    print(clr("\n  🧠 Loading AI models...", CYAN))
    ai = AIEngine(MODELS_DIR)
    loaded = sum([ai.xgb is not None, ai.lgb is not None, ai.cat is not None])
    if loaded:
        print(clr(f"  ✅ {loaded}/3 models loaded from models/", GREEN))
    else:
        print(clr("  ⚠️  No pre-trained models found. Using heuristic signals.", YELLOW))

    # Connect
    print(clr("  🔗 Connecting to Quotex...", CYAN))
    connector = QuotexConnector(cfg)
    connected = await connector.connect()
    if connected:
        print(clr("  ✅ Connected!\n", GREEN))
    else:
        print(clr("  ⚠️  Could not connect. Some features unavailable.\n", YELLOW))

    stats = StatsTracker()
    mtg   = MartingaleManager(cfg.get("trade_amount", 1.0), load_mtg())

    while True:
        print_main_menu(cfg)
        choice = input(clr("  Choice: ", YELLOW)).strip()

        if choice == "1":
            # Start generator
            gen = SignalGenerator(connector, ai, cfg, stats, mtg)
            try:
                await gen.run()
            except KeyboardInterrupt:
                gen.running = False
                print(clr("\n  ⛔ Stopped by user.", RED))

        elif choice == "2":
            bal = await connector.get_balance()
            profile = await connector.get_profile()
            name = profile.get("name", "User") if isinstance(profile, dict) else "User"
            banner()
            divider()
            print(clr(f"\n  👤 Account  : {name}", WHITE))
            print(clr(f"  💳 Type     : {cfg.get('account_type','PRACTICE')}", WHITE))
            print(clr(f"  💰 Balance  : ${bal:.2f}", GREEN, True))
            divider()
            input(clr("\n  Press Enter...", WHITE))

        elif choice == "3":
            banner()
            print(clr("\n  📊 TRADING STATISTICS\n", CYAN, True))
            divider()
            print(stats.summary())
            divider()
            input(clr("\n  Press Enter...", WHITE))

        elif choice == "4":
            sig_test = {
                "asset": "EURUSD",
                "direction": "CALL",
                "confidence": 85.0,
                "regime": "TRENDING",
            }
            gen_tmp = SignalGenerator(connector, ai, cfg, stats, mtg)
            msg = gen_tmp.format_signal(sig_test, cfg.get("signal_style", 1))
            ok  = send_telegram(cfg.get("telegram_token",""), cfg.get("telegram_chat_id",""), msg)
            print(clr(f"\n  {'✅ Test signal sent!' if ok else '❌ Telegram not configured.'}", GREEN if ok else RED))
            time.sleep(2)

        elif choice == "5":
            cfg["ai_learning"] = not cfg.get("ai_learning", True)
            save_config(cfg)
            status = "ON" if cfg["ai_learning"] else "OFF"
            print(clr(f"\n  🧠 AI Learning: {status}", GREEN if cfg["ai_learning"] else RED))
            time.sleep(1.5)

        elif choice == "6":
            view_last_trades(stats)

        elif choice == "7":
            cfg = config_submenu(cfg)
            # reload mtg with new amount
            mtg = MartingaleManager(cfg.get("trade_amount", 1.0), load_mtg())

        elif choice == "0":
            print(clr("\n  👋 Goodbye!\n", CYAN))
            await connector.disconnect()
            break
        else:
            print(clr("  ❓ Invalid choice.", RED))
            time.sleep(1)


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(clr("\n\n  👋 Exited.\n", CYAN))
    except Exception as e:
        print(clr(f"\n  ❌ Fatal error: {e}", RED))
        logger.exception("Fatal error")
        traceback.print_exc()
