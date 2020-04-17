# -----------------------------------------Libraries--------------------------------------------------------------------
import machine
from machine import Pin, I2C, ADC, Timer
import utime
import ssd1306
import network
import ujson
from simple import MQTTClient

# -----------------------------------------Parameter Init---------------------------------------------------------------
killswitch = Pin(16, Pin.OUT)  #kill switch
killswitch.value(1)

oldencdata = 0b0000
encdata = 0b0000
debouncetime = 150
lastbouncetime = 0
updatescreen = 1
dispcursor = 0
pnr = 0
ticktock = 0

Menu0 = ["id1", "id2", "id3", "id4", "id5", "id6", "id7", "id8", "id9", "id10"]
Value0 = ["off", "off", "0", "20", "40", "600", "80", "100", "on", "off", "ON", "OFF"]
Value1 = ["0", "10", "20", "30", "40", "23", "600", "70", "26", "90", "100", "30"]
datatype = [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]


# -------------------------------------------Read the Secrets.json------------------------------------------------------
with open('secrets.json', 'r') as openfile:
    # file includes   "devicename", "SSID", "SSIDpass", "StaticIP", "mqttserver", "mqttusername", "mqttpass",
    #"topicpub", "topicsub",
    secrets = ujson.load(openfile)



#--------------------------------------------MQTT connection-----------------------------------------------------------
def mqttpublisher():
    global mqttobject
    initialmsg = {}
    initialmsg["id"] = 99
    initialmsgjson = ujson.dumps(initialmsg)
    mqttobject.publish(secrets["topicpub"], initialmsgjson)

def mqttconfig(v):
    global mqttobject
    if wlan.isconnected():
        mqttconn.deinit()
        mqttobject = MQTTClient(secrets["devicename"], secrets["mqttserver"], port=1883, user=secrets["mqttusername"], password=secrets["mqttpass"])
        mqttobject.set_callback(mqttcallback)
        mqttobject.connect()
        mqttobject.subscribe(secrets["topicsub"])
        mqttpublisher()
        mqttconn.init(period=150, mode=Timer.PERIODIC, callback=newmsg)


def mqttcallback(topic, msg):
    global updatescreen
    rcvmsg = ujson.loads(msg)
    Value0[rcvmsg["id"]] = rcvmsg["value0"]
    Value1[rcvmsg["id"]] = rcvmsg["value1"]
    if "name" in rcvmsg:
        Menu0[rcvmsg["id"]] = rcvmsg["name"]
        datatype[rcvmsg["id"]] = rcvmsg["type"]
    updatescreen = 1


def newmsg(v):
    global mqttobject
    mqttobject.check_msg()


# -------------------------------------------WIFI connection-----------------------------------------------------------
wlan = network.WLAN(network.STA_IF)
if not wlan.isconnected():
    wlan.active(True)
    wlan.connect(secrets["SSID"], secrets["SSIDpass"])
    mqttconn = Timer(2)
    mqttconn.init(mode=Timer.PERIODIC, period=200, callback=mqttconfig)  # one shot firing after 1000ms
# ------------------------------------------Functions-------------------------------------------------------------------


def dispcursorupdate(incdec):
    global dispcursor, pnr
    if encbut.value() == 0:
        dispcursor = dispcursor + incdec
    elif datatype[dispcursor] == 1:  # set dimmer
        Value1[dispcursor] = str(int(Value1[dispcursor]) + 10 * incdec)
        pnr = 1
        if int(Value1[dispcursor]) < 0:
            Value1[dispcursor] = "0"
        if int(Value1[dispcursor]) > 100:
            Value1[dispcursor] = "100"
    elif datatype[dispcursor] == 2:  # set temp
        Value1[dispcursor] = str(int(Value1[dispcursor]) + incdec)
        pnr = 1
        if int(Value1[dispcursor]) < 18:
            Value1[dispcursor] = "18"
        if int(Value1[dispcursor]) > 30:
            Value1[dispcursor] = "30"


