import requests
import xbmc
import xbmcaddon
import xbmcgui
import os
import json
import shutil

addon = xbmcaddon.Addon()
smb_username = "kodi" #str(addon.getSetting("smb_username"))
smb_password = "kodi" #str(addon.getSetting("smb_password"))
smb_path = "smb:/192.168.50.1/kodi_data" # str(addon.getSetting("smb_path"))
sync_interval = 10 #(addon.getSetting("sync_interval"))
enable_logging = True #bool(addon.getSetting("enable_logging"))


def log_message(message, level=xbmc.LOGINFO):  # Use LOGINFO instead of LOGNOTICE
    xbmc.log(f"[WatchStatusSync] {message}", level)


import time
import threading

class WatchStatusSync(xbmc.Monitor):
    def __init__(self):
        super().__init__()
        self.running = True
        threading.Thread(target=self.periodic_sync, daemon=True).start()

    def onPlayBackStopped(self):
        self.sync_watched_status()

    def sync_watched_status(self):
        log_message("Syncing watched status...")
        watched_status = self.get_kodi_watched_status()
        self.store_to_smb(watched_status)

    def get_kodi_watched_status(self):
        query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties":["playcount"]}, "id": 1}'
        response = xbmc.executeJSONRPC(query)
        return json.loads(response)

    def store_to_smb(self, data):
        file_path = smb_path + "/" + "watched_status.json"

        # Read the JSON file
        response = requests.get(file_path, auth=(smb_username, smb_password))
        if response.status_code == 200:
            data = response.json()
            print("Loaded JSON:", data)
        else:
            print("Error loading JSON:", response.status_code)



    def load_updates(self):
        log_message("Loading watched status...")
        file_path = smb_path + "/" + "watched_status.json"

        # Read the JSON file
        response = requests.get(file_path, auth=(smb_username, smb_password))
        if response.status_code == 200:
            updated_status = response.json()
            print("Loaded JSON:", updated_status)
        else:
            print("Error loading JSON:", response.status_code)
        self.apply_updates(updated_status)

    def apply_updates(self, data):
        # Logic to update Kodi's local watched status based on SMB data
        pass

    def periodic_sync(self):
        while self.running:
            try:
                log_message("Performing scheduled watched status sync...")
                self.sync_watched_status()
                time.sleep(sync_interval*60)  # Wait for sync_interval minutes before next sync
            except Exception as e:
                log_message(f"{e}")
                log_message("stop running")
                self.running = False

watch_sync = WatchStatusSync()
