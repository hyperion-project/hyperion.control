import xbmc, xbmcaddon
import simplejson as json

ADDON = xbmcaddon.Addon()
ADDONNAME = ADDON.getAddonInfo('id')

def log(message, level=xbmc.LOGNOTICE):
    xbmc.log('[%s] %s' % (ADDONNAME, message.encode('utf-8')), level)

def getSetting(opt):
    return ADDON.getSetting(opt)

def getAddonVersion():
    return ADDON.getAddonInfo('version')

def getAddonChangelog():
    return ADDON.getAddonInfo('changelog')

def getBoolSetting(opt):
    """ With Kodi 18 native api available """
    return True if ADDON.getSetting(opt).upper() == "TRUE" else False

def setSetting(opt, value):
    return ADDON.setSetting(opt, value)

def openSettings():
    ADDON.openSettings()

def getLS(nr):
    return ADDON.getLocalizedString(nr)

def validateAuthToken(authToken):
    return True if len(authToken) == 36 else False

def updateSavedAddonVersion():
    setSetting('currAddonVersion', getAddonVersion())
    
def intToCompString(comp):
    switch = {
        0: "COMP_GRABBER",
        1: "COMP_V4L",
        2: "COMP_LEDDEVICE",
        3: "COMP_SMOOTHING",
        4: "COMP_BLACKBORDER",
        5: "COMP_FORWARDER",
        6: "COMP_BOBLIGHTSERVER",
        7: "COMP_ALL",
    }
    return switch.get(comp, "NOT_FOUND")

def modeTo3D(mode=None):
    switch = {
        "split_vertical": "3DSBS",
        "split_horizontal": "3DTAB",
    }
    return switch.get(mode, "2D")

def getStereoscopeMode():
    try:
        response = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["stereoscopicmode"]},"id":669}'))
        mode = response["result"]["stereoscopicmode"]["mode"]
        return modeTo3D(mode)

    except:
        log("getStereoscopeMode() has thrown an exception!")
        return modeTo3D()
