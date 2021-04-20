from Resources.AppResourceManager import AppResourceManager
import Foundation


# Thanks to this post:
# https://gist.github.com/codiez/260617/b0022ce6413fe016f146beb515ae90d49fbfcd21


class AppleMusicHandler(object):
    def __init__(self, command):
        self.command = command
        self.app_resource_manager = AppResourceManager()
        nc = Foundation.NSDistributedNotificationCenter.defaultCenter()
        nc.addObserver_selector_name_object_(self, 'get_current_song:', 'com.apple.Music.playerInfo', None)

    def get_current_song_(self, song):
        try:
            song_details = {}
            ui = song.userInfo()
            for x in ui:
                song_details[x] = ui.objectForKey_(x)
            if song_details.get("Player State") == "Playing":
                details = song_details.get("Name")
            else:
                details = f"{self.app_resource_manager.get_string('paused')} - {song_details.get('Name')}"
            state = song_details.get("Artist")
            song_duration = float(song_details.get("Total Time") / 1000)
        except:
            details = self.app_resource_manager.get_string("unknown")
            state = self.app_resource_manager.get_string("unknown")
            song_duration = float(0)

        self.command(details, state, song_duration)
