import xbmc


class XBMCMonitor(xbmc.Monitor):
    """ xbmc monitor class """
    def __init__(self):
        super().__init__()
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, command):
        for observer in self._observers:
            observer.notify(command)

    def onSettingsChanged(self):
        self.notify_observers("updateSettings")

    def onScreensaverActivated(self):
        self.notify_observers("screensaver")

    def onScreensaverDeactivated(self):
        self.notify_observers("menu")
