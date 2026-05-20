# test_connect.py 
import paho.mqtt.client as mqtt
import os

coolingThreshold = 35.0
freezeWarnThreshold = 5.0


# The callback function. It will be triggered when trying to connect to the MQTT broker
# client is the client instance connected this time
# userdata is users' information, usually empty. If it is needed, you can set it through user_data_set function.
# flags save the dictionary of broker response flag.
# rc is the response code.
# Generally, we only need to pay attention to whether the response code is 0.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")
        client.subscribe("shellies/GreenhouseTemp/sensor/temperature")
        print("cooling threshold is "+str(coolingThreshold)+" °C")
        print("freeze-warn threshold is "+str(freezeWarnThreshold)+" °C")

    else:
        print(f"Connected fail with code {rc}")

def on_message_print(client, userdata, message):
    print("Temperature Data Received")
    #print("%s %s" % (message.topic, message.payload))
    payloadValue = float(message.payload)
    print(str(payloadValue)+" °C")
    
    if payloadValue>coolingThreshold:
        print("It is too hot")
        os.system('pinctrl set 21 op pn dh')
        os.system('pinctrl get 21')
    elif payloadValue<freezeWarnThreshold:
        print("It is too cold")
        os.system('pinctrl set 21 op pn dh')
        os.system('pinctrl get 21')
    else:
        print("Temperature is optimal")
        os.system('pinctrl set 21 op pn dl')
        os.system('pinctrl get 21')

client = mqtt.Client(client_id="GreenhouseControl")
client.username_pw_set("dodo","ds1702")
client.on_connect = on_connect
client.on_message = on_message_print
client.connect("192.168.0.10", 1883, 60)
client.loop_forever()
