"""
Global Internet Tunnel Manager for Student OS & Antigravity Workstation.
Enables peer-to-peer / remote access from mobile devices anywhere in the world
over cellular data (4G/5G) or remote Wi-Fi via Cloudflare Secure Tunnels.
"""

import os
import re
import json
import time
import urllib.request
import logging
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("global_tunnel")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
BIN_DIR = BACKEND_DIR / "bin"
DATA_DIR = BACKEND_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
BIN_DIR.mkdir(parents=True, exist_ok=True)

TUNNEL_INFO_FILE = DATA_DIR / "global_tunnel_info.json"
CLOUDFLARED_EXE = BIN_DIR / "cloudflared.exe"

# Unique Cloud Discovery Channel for Shaunak's Workstation
# Allows the mobile app to automatically discover the active public URL from anywhere in the world.
DISCOVERY_TOPIC = "shaunak_studentos_global_url_88f9a2"
DISCOVERY_PUB_URL = f"https://ntfy.sh/{DISCOVERY_TOPIC}"

class GlobalTunnelManager:
    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._public_url: Optional[str] = None
        self._started_at: Optional[str] = None
        self._status = "stopped"
        self._custom_url: Optional[str] = None
        self._last_error: Optional[str] = None
        self._reconnect_count = 0
        self._load_cached_info()

    def _load_cached_info(self):
        if TUNNEL_INFO_FILE.exists():
            try:
                with open(TUNNEL_INFO_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._custom_url = data.get("custom_url")
                    self._public_url = data.get("public_url")
            except Exception as e:
                logger.debug(f"Could not load cached tunnel info: {e}")

    def _save_info(self):
        try:
            info = {
                "public_url": self._public_url,
                "custom_url": self._custom_url,
                "status": self._status,
                "started_at": self._started_at,
                "discovery_topic": DISCOVERY_TOPIC,
                "discovery_url": f"https://ntfy.sh/{DISCOVERY_TOPIC}/raw?poll=1",
                "last_updated": datetime.now().isoformat()
            }
            with open(TUNNEL_INFO_FILE, "w", encoding="utf-8") as f:
                json.dump(info, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save tunnel info: {e}")

    def _publish_to_cloud_discovery(self, url: str):
        """
        Publishes the active public URL to the secure cloud registry channel
        so the mobile app can discover the live workstation URL on cellular data.
        """
        try:
            payload = json.dumps({
                "url": url,
                "workstation": "Shaunak Laptop (Automation)",
                "timestamp": datetime.now().isoformat(),
                "port": 8000,
                "type": "cloudflare_quick_tunnel"
            }).encode("utf-8")

            req = urllib.request.Request(
                DISCOVERY_PUB_URL,
                data=payload,
                headers={
                    "Title": "Student OS Workstation Online",
                    "Tags": "laptop,rocket",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status in (200, 201):
                    logger.info(f"Published global tunnel URL to cloud registry: {url}")
        except Exception as e:
            logger.warning(f"Cloud discovery publication note: {e}")

    def start_tunnel(self, local_port: int = 8000) -> Dict[str, Any]:
        """
        Starts the Cloudflare Quick Tunnel daemon in a background supervisor thread.
        """
        if self._running and self._process and self._process.poll() is None:
            return self.get_status()

        if not CLOUDFLARED_EXE.exists():
            self._status = "error"
            self._last_error = "cloudflared.exe binary not found in backend/bin"
            return self.get_status()

        self._running = True
        self._status = "starting"
        self._last_error = None
        self._started_at = datetime.now().isoformat()

        self._thread = threading.Thread(target=self._run_supervisor, args=(local_port,), daemon=True)
        self._thread.start()

        # Wait up to 8 seconds for the public URL to be established
        t0 = time.time()
        while time.time() - t0 < 8:
            if self._public_url:
                break
            time.sleep(0.3)

        return self.get_status()

    def _run_supervisor(self, local_port: int):
        while self._running:
            try:
                cmd = [
                    str(CLOUDFLARED_EXE),
                    "tunnel",
                    "--url", f"http://127.0.0.1:{local_port}",
                    "--no-autoupdate"
                ]
                logger.info(f"Launching Cloudflare Global Tunnel targeting port {local_port}...")
                
                # Use CREATE_NO_WINDOW on Windows
                creationflags = 0x08000000 if os.name == "nt" else 0

                self._process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    creationflags=creationflags
                )

                found_url = False
                for line in self._process.stderr:
                    line_clean = line.strip()
                    logger.debug(f"[cloudflared] {line_clean}")
                    
                    if not found_url:
                        # Match https://*.trycloudflare.com
                        m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line_clean)
                        if m:
                            self._public_url = m.group(0)
                            self._status = "online"
                            found_url = True
                            logger.info(f"🌐 Global Internet Tunnel Active: {self._public_url}")
                            self._save_info()
                            # Publish to cloud discovery
                            threading.Thread(target=self._publish_to_cloud_discovery, args=(self._public_url,), daemon=True).start()

                # Process exited
                exit_code = self._process.wait()
                if self._running:
                    self._reconnect_count += 1
                    logger.warning(f"Cloudflare tunnel process ended (code {exit_code}). Reconnecting in 3s...")
                    time.sleep(3)

            except Exception as e:
                self._last_error = str(e)
                self._status = "error"
                logger.error(f"Error in global tunnel supervisor: {e}")
                if self._running:
                    time.sleep(5)

    def stop_tunnel(self) -> Dict[str, Any]:
        """
        Stops the active global tunnel.
        """
        self._running = False
        if self._process:
            try:
                self._process.terminate()
                self._process.kill()
            except Exception:
                pass
            self._process = None

        self._status = "stopped"
        self._public_url = None
        self._save_info()
        logger.info("Global internet tunnel stopped.")
        return self.get_status()

    def set_custom_url(self, url: str) -> Dict[str, Any]:
        """
        Saves a custom global URL (such as a custom domain or Tailscale / Ngrok URL).
        """
        self._custom_url = url.strip() if url else None
        self._save_info()
        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        """
        Returns full diagnostic status of the global internet tunnel.
        """
        effective_url = self._custom_url or self._public_url
        return {
            "status": self._status,
            "running": self._running and bool(self._public_url),
            "public_url": self._public_url,
            "custom_url": self._custom_url,
            "effective_url": effective_url,
            "provider": "Cloudflare Quick Tunnel (Free & Global)",
            "started_at": self._started_at,
            "discovery_topic": DISCOVERY_TOPIC,
            "discovery_url": f"https://ntfy.sh/{DISCOVERY_TOPIC}/raw",
            "last_error": self._last_error,
            "reconnect_count": self._reconnect_count,
            "features": [
                "Zero Port-Forwarding Needed",
                "Works Worldwide across Cellular 4G/5G & Any Wi-Fi",
                "SSL Encrypted (HTTPS/WSS)",
                "Automatic Cloud Relay Auto-Discovery"
            ]
        }

# Global Singleton Instance
global_tunnel_manager = GlobalTunnelManager()
