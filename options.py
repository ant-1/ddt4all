#!/usr/bin/python3
# -*- coding: utf-8 -*-
import gettext
import json
import locale
import os

simulation_mode = False
port_speed = 38400
port_name = ""
port = ""
promode = False
elm = None
log = "ddt"
opt_cfc0 = False
opt_n1c = True
log_all = False
auto_refresh = False
elm_failed = False
# KWP2000 Slow init
opt_si = False
report_data = True
dark_mode = False
ecus_dir = "ecus/"
graphics_dir = "graphics/"
last_error = ""
main_window = None
ecu_scanner = None
debug = 'DDTDEBUG' in os.environ
cantimeout = 0
refreshrate = 5
mode_edit = False
safe_commands = ["3E", "14", "21", "22", "17", "19", "10"]
configuration = {
    "lang": None,
    "dark": False,
    "socket_timeout": False,
    "device_settings": {},
    "auto_detect_devices": True,
    "connection_timeout": 10,
    "read_timeout": 5,
    "max_reconnect_attempts": 3,
    "preferred_device_order": ["vlinker", "vgate", "obdlink", "obdlink_ex", "elm327", "els27"],
    "enable_device_validation": True
}
lang_list = {
    "English": "en_US",
    "German": "de",
    "Spanish": "es",
    "French": "fr",
    "Hungarian": "hu",
    "Italian": "it",
    "Dutch": "nl",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Serbian": "sr",
    "Turkish": "tr",
    "Ukrainian": "uk_UA"
}


def save_config():
    # print(f'Save ddt4all_data/config.json lang: {configuration["lang"]} -> Ok.')
    js = json.dumps(configuration, ensure_ascii=False, indent=True)
    f = open("ddt4all_data/config.json", "w", encoding="UTF-8")
    f.write(js)
    f.close()


def create_new_config():
    configuration["lang"] = get_translator_lang()
    configuration["dark"] = False
    configuration["socket_timeout"] = False
    configuration["device_settings"] = {}
    configuration["auto_detect_devices"] = True
    configuration["connection_timeout"] = 10
    configuration["read_timeout"] = 5
    configuration["max_reconnect_attempts"] = 3
    configuration["preferred_device_order"] = ["vlinker", "vgate", "obdlink", "obdlink_ex", "els27", "elm327"]
    configuration["enable_device_validation"] = True
    save_config()


def load_configuration():
    try:
        f = open("ddt4all_data/config.json", "r", encoding="UTF-8")
        config = json.loads(f.read())
        # load config as multiplatform (mac fix macOs load conf)
        lang_value = config.get("lang", get_translator_lang())
        # Handle null/None values properly
        configuration["lang"] = lang_value if lang_value is not None else get_translator_lang()
        configuration["dark"] = config.get("dark", False)
        configuration["socket_timeout"] = config.get("socket_timeout", False)
        
        # Load enhanced device settings with defaults
        configuration["device_settings"] = config.get("device_settings", {})
        configuration["auto_detect_devices"] = config.get("auto_detect_devices", True)
        configuration["connection_timeout"] = config.get("connection_timeout", 10)
        configuration["read_timeout"] = config.get("read_timeout", 5)
        configuration["max_reconnect_attempts"] = config.get("max_reconnect_attempts", 3)
        configuration["preferred_device_order"] = config.get("preferred_device_order", 
                                                           ["vlinker", "vgate", "obdlink", "obdlink_ex", "els27", "elm327"])
        configuration["enable_device_validation"] = config.get("enable_device_validation", True)
        
        # Ensure LANG environment variable is set to a valid string
        if configuration["lang"] is not None:
            os.environ['LANG'] = configuration["lang"]
        else:
            os.environ['LANG'] = get_translator_lang()
        f.close()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        create_new_config()


def get_last_error():
    global last_error
    err = last_error
    last_error = ""
    return err


def get_translator_lang():
    # default translation if err set to en_US
    loc_lang = "en_US"
    try:
        lang, enc = locale.getdefaultlocale()
        if lang is not None:
            loc_lang = lang
    except:
        try:
            lang, enc = locale.getlocale()
            if lang is not None:
                loc_lang = lang
        except:
            pass
    
    # Ensure we never return None
    if loc_lang is None:
        loc_lang = "en_US"
    
    return loc_lang


def get_device_settings(device_type, port=None):
    """Get device-specific settings with fallback to defaults"""
    device_key = f"{device_type}_{port}" if port else device_type
    
    # Default settings by device type
    defaults = {
        'vlinker': {'baudrate': 38400, 'timeout': 3, 'rtscts': False, 'dsrdtr': False},
        'elm327': {'baudrate': 38400, 'timeout': 5, 'rtscts': False, 'dsrdtr': False},
        'obdlink': {'baudrate': 115200, 'timeout': 2, 'rtscts': True, 'dsrdtr': False},
        'obdlink_ex': {'baudrate': 115200, 'timeout': 2, 'rtscts': True, 'dsrdtr': False},
        'els27': {'baudrate': 38400, 'timeout': 4, 'rtscts': False, 'dsrdtr': False, 'can_pins': '12-13'},  # ELS27 V5 with CAN on pins 12-13
        'vgate': {'baudrate': 115200, 'timeout': 2, 'rtscts': False, 'dsrdtr': False},

        'unknown': {'baudrate': 38400, 'timeout': 5, 'rtscts': False, 'dsrdtr': False}
    }
    
    # Get saved settings or use defaults
    saved_settings = configuration.get("device_settings", {}).get(device_key, {})
    default_settings = defaults.get(device_type, defaults['unknown'])
    
    # Merge saved settings with defaults
    settings = default_settings.copy()
    settings.update(saved_settings)
    
    return settings


def save_device_settings(device_type, settings, port=None):
    """Save device-specific settings"""
    device_key = f"{device_type}_{port}" if port else device_type
    
    if "device_settings" not in configuration:
        configuration["device_settings"] = {}
    
    configuration["device_settings"][device_key] = settings
    save_config()


def get_connection_timeout():
    """Get connection timeout from configuration"""
    return configuration.get("connection_timeout", 10)


def get_read_timeout():
    """Get read timeout from configuration"""
    return configuration.get("read_timeout", 5)


def get_max_reconnect_attempts():
    """Get maximum reconnection attempts"""
    return configuration.get("max_reconnect_attempts", 3)


def is_device_validation_enabled():
    """Check if device validation is enabled"""
    return configuration.get("enable_device_validation", True)


def get_preferred_device_order():
    """Get preferred device detection order"""
    return configuration.get("preferred_device_order", ["vlinker", "vgate", "obdlink", "obdlink_ex", "els27", "elm327"])


def translator(domain):
    load_configuration()
    # Set up message catalog access
    t = gettext.translation(domain, 'ddt4all_data/locale', fallback=True)  # not ok in python 3.11.x, codeset="utf-8")
    return t.gettext
