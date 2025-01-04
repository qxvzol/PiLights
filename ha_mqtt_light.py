"""
Create class for my HA light
"""

from machine import Pin
from umqtt.simple import MQTTClient
import json

OFF=0
ON=1

class HA_MQTT_light:
    # my light data
    led = Pin("LED", Pin.OUT)
    def __init__(self, name, mqtt_server):
        self.name = name
        self.ha_mqtt_state_topic="ollie/"+name+"/state"
        self.ha_mqtt_command_topic="ollie/"+name+"/switch"
        self.ha_mqtt_discovery_topic="homeassistant/light/"+name+"/config"
        def callback(topic,msg):
            self.process_recieved_switch_info(topic,msg)

        self.client = MQTTClient(client_id=name,server=mqtt_server)
        self.client.set_callback(callback)
        print('MQTT connect to server result {}', self.client.connect())
        self.client.subscribe(self.ha_mqtt_command_topic+"/#")
        
    def __str__(self):
        return f"LED state = {self.led.value()}"

    def process_recieved_switch_info(self,topic,msg):
        print('received message %s on topic %s' % (msg, topic))
        if msg==b'ON':
            self.led.on()
        elif msg==b'OFF':
            self.led.off()
        else:
            print("error not understood")

    def publish_discovery_info(self):
        discovery_payload = {
            "name": self.name,
            "state_topic": self.ha_mqtt_state_topic,
            "command_topic": self.ha_mqtt_command_topic,
            "optimistic": "false"
            }
        self.client.publish(self.ha_mqtt_discovery_topic, bytes(json.dumps(discovery_payload), 'utf-8'))
    
    def publish_state_info(self):
        self.client.publish(self.ha_mqtt_state_topic, msg="OFF")