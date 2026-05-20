import paho.mqtt.client as mqtt
import os
import time


sensorDataLocation = "/sys/bus/w1/devices/28-0e2461c86a63/w1_slave"
updateInterval = 120 #update interval in seconds

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")

        with open(sensorDataLocation) as sensorFile:
            fileContent = sensorFile.read()
            tempIndicatorLocation = fileContent.find('t=')
            tempValue = float((fileContent[tempIndicatorLocation+2:]))/1000.0
            print(tempValue)
            client.publish("GreenhouseControl/tempSensor01", tempValue, qos=2)
        
    else:
        print(f"Connected fail with code {rc}")



while True:
    time.sleep(updateInterval)

    client = mqtt.Client(client_id="GreenhouseControl_tempSensor")
    client.username_pw_set("dodo","ds1702")
    client.on_connect = on_connect
    client.connect("192.168.0.10", 1883, 60)

    client.loop_start()
    time.sleep(0.5)
    client.loop_stop()
    
