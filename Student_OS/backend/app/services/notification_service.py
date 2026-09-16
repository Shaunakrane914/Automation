import subprocess
import logging

logger = logging.getLogger("notification_service")

def send_windows_notification(title: str, message: str) -> bool:
    """
    Dispatches a native Windows system notification without blocking.
    """
    try:
        clean_title = title.replace("'", " ").replace('"', ' ')
        clean_msg = message.replace("'", " ").replace('"', ' ')
        ps_cmd = f"""
        [void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::Information
        $notify.BalloonTipTitle = '{clean_title}'
        $notify.BalloonTipText = '{clean_msg}'
        $notify.Visible = $True
        $notify.ShowBalloonTip(4000)
        Start-Sleep -Seconds 1
        $notify.Dispose()
        """
        subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd])
        return True
    except Exception as e:
        logger.warning(f"Could not send notification: {e}")
        return False
