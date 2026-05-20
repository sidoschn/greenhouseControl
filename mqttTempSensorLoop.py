import paho.mqtt.client as mqtt
import os
import time
from ds18b20 import DS18B20

sensor = DS18B20()
updateInterval = 120 #update interval in seconds

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")

        tempValue = sensor.get_temperature()

        client.publish("GreenhouseControl/tempSensor01", tempValue, qos=2)
        
    else:
        print(f"Connected fail with code {rc}")



while True:
    time.sleep(updateInterval)

    client = mqtt.Client(client_id="GreenhouseControl_tempSensor")
    client.username_pw_set("admin","admin")
    client.on_connect = on_connect
    client.connect("192.168.0.54", 1883, 60)

    client.loop_start()
    time.sleep(0.5)
    client.loop_stop()
    
