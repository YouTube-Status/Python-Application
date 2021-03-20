# -*- coding: utf-8 -*-
# referred to https://developer.mozilla.org/ja/docs/Mozilla/Add-ons/WebExtensions/Native_messaging
import json
import sys
import struct
from os import path
import logging
from process import process_message

directory_path = path.expandvars("%APPDATA%/approvers/youtube_status")

log_format = logging.Formatter("[%(asctime)s]%(name)s: %(message)s")
error_log = logging.getLogger("ERROR")
error_log.setLevel(logging.WARNING)
error_handler = logging.FileHandler("log/error.log")
error_handler.setFormatter(log_format)
error_log.addHandler(error_handler)

def directory():
    if path.exists(directory_path):
        send_message(encode_message("200"))
    else:
        send_message(encode_message("404"))

def get_message():
    raw_length = sys.stdin.buffer.read(4)

    if not raw_length:
        sys.exit(0)
    message_length = struct.unpack("=I", raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)

def encode_message(message_content):
    encoded_content = json.dumps(message_content).encode("utf-8")
    encoded_length = struct.pack("=I", len(encoded_content))
    return {"length": encoded_length, "content": struct.pack(str(len(encoded_content))+"s",encoded_content)}

def send_message(encoded_message):
    sys.stdout.buffer.write(encoded_message["length"])
    sys.stdout.buffer.write(encoded_message["content"])
    sys.stdout.buffer.flush()

def run():
    try:
        while True:
            directory()
            message = get_message()
            process_message(message)
    except Exception as e:
        error_log.error(e)
        return