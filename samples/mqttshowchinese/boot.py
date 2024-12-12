# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import machine
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from web.mqtt.umqttsimple import MQTTClient
import gb2312
import chineseHelper
import ubinascii
import network
import esp
import gc
import time
gc.collect()

ssid = 'CU_eT83'
password = 'wanglijun123456'
mqtt_server = '211.101.235.6'
mqtt_user = '20154530'
mqtt_pass = 'q8899194'
# using default address 0x3C

#mqtt_server = '192.168.1.144'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'22'
topic_pub = b'33'

oled=None 

def drawHz(x, y, oled, newdata):
    size = len(newdata)
    row = y
    col = x
    print(size)
    for i in range(0, size):
        if i%2 == 0:
            row+=1
            col=x
        num = newdata[i]
        for j in range(7, -1, -1):
            bit = num >> j & 0b1
            col+=1
            oled.pixel(col,row,bit)
            
def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    client = MQTTClient(client_id, mqtt_server, port=2883, user=mqtt_user, password=mqtt_pass)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

def sub_cb(topic, msg):
    global oled
    oled.fill(0)
    size = len(msg)
    col = 0
    row = 16
    count = 0
    for i in range(0 , size):
        if msg[i] & 0xe0 == 0xe0:
            chfont = gb2312.fontbyte.utf_bytes([msg[i],msg[i+1],msg[i+2]])
            oledstrs = chineseHelper.instance.GetHzCodeInternal(chfont)
            drawHz((count%8) * 16,(count//8 + 1)*16, oled, oledstrs[0])
            i+=3
            count+=1
        else:
            i+=1
    oled.show()
    

def main():
    global oled
    print("start")
    i2c = I2C(1,sda=Pin(21), scl=Pin(22))
    oled = SSD1306_I2C(128, 64, i2c)
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
        pass
    
    client = connect_and_subscribe()
    
    last_message = 0
    message_interval = 5
    counter = 0
    while True:
        try:
            client.check_msg()
            if (time.time() - last_message) > message_interval:
                msg = b'Hello #%d' % counter
                client.publish(topic_pub, msg)
                last_message = time.time()
                counter += 1
        except OSError as e:
            pass

main()