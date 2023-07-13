import xbmc, xbmcaddon
import simplejson as json
import sys

ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo('id')

def log(message, level=xbmc.LOGINFO):
    xbmc.log(f"[{ADDON_NAME}] {message.encode('utf-8')}", level)

def get_setting(opt):
    return ADDON.getSetting(opt)

def get_addon_version():
    return ADDON.getAddonInfo('version')

def get_addon_changelog():
    return ADDON.getAddonInfo('changelog')

def get_bool_setting(opt):
    """ With Kodi 18 native api available """
    return ADDON.get_setting(opt).upper() == "TRUE"

def set_setting(opt, value):
    return ADDON.setSetting(opt, value)

def open_settings():
    ADDON.openSettings()

def get_localized_string(nr):
    return ADDON.getLocalizedString(nr)

def validate_auth_token(authToken):
    return len(authToken) == 36

def update_saved_addon_version():
    set_setting('currAddonVersion', get_addon_version())

def int_to_comp_string(comp):
    switch = {
        0: "GRABBER",
        1: "V4L",
        2: "LEDDEVICE",
        3: "SMOOTHING",
        4: "BLACKBORDER",
        5: "FORWARDER",
        6: "UDPLISTENER",
        7: "BOBLIGHTSERVER",
        8: "ALL",
    }
    return switch.get(comp, "NOT_FOUND")

def is_py3():
    return sys.version_info[0] == 3

def bytes_decode_utf8(data):
    return data.decode('utf-8') if is_py3() else data

def bytes_encode_utf8(data):
    return data.encode('utf-8') if is_py3() else data

def mode_to_3d(mode=None):
    switch = {
        "split_vertical": "3DSBS",
        "split_horizontal": "3DTAB",
    }
    return switch.get(mode, "2D")

def get_stereoscopic_mode():
    try:
        response = json.loads(bytes_decode_utf8(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["stereoscopicmode"]},"id":669}')))
        mode = response["result"]["stereoscopicmode"]["mode"]
        return mode_to_3d(mode)
    except Exception:
        log("getStereoscopeMode() has thrown an exception!")
        return mode_to_3d()
