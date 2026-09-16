import httpx
import logging
from typing import Optional
from app.config import settings
from app.database import log_agent_event

logger = logging.getLogger("notifications")

async def send_ntfy_notification(title: str, message: str, priority: str = "default", tags: Optional[str] = None):
    """
    Sends push notification via ntfy.sh (No signup or phone number required).
    """
    if not settings.NTFY_TOPIC:
        return False

    url = f"https://ntfy.sh/{settings.NTFY_TOPIC}"
    headers = {
        "Title": title,
        "Priority": priority,
    }
    if tags:
        headers["Tags"] = tags

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, content=message.encode("utf-8"), headers=headers)
            if resp.status_code == 200:
                log_agent_event("INFO", f"Push notification dispatched via ntfy.sh: {title}")
                return True
            else:
                logger.error(f"ntfy.sh failed with status {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        logger.error(f"Failed to send ntfy notification: {e}")
        return False

async def send_telegram_notification(message: str):
    """
    Sends message via Telegram Bot API if configured.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                log_agent_event("INFO", f"Telegram alert dispatched: {message[:50]}...")
                return True
    except Exception as e:
        logger.error(f"Failed to send telegram notification: {e}")
    return False

async def dispatch_alert(title: str, message: str, priority: str = "default", tags: str = "bell") -> bool:
    """
    Unified dispatcher to all active mobile channels.
    """
    n_res = await send_ntfy_notification(title=title, message=message, priority=priority, tags=tags)
    t_res = await send_telegram_notification(f"*{title}*\n{message}")
    return bool(n_res or t_res)
