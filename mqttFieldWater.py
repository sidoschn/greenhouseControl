import paho.mqtt.client as mqtt
import os
import yaml
import sys
import time


#print(len(sys.argv))
if len(sys.argv)>1:
    bEnable = sys.argv[1]
else:
    bEnable = "_"
    
print(bEnable)

greenhouseWateringChannel = 3

# dictionary of available output (relais) pins
outputPins = {
    1:'5',
    2:'6',
    3:'13',
    4:'16',
    5:'19',
    6:'20',
    7:'21',
    8:'26'
}


# The callback function. It will be triggered when trying to connect to the MQTT broker
# client is the client instance connected this time
# userdata is users' information, usually empty. If it is needed, you can set it through user_data_set function.
# flags save the dictionary of broker response flag.
# rc is the response code.
# Generally, we only need to pay attention to whether the response code is 0.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")

        if bEnable == "on":
            os.system('pinctrl '+outputPins[greenhouseWateringChannel]+' dl')
            print("Started watering field")
            client.publish("GreenhouseControl/fieldWater", '{"state": "ON"}', qos=2)
        elif bEnable == "off":
            os.system('pinctrl '+outputPins[greenhouseWateringChannel]+' dh')
            print("Stopped watering field")
            client.publish("GreenhouseControl/fieldWater", '{"state": "OFF"}', qos=2)
        else:
            os.system('pinctrl '+outputPins[greenhouseWateringChannel])
        
        
    else:
        print(f"Connected fail with code {rc}")
    
client = mqtt.Client(client_id="GreenhouseControl_fieldWaterStatus")
client.username_pw_set("dodo","ds1702")
client.on_connect = on_connect
client.connect("192.168.0.10", 1883, 60)

client.loop_start()
time.sleep(0.5)
client.loop_stop()



