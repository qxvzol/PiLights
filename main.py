"""
My simple MQTT client
"""
import network
import time
from ha_mqtt_light import HA_MQTT_light

from secret import ssid, password, mqtt_server

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

ha_led = HA_MQTT_light("pi_led",mqtt_server)
ha_led.publish_discovery_info()

try:
    while True:
        ha_led.client.wait_msg()
finally:
    print("Finished.")
    ha_led.client.disconnect()