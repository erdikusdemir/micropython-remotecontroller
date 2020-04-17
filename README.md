# micropython-remotecontroller
ESP8266 based smart remote controller. Code works on micropython.  
The version with the C++: https://github.com/erdikusdemir/smarthome-wifi-remote  

# DESCRIPTION 

Portable remote controller to control smart home devices over MQTT protocol. It is based on micropython uploaded ESP8266 with OLED LCD and rotary encoder.
Remote can control switches, dimmers, fans, and temperature controllers.

The remote controller communicates with Node-Red flow by MQTT JSON messages. Node-Red flow converts the signals from both remote and HA side and makes implementation easier. Items you would like to control by remote can be edited by "config file" function. Arduino sketch only configures Wifi and MQTT settings. All the item information are called at the initialization stage of the remote.

Wemos kill its power after 15 secs of idle time. Thus, power consumption of the remote is zero when it is not used. 

Hardware is consist of;
1. Wemos D1 mini Pro,
2. A clickable rotary encoder,
3. 0.96" I2C 128x64 OLED display,
4. Wemos battery shield,
5. LIPO battery,
6. 3D printed enclosure (under progress),  
7. TPS27081ADDCR load switch,  
8. 2222A NPN transistor,  
9. 330, 1 k, and 1 MOhm resistors.  

<img src="https://github.com/erdikusdemir/micropython-remotecontroller/blob/master/remote_insidecover.jpg" width="600">
<img src="https://github.com/erdikusdemir/micropython-remotecontroller/blob/master/Schematic.PNG" width="800">


# Micropython installation and code upload:  
1. Install python core from here https://www.python.org/downloads/  
2. Download esptool from here https://github.com/espressif/esptool/releases and unzip in a folder  
3. Download esp8266 micropython firmware from here https://micropython.org/download/esp8266/ (you can pick the recent stable release)  
4. open console in your operating system. for windows: cmd
5. go to the directery of esptool.py  for windows example: cd C:\Users\"user"\Desktop\esptool-master
6. connect the chip to the PC  
7. run "python esptool.py --chip esp8266 erase_flash" (COM port will be showed on the screen. Please note the COM port for the next step(s))  
8. after erase completed run flash code "python esptool.py --port COM7 --baud 460800 write_flash --flash_size=4MB 0 C:\Users\"user"\esp8266-2020.bin" (Don't forget to change your COM port and the full directory of the micropython firmware.)  
9. Edit the secrets.json file according to your credentials and save it  
10. Now we can upload the code. Download "uPyloader" from here https://github.com/BetaRavener/uPyLoader/releases  
11. Run the program and connect to your device. After the first connection a popup window will show up. Say ok and go to File -> Init transfer files. After program sends two files you should see the programs inside the chip  
12. Go to File -> Navigate and select the project folder  
13. On the left side you should see the project files. Select the files with .py extention and the "secrets.json" and press transfer. 
14. After transfer completed hard reset the device and you should good to go  
15. Bravo!  

# Instructions:  
1. Follow the schematic and build the hardware,  
2.1. Modify the secret.json file according to your credentials,  
2.2. Copy the files into the micropython ESP8266,  
3.1. Copy NodeRed flow into your NodeRed server,  
3.2. Configure your HA and MQTT servers,  
3.3. Configure your items by editing "config file" function,  
(id: order in your OLED screen, HAid: id name of item you want to control, type: switch(0), dimmer(1), or temperature controller(2))  
4.4. Deploy the node and everything should works.  

# To do list:
1. ESP chip being very slow to connect to the wifi. This needs to be fasten up somehow. Chip develops an issue when erasing the settings.  
3. Case design needs to be finished.  

