import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "email_address": "",
    "email_provider": "smtp",
    "email_smtp_server": "smtp.gmail.com",
    "email_smtp_port": 587,
    "email_username": "",
    "email_password": "",
    "sendgrid_api_key": "",
    "check_interval_minutes": 1,
    "whatsapp_enabled": False,
    "whatsapp_number": "",
    "whatsapp_provider": "twilio",
    "twilio_account_sid": "",
    "twilio_auth_token": "",
    "twilio_whatsapp_number": ""
}


def load_config():
    merged = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            merged.update(data)
    # Override with environment variables (for Render / Docker)
    env_map = {
        "email_address": "SMTP_EMAIL",
        "email_provider": "EMAIL_PROVIDER",
        "email_smtp_server": "SMTP_SERVER",
        "email_smtp_port": "SMTP_PORT",
        "email_username": "SMTP_USERNAME",
        "email_password": "SMTP_PASSWORD",
        "sendgrid_api_key": "SENDGRID_API_KEY",
        "check_interval_minutes": "CHECK_INTERVAL",
    }
    for cfg_key, env_var in env_map.items():
        val = os.environ.get(env_var)
        if val is not None:
            if cfg_key in ("email_smtp_port", "check_interval_minutes"):
                try:
                    merged[cfg_key] = int(val)
                except ValueError:
                    pass
            else:
                merged[cfg_key] = val
    return merged


def save_config(**kwargs):
    config = load_config()
    valid_keys = DEFAULT_CONFIG.keys()
    for key, val in kwargs.items():
        if key in valid_keys:
            if isinstance(val, str):
                val = val.strip()
            config[key] = val
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def is_configured():
    cfg = load_config()
    if not cfg.get("email_address"):
        return False
    provider = cfg.get("email_provider", "smtp")
    if provider == "sendgrid":
        return bool(cfg.get("sendgrid_api_key"))
    return bool(cfg.get("email_password"))


def get_whatsapp_config():
    cfg = load_config()
    return {
        "enabled": cfg.get("whatsapp_enabled", False),
        "number": cfg.get("whatsapp_number", ""),
        "provider": cfg.get("whatsapp_provider", "twilio"),
        "account_sid": cfg.get("twilio_account_sid", ""),
        "auth_token": cfg.get("twilio_auth_token", ""),
        "from_number": cfg.get("twilio_whatsapp_number", "")
    }
