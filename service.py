import xbmc, xbmcgui
from resources.lib.utils import *
from resources.lib.gui import doInitialWizard, doChangelogDisplay, doSSDPDiscovery, notifyUser
from resources.lib.connection import Connection

class XBMCPlayer(xbmc.Player):
    """ xbmc player class """
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.__playerPause = False
        self.__observers = []

    def __del__(self):
        del self.xbmc.Player

    def register_observer(self, observer):
        self.__observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self.__observers:
            observer.notify(self, *args, **kwargs)

    def notify(self):
        self.notify_observers("updateState")

    def isPausing(self):
        return self.__playerPause

    def onPlayBackPaused(self):
        self.__playerPause = True
        self.notify()

    def onPlayBackResumed(self):
        self.__playerPause = False
        self.notify()

    def onPlayBackStarted(self):
        self.notify()

    def onPlayBackStopped(self):
        self.__playerPause = False
        self.notify()

    def onPlayBackEnded(self):
        self.notify()

class XBMCMonitor(xbmc.Monitor):
    """ xbmc monitor class """
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        self.__screensaverActive = False
        self.__observers = []

    def __del__(self):
        del self.xbmc.Monitor

    def register_observer(self, observer):
        self.__observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self.__observers:
            observer.notify(self, *args, **kwargs)

    def onSettingsChanged(self):
        self.notify_observers("updateSettings")

    def isScreensaverActive(self):
        return self.__screensaverActive

    def onScreensaverActivated(self):
        self.__screensaverActive = True
        self.notify_observers("updateState")

    def onScreensaverDeactivated(self):
        self.__screensaverActive = False
        self.notify_observers("updateState")

class Hyperion:
    """ Main instance class """
    def __init__(self):
        self.prev_videoMode = "2D"
        self.prev_compState = None
        self.initialized = False

        self.player = XBMCPlayer()
        self.player.register_observer(self)
        self.monitor = XBMCMonitor()
        self.monitor.register_observer(self)
        self.connection = Connection()

        self.updateSettings()
        self.daemon()

    def __del__(self):
        del self.player
        del self.monitor

    def notify(self, observable, *args, **kwargs):
        if "updateState" in args:
            self.updateState()
        else:
            self.updateSettings()

    def initialize(self):
        # check for changelog display, but not on first run
        if getBoolSetting('showChangelogOnUpdate') and not getBoolSetting('firstRun'):
            doChangelogDisplay()

        # check for setup wizard
        if getBoolSetting('firstRun'):
            # be sure to fill in the current version
            updateSavedAddonVersion()
            doInitialWizard()
            setSetting('firstRun', 'False')

        if self.enableHyperion:
            self.connection.sendComponentState("ALL", True)

        self.initialized = True

    def updateSettings(self):
        # update settings, update the connection and updateState().
        self.ip = getSetting('ip')
        self.port = getSetting('port')
        self.videoModeEnabled = getBoolSetting('videoModeEnabled')
        self.enableHyperion = getBoolSetting('enableHyperion')
        self.disableHyperion = getBoolSetting('disableHyperion')
        self.authToken = getSetting('authToken')
        self.opt_targetComp = intToCompString(int(getSetting('targetComponent')))
        self.opt_screensaverEnabled = getBoolSetting('screensaverEnabled')
        self.opt_videoEnabled = getBoolSetting('videoEnabled')
        self.opt_audioEnabled = getBoolSetting('audioEnabled')
        self.opt_pauseEnabled = getBoolSetting('pauseEnabled')
        self.opt_menuEnabled = getBoolSetting('menuEnabled')
        self.opt_debug = getBoolSetting('debug')
        self.opt_showChangelogOnUpdate = getBoolSetting('showChangelogOnUpdate')
        self.tasks = getSetting('tasks')

        if self.opt_debug:
            log('Settings updated!')
            log('Hyperion ip:           %s' % (self.ip))
            log('Hyperion port:         %s' % (self.port))
            log('Enable H on start:     %s' % (self.enableHyperion))
            log('Disable H on stop:     %s' % (self.disableHyperion))
            log('VideoMode enabled:     %s' % (self.videoModeEnabled))
            log('Hyperion target comp:  %s' % (self.opt_targetComp))
            log('Screensaver enabled:   %s' % (self.opt_screensaverEnabled))
            log('Video enabled:         %s' % (self.opt_videoEnabled))
            log('Audio enabled:         %s' % (self.opt_audioEnabled))
            log('Pause enabled:         %s' % (self.opt_pauseEnabled))
            log('Menu enabled:          %s' % (self.opt_menuEnabled))
            log('Debug enabled:         %s' % (self.opt_debug))
            log('ChangelogOnUpdate:     %s' % (self.opt_showChangelogOnUpdate))
            log('tasks:                 %s' % (self.tasks))

        self.connection.updateURL(self.ip, self.port)
        if validateAuthToken(self.authToken):
            self.connection.updateHeader(self.authToken)
        elif self.authToken != "":
            notifyUser(getLS(32105))
        # do just once on startup, we might want to show a changelog
        if not self.initialized:
            self.initialize()

        self.updateState()

        # Checkout Tasklist for pending tasks
        if self.tasks == '1':
            setSetting('tasks','0')
            doSSDPDiscovery()

    def daemon(self):
        # Keep the Hyperion class alive, aborts if Kodi requests it
        while not self.monitor.abortRequested():
            if self.monitor.waitForAbort():
                # last steps before script shutdown
                if self.disableHyperion:
                    self.connection.sendComponentState("ALL", False)

                log("Hyperion-control stopped")
                break

    def updateState(self):
        # update state of the chosen component based on latest settings/kodi states and send the state to hyperion
        # check first screensaver, then pause and as last player!
        if self.monitor.isScreensaverActive():
            if self.opt_debug:
                notifyUser("monitor.isScreensaverActive",1000)
            compState = True if self.opt_screensaverEnabled else False
        elif self.player.isPausing():
            if self.opt_debug:
                notifyUser("player.isPausing",1000)
            compState = True if self.opt_pauseEnabled else False
        elif self.player.isPlayingAudio():
            if self.opt_debug:
                notifyUser("player.isPlayingAudio",1000)
            compState = True if self.opt_audioEnabled else False
        elif self.player.isPlaying():
            if self.opt_debug:
                notifyUser("player.isPlayingVideo",1000)
            compState = True if self.opt_videoEnabled else False
        else:
            if self.opt_debug:
                notifyUser("MENU mode",1000)
            compState = True if self.opt_menuEnabled else False

        # update comp state just if required
        if self.prev_compState != compState:
            self.connection.sendComponentState(self.opt_targetComp, compState)
            self.prev_compState = compState

        # update stereoscrope mode always, better apis for detection available?
        # Bug: race condition, return of jsonapi has wrong gui state after onPlayBackStopped after a 3dmovie
        if self.videoModeEnabled:
            newMode = getStereoscopeMode()
            if self.prev_videoMode != newMode:
                self.connection.sendVideoMode(newMode)
                self.prev_videoMode = newMode

if __name__ == '__main__':
    hyperion = Hyperion()
    del hyperion
