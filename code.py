import board
import displayio
import terminalio
import neopixel
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_display_text import label
from adafruit_gizmo import tft_gizmo
from time import sleep

from signage_air_quality.air_quality_packet import Packet, AirQualityPacket
from signage_air_quality.aqi import Aqi

DISPLAY_WIDTH=240
DISPLAY_HEIGHT=240
MAX_COLORS=7

#------------------------------------------------------

def draw_background(width, height, top, bottom):
    bitmap = displayio.Bitmap(width, height, MAX_COLORS)
    for x in range(0, width):
        for y in range(0, x):
            bitmap[x,y] = top
        for y in range(x, height):
            bitmap[x,y] = 0 if (x == y) else bottom

    return bitmap

#------------------------------------------------------

display = tft_gizmo.TFT_Gizmo()
splash = displayio.Group(max_size=10)
display.show(splash)

aqi = Aqi()
colors = {'PM2.5': 0, 'O3': 0}
value_text = {'PM2.5': '', 'O3': ''}
label_text = {'PM2.5': '', 'O3': ''}

palette = displayio.Palette(len(aqi.levels) + 1)
palette[0] = 0x000000 # no data available
for level in aqi.levels:
    palette[level.index] = level.rgb

bitmap = draw_background(DISPLAY_WIDTH, DISPLAY_HEIGHT, colors['PM2.5'], colors['O3'])
bg_sprite = displayio.TileGrid(bitmap, pixel_shader=palette, x=0, y=0)
splash.append(bg_sprite)

pm25_value_group = displayio.Group(scale=3, x=180, y=60)
pm25_text = label.Label(terminalio.FONT, text='--', color=0x000000)
pm25_value_group.append(pm25_text)
splash.append(pm25_value_group)

o3_value_group = displayio.Group(scale=3, x=60, y=180)
o3_text = label.Label(terminalio.FONT, text='--', color=0x000000)
o3_value_group.append(o3_text)
splash.append(o3_value_group)

#text_group = displayio.Group(max_size=10, scale=2, x=20, y=120)
#text = 'Air Quality Index'
#text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
#text_group.append(text_area)
#splash.append(text_group)

ble = BLERadio()
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)

while True:
    ble.start_advertising(advertisement)
    while not ble.connected:
        pass
    ble.stop_advertising()

    while ble.connected:
        packet = Packet.from_stream(uart_server)
        if isinstance(packet, AirQualityPacket):
            print("AirQualityPacket: metric={0}, value={1}".format(packet.metric, packet.value))
            level = aqi.level_for_value(packet.value)
            colors[packet.metric] = level.index
            value_text[packet.metric] = str(packet.value)
            label_text[packet.metric] = level.label

            bitmap = draw_background(DISPLAY_WIDTH, DISPLAY_HEIGHT, top=colors['PM2.5'], bottom=colors['O3'])
            new_sprite = displayio.TileGrid(bitmap, pixel_shader=palette, x=0, y=0)
            splash.remove(bg_sprite)
            splash.insert(0, new_sprite)
            bg_sprite = new_sprite

            # FIXME: choose text colors conditionally based on background color
            if packet.metric == 'PM2.5':
                new_pm25_text = label.Label(terminalio.FONT, text=value_text['PM2.5'], color=0x000000)
                pm25_value_group.remove(pm25_text)
                pm25_value_group.append(new_pm25_text)
                pm25_text = new_pm25_text
            elif packet.metric == 'O3':
                new_o3_text = label.Label(terminalio.FONT, text=value_text['O3'], color=0x000000)
                o3_value_group.remove(o3_text)
                o3_value_group.append(new_o3_text)
                o3_text = new_o3_text
