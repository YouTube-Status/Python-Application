# -*- coding: utf-8 -*-
# referred to https://developer.mozilla.org/ja/docs/Mozilla/Add-ons/WebExtensions/Native_messaging
import sys
import ast
import os
from os import path
import configparser
import logging

directory_path = path.expandvars("%APPDATA%/approvers/youtube_status")
config_file_path = path.expandvars("%APPDATA%/approvers/youtube_status/status.ini")

log_format = logging.Formatter("[%(asctime)s]%(name)s: %(message)s")

error_log = logging.getLogger("ERROR")
error_log.setLevel(logging.WARNING)
error_handler = logging.FileHandler("log/error.log")
error_handler.setFormatter(log_format)
error_log.addHandler(error_handler)

info_log = logging.getLogger("INFO")
info_log.setLevel(logging.DEBUG)
info_handler = logging.FileHandler("log/communication.log")
info_handler.setFormatter(log_format)
info_log.addHandler(info_handler)

def read_config():
    os.makedirs(directory_path, exist_ok=True)
    
    config_ini = configparser.ConfigParser()
    if path.exists(config_file_path):
        config_ini.read(config_file_path)
        return config_ini

    if path.exists(directory_path):
        write_config("null", False, 0, False, "null", "null", new=True)

        config_ini = configparser.ConfigParser()
        config_ini.read(config_file_path)
        return config_ini

    return False

def write_config(token, active, multi, active_tab, title, url, log_data=False, new=False):
    try:
        token = str(token)
        active = str(active).lower()
        multi = int(multi)
        active_tab = str(active_tab).lower()
        title = str(title).replace("%", "%%")
        url = str(url).replace("%", "%%")
    except Exception as e:
        error_log.error(e)
        return

    if not path.exists(directory_path):
        return

    if not new:
        status_ini = read_config()
        if status_ini:
            status_token = status_ini["YouTube_Status"]["token"]
            status_active = status_ini["YouTube_Status"]["active"]
            status_multi = int(status_ini["YouTube_Status"]["multi"])
            status_active_tab = status_ini["YouTube_Status"]["active_tab"]
            status_title = str(status_ini["YouTube_Status"]["title"]).replace("%", "%%")
            status_url = str(status_ini["YouTube_Status"]["url"]).replace("%", "%%")
        else:
            status_token = "null"
            status_active = "false"
            status_multi = 0
            status_active_tab = "false"
            status_title = "null"
            status_url = "null"

        if token == status_token and active == status_active and multi == status_multi and active_tab == status_active_tab and title == status_title and url == status_url:
            return

    config_ini = configparser.ConfigParser()
    config_ini["YouTube_Status"] = {
            "token": token,
            "active": active,
            "multi": multi,
            "active_tab": active_tab,
            "title": title,
            "url": url
        }

    if log_data:
        info_log.info(log_data)

    try:
        with open(config_file_path, "w") as f:
            config_ini.write(f)
    except Exception as e:
        error_log.error(e)
        return

def process_message(message):
    try:
        message_dict = ast.literal_eval(message)
    except Exception as e:
        error_log.error(e)
        return

    try:
        token = message_dict["token"]
        type = message_dict["type"]
    except Exception as e:
        error_log.error(e)
        return

    status_ini = read_config()
    if status_ini:
        status_token = status_ini["YouTube_Status"]["token"]
        status_active = status_ini["YouTube_Status"]["active"]
    else:
        status_token = None
        status_active = False

    if type == "status":
        try:
            active = message_dict["active"]
            multi = message_dict["multi"]
            active_tab = message_dict["active_tab"]
            title = message_dict["title"]
            url = message_dict["url"]
        except Exception as e:
            error_log.error(e)
            return

        if active:
            if active_tab:
                write_config(token, active, multi, active_tab, title, url, log_data=message)
            else:
                if status_active == "false":
                    write_config(token, active, multi, active_tab, title, url, log_data=message)
                elif status_token == token:
                    write_config(token, active, multi, active_tab, title, url, log_data=message)
        else:
            if status_token == token:
                write_config("null", False, 0, False, "null", "null", log_data=message)

    elif str(type).startswith("disconnect"):
        if status_token == token:
            write_config("null", False, 0, False, "null", "null", log_data=message)
        
        if type == "disconnect_all":
            sys.exit()