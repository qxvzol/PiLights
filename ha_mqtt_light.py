"""
Create class for my HA light
"""

from machine import Pin
from umqtt.simple import MQTTClient
import json
from neopixel import Neopixel


OFF=False
ON=True

class HA_MQTT_light:
    # my light data
    pixels = Neopixel(144, 0, 0, "RGBW")
    pixels.fill((0,0,0,0))
    pixels.show()
    def __init__(self, name, mqtt_server):
        self.dev_name = name + "_15072010"
        self.device_cfg = {
                    "identifiers": self.dev_name,
                    "name": "Pi Lights",
                    "model": "RPi Pico-W",
                    "sw": "0.2",
                    "manufacturer": "Ollie Saunders" 
                    }
        self.base_topic="homeassistant/light/"+self.dev_name
        self.discovery_topic=self.base_topic+"/config"
        self.base_command_topic=self.base_topic+"/command"
        self.availability_topic=self.base_topic+"/available"
        self.state_topic=self.base_topic+"/state"
        self.led_value = OFF
        
        def callback(topic,msg):
            self.process_recieved_switch_info(topic,msg)

        self.client = MQTTClient(client_id=name,server=mqtt_server)
        self.client.set_callback(callback)
        print('MQTT connect to server result {}', self.client.connect())
        self.client.subscribe(self.base_command_topic+"/#")
        
    def __str__(self):
        return f"LED state = {self.led_value}"

    def process_recieved_switch_info(self,topic,msg):
        print('received message %s on topic %s' % (msg, topic))
        if msg==b'ON':
            self.pixels.fill((0,0,0,255))
            self.pixels.show()
            self.led_value = ON
        elif msg==b'OFF':
            self.pixels.fill((0,0,0,0))
            self.pixels.show()
            self.led_value = OFF
        else:
            print("error not understood")
        self.publish_state_info()

    def publish_discovery_info(self):
        discovery_payload = {
            "name": "pi_ledf",
            "state_topic": self.state_topic,
            "command_topic": self.base_command_topic+"/switch",
            "availability_topic": self.availability_topic,
            "unique_id": self.dev_name,
            "device": self.device_cfg,
            "brightness_state_topic": self.base_topic+"/brightness/status",
            "brightness_command_topic": self.base_command_topic+"/brightness",
            "rgb_state_topic": self.base_topic+"/rgb/status",
            "rgb_command_topic": self.base_command_topic+"/rgb",
            "state_value_template": "{{ value_json.state }}",
            "brightness_value_template": "{{ value_json.brightness }}",
            "rgb_value_template": "{{ value_json.rgb | join(',') }}",
            }

        print("publish message= ",self.discovery_topic,bytes(json.dumps(discovery_payload), 'utf-8'))
        self.client.publish(self.discovery_topic, bytes(json.dumps(discovery_payload), 'utf-8'),retain=True)
    
    def publish_state_info(self):
        if self.led_value == OFF:
            msg = "OFF"
        else:
            msg = "ON"
        self.client.publish(self.availability_topic, msg='online') 
        self.client.publish(self.state_topic, msg) 