import network
import time
from umqtt.simple import MQTTClient

from machine import Pin

from secret import ssid, password, mqtt_server

led = Pin("LED", Pin.OUT)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

def callback(topic, msg):
    print('received message %s on topic %s' % (msg, topic))
    if msg==b'on':
        led.on()
    elif msg==b'off':
        led.off()
    else:
        print("error not understood")

client = MQTTClient(client_id="pylights",server=mqtt_server)
client.set_callback(callback)
client.connect()

client.publish("light/state", msg="OFF")
client.subscribe("light/switch/#")

try:
    while True:
        client.wait_msg()
finally:
    print("Finished.")
    client.disconnect()