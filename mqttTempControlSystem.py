import paho.mqtt.client as mqtt
import os
import yaml
import time
import threading
import autoUpdate as updater

updater.performAutoupdate()

coolingThreshold = 35.0
coolingRelaisChannel = 2
coolingTime = 60
freezeWarnThreshold = 5.0
greenhouseWateringChannel = 1
fieldWateringChannel = 3

baseTopic = "GreenhouseControl"
greenHouseWateringTopic = "greenhouseWater"
coolingTopic = "coolingStatus"
fieldWaterTopic = "fieldWater"

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
        client.subscribe("GreenhouseControl/isAlive/set")
        #client.subscribe("shellies/GreenhouseTemp/sensor/temperature")
        client.subscribe("GreenhouseControl/tempSensor01")
        client.subscribe("GreenhouseControl/coolingStatus/set")
        client.subscribe("GreenhouseControl/greenhouseWater/set")
        client.subscribe("GreenhouseControl/fieldWater/set")
        print("cooling threshold is "+str(coolingThreshold)+" °C")
        print("freeze-warn threshold is "+str(freezeWarnThreshold)+" °C")

        print("publishing initial system status")
        client.publish("GreenhouseControl/isAlive", '{"state": "ON"}', qos=2)
        client.publish("GreenhouseControl/freezeWarning", '{"state": "OFF"}', qos=2)
        client.publish("GreenhouseControl/lastReceivedTemp", qos=2)
        client.publish("GreenhouseControl/greenhouseWater", '{"state": "OFF"}', qos=2)
        client.publish("GreenhouseControl/fieldWater", '{"state": "OFF"}', qos=2)
        
        
    else:
        print(f"Connected fail with code {rc}")

def on_message_print(client, userdata, message):
     #print("%s %s" % (message.topic, message.payload))    

    #if message.topic == "shellies/GreenhouseTemp/sensor/temperature":
    if message.topic == "GreenhouseControl/tempSensor01":
        print("Temperature Data Received")
        payloadValue = float(message.payload)
        print(str(payloadValue)+" °C")
        
        if payloadValue>coolingThreshold:
            print("It is too hot")
            activateCooling(client)
            client.publish("GreenhouseControl/lastReceivedTemp", payloadValue, qos=2)
            #timedCoolingThread.start()
            
        elif payloadValue<freezeWarnThreshold:
            print("It is too cold")
            os.system('pinctrl set 21 op pn dh')
            os.system('pinctrl get 21')
            client.publish("GreenhouseControl/freezeWarning", '{"state": "ON"}', qos=2)
            client.publish("GreenhouseControl/lastReceivedTemp", payloadValue, qos=2)
            
        else:
            print("Temperature is optimal")
            deactivateCooling(client)
            client.publish("GreenhouseControl/freezeWarning", '{"state": "OFF"}', qos=2)
            client.publish("GreenhouseControl/lastReceivedTemp", payloadValue, qos=2)

    elif message.topic == "GreenhouseControl/coolingStatus/set":
        #print(message.topic)
        #print(message.payload)
        payloadDict = yaml.safe_load(message.payload)
        
        if payloadDict["state"] == "ON":
            print("manually turning on cooling")
            activateCooling(client)
            
        elif payloadDict["state"] == "OFF":
            print("manually turning off cooling")
            deactivateCooling(client)
            
        else:
            print("unknown state")

    elif message.topic == "GreenhouseControl/greenhouseWater/set":
        payloadDict = yaml.safe_load(message.payload)
        if payloadDict["state"] == "ON":
            print("manually turning on watering")
            
            activateWatering(client)
            
        elif payloadDict["state"] == "OFF":
            print("manually turning off watering")
            deactivateWatering(client)

    elif message.topic == "GreenhouseControl/fieldWater/set":
        payloadDict = yaml.safe_load(message.payload)
        if payloadDict["state"] == "ON":
            print("manually turning on field watering")
            activateFieldWatering(client)
            
        elif payloadDict["state"] == "OFF":
            print("manually turning off field watering")
            deactivateFieldWatering(client)
                        
    elif message.topic == "GreenhouseControl/isAlive/set":
        client.publish("GreenhouseControl/isAlive", '{"state": "OFF"}', qos=2)
        client.publish("GreenhouseControl/isAlive", '{"state": "ON"}', qos=2)
        

def activateCooling(client):
    # os.system('pinctrl '+outputPins[coolingRelaisChannel]+' dl')
    # os.system('pinctrl '+outputPins[coolingRelaisChannel])
    # client.publish("GreenhouseControl/coolingStatus", '{"state": "ON"}', qos=2)
    switchRelais(coolingRelaisChannel,coolingTopic,"on",client)

def deactivateCooling(client):
    # os.system('pinctrl '+outputPins[coolingRelaisChannel]+' dh')
    # os.system('pinctrl '+outputPins[coolingRelaisChannel])
    # client.publish("GreenhouseControl/coolingStatus", '{"state": "OFF"}', qos=2)
    switchRelais(coolingRelaisChannel,coolingTopic,"off",client)

def activateWatering(client):
    #os.system('/usr/bin/python /home/admin/pythonScripts/mqttGreenhouseWater.py on')
    switchRelais(greenhouseWateringChannel,greenHouseWateringTopic,"on",client)

def deactivateWatering(client):
    #os.system('/usr/bin/python /home/admin/pythonScripts/mqttGreenhouseWater.py off')
    switchRelais(greenhouseWateringChannel,greenHouseWateringTopic,"off",client)

def activateFieldWatering(client):
    #os.system('/usr/bin/python /home/admin/pythonScripts/mqttFieldWater.py on')
    switchRelais(fieldWateringChannel,fieldWaterTopic,"on",client)

def deactivateFieldWatering(client):
    #os.system('/usr/bin/python /home/admin/pythonScripts/mqttFieldWater.py off')
    switchRelais(fieldWateringChannel,fieldWaterTopic,"off",client)


def switchRelais(pinChannel, pinChannelName, bEnable, client):
     
    if bEnable == "on":
        os.system('pinctrl '+outputPins[pinChannel]+' dl')
        print("Started watering")
        client.publish("GreenhouseControl/"+pinChannelName, '{"state": "ON"}', qos=2)
    elif bEnable == "off":
        os.system('pinctrl '+outputPins[pinChannel]+' dh')
        print("Stopped watering")
        client.publish("GreenhouseControl/"+pinChannelName, '{"state": "OFF"}', qos=2)
    else:
        os.system('pinctrl '+outputPins[pinChannel])




# def timedCoolingShutdown(client):
#     time.sleep(coolingTime)
#     print("Cooling for "+str(coolingTime)+" seconds")
#     deactivateCooling(client)
#     print("Done cooling")

def initOutputPins(pinDict):
    for outPin in pinDict.values():
        os.system('pinctrl '+outPin+' op dh')
    
initOutputPins(outputPins) # initialize all output pins and set relais to disabled



client = mqtt.Client(client_id="GreenhouseControl")
client.username_pw_set("admin","admin")
client.on_connect = on_connect
client.on_message = on_message_print
client.will_set("GreenhouseControl/isAlive", '{"state": "OFF"}', qos=2)
client.connect("192.168.0.54", 1883, 60)

deactivateCooling(client)
deactivateWatering(client)
deactivateFieldWatering(client)

#timedCoolingThread = threading.Thread(target=timedCoolingShutdown, args=(client,), daemon=True)

client.loop_forever()
