import xbmcgui
import lib.ssdp as ssdp
from lib.utils import open_settings, get_localized_string, get_setting, set_setting, get_addon_version, get_addon_changelog

def notify_user(message, time=3000, icon=xbmcgui.NOTIFICATION_INFO):
    xbmcgui.Dialog().notification('Hyperion Control', message.encode('utf-8'), icon, time)

def build_select_list(data):
    return [item["ip"] + ":" + item["port"] for item in data]

def get_ssdp_data(data):
    """Returns a list with a dict that contains "ip", "port", "usn" from the ssdp object."""
    addresses = []
    for item in data:
        ip_port = item.location[item.location.find("/")+2:item.location.rfind("/")].split(":")
        addresses.append({"ip":ip_port[0], "port": ip_port[1], "usn": item.usn})
    return addresses

def do_ssdp_discovery():
    search_target = "urn:hyperion-project.org:device:basic:1"
    # start sync search
    response = ssdp.discover(search_target)

    if filtered_response := [
        item for item in response if item.st == search_target
    ]:
        ip_port_usn_list = get_ssdp_data(filtered_response)
        # if there is more than one entry the user should select one
        if len(filtered_response) > 1:
            selected_server = xbmcgui.Dialog().select(get_localized_string(32102), build_select_list(ip_port_usn_list))
        else:
            xbmcgui.Dialog().ok(
                'Hyperion Control',
                f'{get_localized_string(32103)}[CR]{ip_port_usn_list[0]["ip"]}:{ip_port_usn_list[0]["port"]}',
            )
            selected_server = 0

        #check user input and push settings if valid
        if selected_server > -1:
            set_setting('SSDPUSN', ip_port_usn_list[selected_server]["usn"])
            set_setting('ip', ip_port_usn_list[selected_server]["ip"])
            set_setting('port', ip_port_usn_list[selected_server]["port"])
    else:
        xbmcgui.Dialog().ok('Hyperion Control', get_localized_string(32104))
    return

def do_initial_wizard():
    if xbmcgui.Dialog().yesno('Hyperion Control', f"{get_localized_string(32100)}[CR]{get_localized_string(32101)}"):
        do_ssdp_discovery()
        open_settings()
    return

def do_changelog_display():
    if get_setting('currAddonVersion') != get_addon_version():
        # updateSavedAddonVersion()
        xbmcgui.Dialog().textviewer('Hyperion Control - Changelog', get_addon_changelog())
