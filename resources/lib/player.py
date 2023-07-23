import xbmc


class Player(xbmc.Player):
    """ xbmc player class """
    def __init__(self):
        super().__init__()
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, command):
        for observer in self._observers:
            observer.notify(command)

    def onPlayBackPaused(self):
        self.notify_observers("pause")

    def onPlayBackResumed(self):
        self._play_handler()

    def onAVStarted(self):
        self._play_handler()

    def onPlayBackStopped(self):
        self.notify_observers("menu")

    def onPlayBackEnded(self):
        self.notify_observers("menu")

    def _play_handler(self):
        command = "playAudio" if self.isPlayingAudio() else "playVideo"
        self.notify_observers(command)
