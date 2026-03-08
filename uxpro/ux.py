# UX-CORE-SYSTEM-LOADER [Build 7.0.5.0]
import os, sys, time, hashlib, hmac
import platform, subprocess, uuid
import json, base64, requests
from cryptography.fernet import Fernet

LICENSE_CACHE = ".license_cache"

API_URL    = "https://uxpro-license-server-v2-1.onrender.com"
API_SECRET = "uxpro_9xK2mP_s3cur3_2025"

# ── Load .env for local core decrypt support ─────────────────
def _load_env():
    env = {}
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except Exception:
        pass
    return env

_ENV = _load_env()
MASTER_KEY = _ENV.get("MASTER_KEY", "")
CORE_PATH  = _ENV.get("CORE_PATH", "ux.py.core")


class LoaderSecurity:
    def __init__(self):
        self.device_id = self._get_device_id()
        self.cache_key = base64.urlsafe_b64encode(
            hashlib.sha256(self.device_id.encode()).digest()
        )

    def _get_device_id(self):
        factors = [str(uuid.getnode()), platform.node(), platform.processor(), platform.machine()]
        try:
            if platform.system() == "Linux":
                if os.path.exists("/etc/machine-id"):
                    factors.append(open("/etc/machine-id").read().strip())
                elif os.path.exists("/var/lib/dbus/machine-id"):
                    factors.append(open("/var/lib/dbus/machine-id").read().strip())
            elif platform.system() == "Windows":
                try:
                    s = subprocess.check_output("wmic bios get serialnumber",shell=True).decode().split("\n")[1].strip()
                    factors.append(s)
                    u = subprocess.check_output("wmic csproduct get uuid",shell=True).decode().split("\n")[1].strip()
                    factors.append(u)
                except: pass
        except: pass
        return hashlib.sha256("|".join(factors).encode()).hexdigest()

    def _make_sig(self, license_key):
        msg = f"{license_key}:{self.device_id}"
        return hmac.new(API_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()

    def save_cache(self, license_key):
        try:
            f = Fernet(self.cache_key)
            data = json.dumps({"key": license_key, "ts": time.time()}).encode()
            with open(LICENSE_CACHE, "wb") as file:
                file.write(f.encrypt(data))
        except: pass

    def load_cache(self):
        if not os.path.exists(LICENSE_CACHE): return None
        try:
            f = Fernet(self.cache_key)
            with open(LICENSE_CACHE, "rb") as file:
                enc = file.read()
            data = json.loads(f.decrypt(enc).decode())
            if time.time() - data.get("ts", 0) > 43200:
                return None
            return data.get("key")
        except: return None

    def verify_and_fetch(self, license_key):
        try:
            r1 = requests.post(f"{API_URL}/verify", json={
                "license_key": license_key,
                "device_id":   self.device_id,
                "sig":         self._make_sig(license_key)
            }, timeout=15)
            d1 = r1.json()

            if not d1.get("valid"):
                msgs = {
                    "not_found":         "\n❌ Invalid License Key",
                    "inactive":          "\n❌ License is not active",
                    "expired":           "\n❌ License Expired — contact @U9KNOWN_X",
                    "revoked":           "\n❌ License Revoked — contact @U9KNOWN_X",
                    "device_mismatch":   "\n❌ Device mismatch — contact @U9KNOWN_X",
                    "invalid_signature": "\n❌ Request tampered",
                    "rate_limited":      "\n❌ Too many requests — try again tomorrow",
                }
                print(msgs.get(d1.get("reason",""), f"\n❌ Auth failed: {d1.get('reason')}"))
                return None

            session_token = d1.get("session_token")
            session_key   = base64.b64decode(d1.get("session_key",""))

            r2 = requests.post(f"{API_URL}/fetch_core", json={
                "session_token": session_token,
                "device_id":     self.device_id,
            }, timeout=30)
            d2 = r2.json()

            if "core" not in d2:
                print(f"\n❌ Core fetch failed: {d2.get('error','unknown')}")
                return None

            enc_bytes = base64.b64decode(d2["core"])
            code = bytes(b ^ session_key[i % len(session_key)] for i, b in enumerate(enc_bytes))
            return code

        except requests.exceptions.ConnectionError:
            print("\n❌ No internet connection")
            return None
        except requests.exceptions.Timeout:
            print("\n❌ Server timeout — try again")
            return None
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return None

    def self_destruct(self):
        print("\n[!] CRITICAL ERROR. WIPING...")
        root = os.path.dirname(os.path.abspath(__file__))
        for r, d, files in os.walk(root, topdown=False):
            for f in files:
                try:
                    p = os.path.join(r, f)
                    with open(p, "wb") as file:
                        file.write(os.urandom(os.path.getsize(p)))
                    os.remove(p)
                except: pass
        sys.exit(1)


# ── LOCAL CORE DECRYPT (no server / no internet needed) ──────
def decrypt_local_core():
    """Decrypt ux.py.core using MASTER_KEY from .env and return code bytes."""
    if not MASTER_KEY:
        print("\n❌ MASTER_KEY not found in .env — cannot use local decrypt")
        return None
    core_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), CORE_PATH)
    if not os.path.exists(core_file):
        print(f"\n❌ Core file not found: {core_file}")
        return None
    try:
        f = Fernet(MASTER_KEY.encode())
        with open(core_file, "rb") as fp:
            enc_data = fp.read().strip()
        # Core is stored as base64(fernet(code))
        raw = base64.b64decode(enc_data)
        code = f.decrypt(raw)
        return code
    except Exception as e:
        print(f"\n❌ Local core decrypt failed: {e}")
        return None


def main():
    print("\n⚡ UX PRO VIP V7 — ULTRA SECURE LOADER")
    print("---------------------------------------")
    print("  [1] 🌐 Online Launch  (License Key + Server)")
    print("  [2] 🔓 Local Launch   (Decrypt Core Offline)")
    print("---------------------------------------")

    mode = input("  Select [1/2] (Enter = 1): ").strip()

    ls = LoaderSecurity()

    if mode == "2":
        # ── LOCAL CORE DECRYPT MODE ──
        print("\n🔓 Local Core Decrypt — Authenticating offline...")
        code = decrypt_local_core()
        if not code:
            sys.exit(1)
        print("✅ Core Decrypted Locally. Launching...\n")
        time.sleep(0.5)
        try:
            exec(compile(code, "<uxpro>", "exec"), globals())
        except Exception as e:
            print(f"Launch Failed: {e}")
            sys.exit(1)

    else:
        # ── ONLINE LICENSE MODE (default) ──
        global l_key
        l_key = ls.load_cache()

        if not l_key:
            l_key = input("🔑 License Key: ").strip().upper()

        print("🔍 Authenticating...")
        code = ls.verify_and_fetch(l_key)

        if not code:
            if os.path.exists(LICENSE_CACHE):
                os.remove(LICENSE_CACHE)
            sys.exit(1)

        ls.save_cache(l_key)

        try:
            print("✅ Core Unlocked. Launching...\n")
            time.sleep(0.5)
            exec(compile(code, "<uxpro>", "exec"), globals())
        except Exception as e:
            print(f"Launch Failed: {e}")
            ls.self_destruct()


if __name__ == "__main__":
    main()
