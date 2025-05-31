import xbmc
import xbmcaddon
import xbmcgui
import os
import json
import shutil


addon = xbmcaddon.Addon()
smb_path = addon.getSetting("smb_path")
smb_username = addon.getSetting("smb_username")
smb_password = addon.getSetting("smb_password")

def log_message(message, level=xbmc.LOGNOTICE):
    xbmc.log(f"[WatchStatusSync] {message}", level)



class WatchStatusSync(xbmc.Monitor):
    def __init__(self):
        super().__init__()

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
        file_path = os.path.join(smb_path, "watched_status.json")
        with open(file_path, "w") as f:
            json.dump(data, f)

    def load_updates(self):
        log_message("Loading watched status...")
        file_path = os.path.join(smb_path, "watched_status.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                updated_status = json.load(f)
            self.apply_updates(updated_status)

    def apply_updates(self, data):
        # Logic to update Kodi's local watched status based on SMB data
        pass

watch_sync = WatchStatusSync()
