# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
gc.collect()
import ujson
with open('secrets.json', 'r') as openfile:
    # file includes   "devicename", "SSID", "SSIDpass", "StaticIP", "mqttserver", "mqttusername", "mqttpass",
    # "topicpub", "topicsub",
    secrets = ujson.load(openfile)
import network
network.WLAN(network.STA_IF).active(False)  # WiFi station interface
#network.WLAN(network.AP_IF).active(False)  # access-point interface
wlan = network.WLAN(network.STA_IF)
if not wlan.isconnected():
    wlan.active(True)
    #wlan.scan()
    wlan.ifconfig((secrets["StaticIP"], '255.255.255.0', secrets["RouterIP"], secrets["RouterIP"]))
    wlan.connect(secrets["SSID"], secrets["SSIDpass"])