import xbmc
from resources.lib.gui import do_initial_wizard, do_changelog_display, do_ssdp_discovery, notify_user
from resources.lib.connection import Connection
from resources.lib.utils import *


class XBMCPlayer(xbmc.Player):
    """ xbmc player class """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._player_paused = False
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer.notify(self, *args, **kwargs)

    def notify(self):
        self.notify_observers("updateState")

    @property
    def paused(self) -> bool:
        return self._player_paused

    def onPlayBackPaused(self):
        self._player_paused = True
        self.notify()

    def onPlayBackResumed(self):
        self._player_paused = False
        self.notify()

    def onPlayBackStarted(self):
        self.notify()

    def onPlayBackStopped(self):
        self._player_paused = False
        self.notify()

    def onPlayBackEnded(self):
        self.notify()

class XBMCMonitor(xbmc.Monitor):
    """ xbmc monitor class """
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._screensaver_active = False
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer.notify(self, *args, **kwargs)

    def onSettingsChanged(self):
        self.notify_observers("updateSettings")

    def is_screensaver_active(self):
        return self._screensaver_active

    def onScreensaverActivated(self):
        self._screensaver_active = True
        self.notify_observers("updateState")

    def onScreensaverDeactivated(self):
        self._screensaver_active = False
        self.notify_observers("updateState")

class Hyperion:
    """ Main instance class """
    def __init__(self, player: XBMCPlayer, monitor: XBMCMonitor) -> None:
        self.prev_video_mode = "2D"
        self.prev_comp_state = None
        self.initialized = False

        self.player = player
        self.player.register_observer(self)
        self.monitor = monitor
        self.monitor.register_observer(self)
        self.connection = Connection()

        self.update_settings()

    def notify(self, observable, *args, **kwargs):
        if "updateState" in args:
            self.update_state()
        else:
            self.update_settings()

    def initialize(self):
        # check for changelog display, but not on first run
        if get_bool_setting('showChangelogOnUpdate') and not get_bool_setting('firstRun'):
            do_changelog_display()

        # check for setup wizard
        if get_bool_setting('firstRun'):
            # be sure to fill in the current version
            update_saved_addon_version()
            do_initial_wizard()
            set_setting('firstRun', 'False')

        if self.enable_hyperion:
            self.connection.send_component_state("ALL", True)

        self.initialized = True

    def update_settings(self):
        # update settings, update the connection and updateState().
        self.ip = get_setting('ip')
        self.port = get_setting('port')
        self.video_mode_enabled = get_bool_setting('videoModeEnabled')
        self.enable_hyperion = get_bool_setting('enableHyperion')
        self.disable_hyperion = get_bool_setting('disableHyperion_player_pause')
        self.auth_token = get_setting('authToken')
        self.opt_target_comp = int_to_comp_string(int(get_setting('targetComponent')))
        self.opt_screensaver_enabled = get_bool_setting('screensaverEnabled')
        self.opt_video_enabled = get_bool_setting('videoEnabled')
        self.opt_audio_enabled = get_bool_setting('audioEnabled')
        self.opt_pause_enabled = get_bool_setting('pauseEnabled')
        self.opt_menu_enabled = get_bool_setting('menuEnabled')
        self.opt_debug = get_bool_setting('debug')
        self.opt_show_changelog_on_update = get_bool_setting('showChangelogOnUpdate')
        self.tasks = get_setting('tasks')

        if self.opt_debug:
            self._log_settings()
        self.connection.update_url(self.ip, self.port)
        if validate_auth_token(self.auth_token):
            self.connection.update_header(self.auth_token)
        elif self.auth_token != "":
            notify_user(get_localized_string(32105))
        # do just once on startup, we might want to show a changelog
        if not self.initialized:
            self.initialize()

        self.update_state()

        # Checkout Tasklist for pending tasks
        if self.tasks == '1':
            set_setting('tasks', '0')
            do_ssdp_discovery()

    def _log_settings(self):
        log('Settings updated!')
        log(f'Hyperion ip:           {self.ip}')
        log(f'Hyperion port:         {self.port}')
        log(f'Enable H on start:     {self.enable_hyperion}')
        log(f'Disable H on stop:     {self.disable_hyperion}')
        log(f'VideoMode enabled:     {self.video_mode_enabled}')
        log(f'Hyperion target comp:  {self.opt_target_comp}')
        log(f'Screensaver enabled:   {self.opt_screensaver_enabled}')
        log(f'Video enabled:         {self.opt_video_enabled}')
        log(f'Audio enabled:         {self.opt_audio_enabled}')
        log(f'Pause enabled:         {self.opt_pause_enabled}')
        log(f'Menu enabled:          {self.opt_menu_enabled}')
        log(f'Debug enabled:         {self.opt_debug}')
        log(f'ChangelogOnUpdate:     {self.opt_show_changelog_on_update}')
        log(f'tasks:                 {self.tasks}')

    def stop(self):
        """Stops the hyperion control."""
        if self.disable_hyperion:
            self.connection.send_component_state("ALL", False)
        log("Hyperion-control stopped")

    def update_state(self):
        # update state of the chosen component based on latest settings/kodi states and send the state to hyperion
        # check first screensaver, then pause and as last player!
        if self.monitor.is_screensaver_active():
            if self.opt_debug:
                notify_user("monitor.isScreensaverActive", 1000)
            comp_state = self.opt_screensaver_enabled
        elif self.player.paused:
            if self.opt_debug:
                notify_user("player.paused", 1000)
            comp_state = self.opt_pause_enabled
        elif self.player.isPlayingAudio():
            if self.opt_debug:
                notify_user("player.isPlayingAudio", 1000)
            comp_state = self.opt_audio_enabled
        elif self.player.isPlaying():
            if self.opt_debug:
                notify_user("player.isPlayingVideo", 1000)
            comp_state = self.opt_video_enabled
        else:
            if self.opt_debug:
                notify_user("MENU mode", 1000)
            comp_state = self.opt_menu_enabled

        # update comp state just if required
        if self.prev_comp_state != comp_state:
            self.connection.send_component_state(self.opt_target_comp, comp_state)
            self.prev_comp_state = comp_state

        # update stereoscopic mode always, better apis for detection available?
        # Bug: race condition, return of jsonapi has wrong gui state after onPlayBackStopped after a 3D movie
        if self.video_mode_enabled:
            new_mode = get_stereoscopic_mode()
            if self.prev_video_mode != new_mode:
                self.connection.send_video_mode(new_mode)
                self.prev_video_mode = new_mode


def main():
    player = XBMCPlayer()
    monitor = XBMCMonitor()
    hyperion = Hyperion(player, monitor)

    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            hyperion.stop()
            break



if __name__ == '__main__':
    main()
