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

ble = BLERadio()
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1)
pixel_position = 0
pixel_color = (10,0,0)

display = tft_gizmo.TFT_Gizmo()
splash = displayio.Group(max_size=10)
display.show(splash)

aqi = Aqi()
color_bitmap = displayio.Bitmap(240, 240, 1)
color_palette = displayio.Palette(len(aqi.levels) + 1)
color_palette[0] = 0x000000 # Black (no data available)
for n, level in enumerate(aqi.levels, start=1):
    color_palette[n] = level.rgb

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

text_group = displayio.Group(max_size=10, scale=2, x=50, y=120)
text = 'Air Quality Index'
text_area = label.Label(terminalio.FONT, text=text, color=0x000000)
text_group.append(text_area)
splash.append(text_group)

while True:
    # Advertise when not connected
    ble.start_advertising(advertisement)
    while not ble.connected:
        pass
    ble.stop_advertising()

    while ble.connected:
        pixels.fill((0,0,0))
        pixels[pixel_position] = pixel_color
        pixels.show()

        packet = Packet.from_stream(uart_server)
        print(packet)
        if isinstance(packet, AirQualityPacket):
            print("AirQualityPacket: metric={0}, value={1}".format(packet.metric, packet.value))
        else:
            print("Unknown packet type!")
