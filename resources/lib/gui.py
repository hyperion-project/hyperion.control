import xbmcgui
from . import ssdp
from .utils import log, openSettings, getLS, getSetting, setSetting, getAddonVersion, getAddonChangelog, updateSavedAddonVersion

def notifyUser(message,time=3000, icon=xbmcgui.NOTIFICATION_INFO):
    xbmcgui.Dialog().notification('Hyperion Control', message.encode('utf-8'), icon, time)

def buildSelectList(data):
    list = []
    for item in data:
        list.append(item["ip"]+":"+item["port"])
    return list

def getSSDPData(data):
    'Returns a list with a dict that contains "ip", "port", "usn" from the ssdp object'
    list = []
    for item in data:
        ipport = item.location[item.location.find("/")+2:item.location.rfind("/")].split(":")
        list.append({"ip":ipport[0], "port": ipport[1], "usn": item.usn})
    return list

def doSSDPDiscovery():
    searchTarget = "urn:hyperion-project.org:device:basic:1"
    #searchTarget = "urn:schemas-upnp-org:device:basic:1"
    filteredResponse = []
    ipPortUsnList = []
    selectedServer = -1
    # start sync search
    response = ssdp.discover(searchTarget)

    for item in response:
        if item.st == searchTarget:
            filteredResponse.append(item)

    if len(filteredResponse) > 0:
        ipPortUsnList = getSSDPData(filteredResponse)
        # if there is more than one entry the user should select one
        if len(filteredResponse) > 1:
            selectedServer = xbmcgui.Dialog().select(getLS(32102), buildSelectList(ipPortUsnList))
        else:
            xbmcgui.Dialog().ok('Hyperion Control', getLS(32103), '-> '+ipPortUsnList[0]["ip"]+':'+str(ipPortUsnList[0]["port"]))
            selectedServer = 0

        #check user input and push settings if valid
        if selectedServer > -1:
            setSetting('SSDPUSN', ipPortUsnList[selectedServer]["usn"])
            setSetting('ip', ipPortUsnList[selectedServer]["ip"])
            setSetting('port', ipPortUsnList[selectedServer]["port"])
        # TODO SSDP USN checks on usual startup to sync ip and port if required. Requires async ssdp
    else:
        xbmcgui.Dialog().ok('Hyperion Control', getLS(32104))
    return

def doInitialWizard():
    if xbmcgui.Dialog().yesno('Hyperion Control',getLS(32100),getLS(32101)):
        doSSDPDiscovery()
        openSettings()
    return

def doChangelogDisplay():
    if getSetting('currAddonVersion') != getAddonVersion():
        xbmcgui.Dialog().textviewer('Hyperion Control - Changelog', getAddonChangelog())
