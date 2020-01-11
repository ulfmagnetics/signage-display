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

#------------------------------------------------------

def chain(*iterables):
    # chain('ABC', 'DEF') --> A B C D E F
    for it in iterables:
        for element in it:
            yield element

def fill_bitmap(width, height, value):
    bitmap = displayio.Bitmap(240, 240, 7)
    for x in range(0, width):
        for y in range(0, height):
            bitmap[x,y] = value
    return bitmap

#------------------------------------------------------

display = tft_gizmo.TFT_Gizmo()
splash = displayio.Group(max_size=10)
display.show(splash)

aqi = Aqi()

palette = displayio.Palette(len(aqi.levels) + 1)
palette[0] = 0x000000 # no data available
for level in aqi.levels:
    palette[level.index] = level.rgb

bitmap = fill_bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 0)
bg_sprite = displayio.TileGrid(bitmap, pixel_shader=palette, x=0, y=0)
splash.append(bg_sprite)

text_group = displayio.Group(max_size=10, scale=2, x=20, y=120)
text = 'Air Quality Index'
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_group.append(text_area)
splash.append(text_group)

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
            bitmap = fill_bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, level.index)
            new_sprite = displayio.TileGrid(bitmap, pixel_shader=palette, x=0, y=0)
            splash.remove(bg_sprite)
            splash.insert(0, new_sprite)
            bg_sprite = new_sprite