def encmove(v):
    irq_state = machine.disable_irq()  # Start of critical section
    global value, encdata, oldencdata, oled, dispcursor, updatescreen, ticktock
    encdata = (encA.value() << 1) | encB.value()
    if ((oldencdata | encdata) == 0b0001) or ((oldencdata | encdata) == 0b1110):  # CW turn.
        dispcursorupdate(1)
    elif ((oldencdata | encdata) == 0b0100) or ((oldencdata | encdata) == 0b1011):  # CCW turn.
        dispcursorupdate(-1)
    oldencdata = encdata << 2
    machine.enable_irq(irq_state)
    updatescreen = 1
    ticktock = utime.ticks_ms()
    killme.init(period=15000, mode=Timer.ONE_SHOT, callback=shutdown)

def encbutprss(a):
    global debouncetime, lastbouncetime, updatescreen, dispcursor, pnr, ticktock
    irq_state = machine.disable_irq()  # Start of critical section
    now = utime.ticks_ms()  # get current time
    if now - lastbouncetime > debouncetime and pnr == 0:
        mqttpublisher()
        ticktock = utime.ticks_ms()
        killme.init(period=15000, mode=Timer.ONE_SHOT, callback=shutdown)
        if Value0[dispcursor] == "off":
            Value0[dispcursor] = "on"
        else:
            Value0[dispcursor] = "off"
    pnr = 0
    lastbouncetime = now
    updatescreen = 1
    machine.enable_irq(irq_state)


def screenhandler(v):  # lasts 78 ms
    global dispcursor, updatescreen, SSID, mqttobject
    if updatescreen:
        if dispcursor <= -1:
            dispcursor = -1
            oled.text("Battery:", 0, 0)
            oled.text(str(pot.read()), 64, 0)
            oled.text("SSID:", 0, 10)
            oled.text(secrets["SSID"], 38, 10)
            oled.text("IP:", 0, 20)
            wifispec = wlan.ifconfig()
            oled.text(wifispec[0], 24, 20)
            oled.text("MQTT: ", 0, 30)
            oled.text(secrets["mqttserver"], 0, 40)
        else:
            if dispcursor > len(Menu0) - 1:
                dispcursor = len(Menu0) - 1
            oled.text(">", 0, (dispcursor % 6) * 10)  # cursor
            if dispcursor // 6 < (len(Menu0) - 1) // 6:
                rmax = (dispcursor // 6 + 1) * 6
            else:
                rmax = len(Menu0)
            for i in range((dispcursor // 6) * 6, rmax):
                oled.text(Menu0[i], 8, (i % 6) * 10)
                oled.text(str(Value0[i]), 80, (i % 6) * 10)
                oled.text(str(Value1[i]), 105, (i % 6) * 10)
        oled.show()  # lasts 70 ms
        oled.fill(0)
        updatescreen = 0


def shutdown(v):
    killswitch.value(0)
    print("goodby cruel world")

# ----------------------------------------------Tickers-----------------------------------------------------------------
fps = Timer(1)  # create tim object
fps.init(period=150, mode=Timer.PERIODIC, callback=screenhandler)  # tim init,callback blink() per second
#timer2: mqttconn
killme = Timer(3)
killme.init(period=15000, mode=Timer.ONE_SHOT, callback=shutdown)
# ----------------------------------------------IO Setup----------------------------------------------------------------
i2c = I2C(-1, scl=Pin(5), sda=Pin(4))  # Oled screen
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
pot = ADC(0)

encA = Pin(12, Pin.IN, Pin.PULL_UP)  # create Button object from pin15,Set Pin15 to input
encA.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encmove)
encB = Pin(13, Pin.IN, Pin.PULL_UP)
encB.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encmove)
encbut = Pin(14, Pin.IN)  # create Button object from pin15,Set Pin15 to input
encbut.irq(trigger=Pin.IRQ_FALLING, handler=encbutprss)

def main():
    if utime.ticks_ms() - ticktock > 15000:
        shutdown(0)

# ---------------------------------------------------Main Loop-----------------------------------------------------------

if __name__ == '__main__':
    #main()
    pass
"""
while True:#bu döngü işlemciyi şişiriyor.
    if utime.ticks_ms() - ticktock > 15000:
        shutdown(0)
"""
#if main nasıl cagırılabilir

# -------------------------------------------------End of Main Loop------------------------------------------------------