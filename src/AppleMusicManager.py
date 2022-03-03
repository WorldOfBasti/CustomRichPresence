from threading import Thread
from osascript import osascript
from Foundation import NSDistributedNotificationCenter
from Foundation import NSRunLoop


# Thanks to this post:
# https://gist.github.com/codiez/260617/b0022ce6413fe016f146beb515ae90d49fbfcd21


class AppleMusicManager(object):
    def __init__(self, app_resource_manager, command):
        self.app_resource_manager = app_resource_manager
        self.command = command
        self.stop_thread = False

    # Start Apple Music synchronization
    def start_syncing(self):
        notification_thread = Thread(target=self.notification)
        notification_thread.start()

        # Update RPC for first time
        self.update_status_(None)

    # Stop Apple Music synchronization
    def stop_syncing(self):
        self.stop_thread = True

    # Apple Music song was changed
    def update_status_(self, _):
        # Get data via apple script
        try:
            if osascript("tell application \"Music\" to get player state as string")[1] == "playing":
                details = osascript("tell application \"Music\" to get name of current track as string")[1]
            else:
                details = self.app_resource_manager.get_string('paused') + " - " + osascript("tell application \"Music\" to get name of current track as string")[1]

            state = osascript("tell application \"Music\" to get artist of current track as string")[1]
            song_duration = float(osascript("tell application \"Music\" to get duration of current track as string")[1].replace(',', '.')) - float(osascript("tell application \"Music\" to get player position as string")[1].replace(',', '.'))
        except:
            details = self.app_resource_manager.get_string("unknown")
            state = self.app_resource_manager.get_string("unknown")
            song_duration = float(0)

        # Update RPC
        self.command(details, state, song_duration)

    # Notify, if Apple Music song gets changed
    def notification(self):
        nc = NSDistributedNotificationCenter.defaultCenter()
        nc.addObserver_selector_name_object_(self, 'update_status:', 'com.apple.Music.playerInfo', None)
        while True:
            if self.stop_thread:
                self.stop_thread = False
                break
            loop = NSRunLoop.currentRunLoop()
            loop.run()
