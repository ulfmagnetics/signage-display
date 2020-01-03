import board
import displayio
import terminalio
import neopixel
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_bluefruit_connect.button_packet import ButtonPacket
from adafruit_display_text import label
from adafruit_gizmo import tft_gizmo
from time import sleep

ble = BLERadio()
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1)
pixel_position = 0
pixel_color = (10,0,0)

display = tft_gizmo.TFT_Gizmo()
splash = displayio.Group(max_size=10)
display.show(splash)

color_bitmap = displayio.Bitmap(240, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x666600

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

text_group = displayio.Group(max_size=10, scale=2, x=50, y=120)
text = 'Hello World!'
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
        if isinstance(packet, ColorPacket):
            print(packet.color)
            pixel_color = packet.color
        elif isinstance(packet, ButtonPacket):
            if packet.pressed:
                print(packet.button)
                if packet.button == '7':
                    pixel_position = pixel_position - 1
                    if pixel_position < 0:
                        pixel_position = 9
                elif packet.button == '8':
                    pixel_position = pixel_position + 1
                    if pixel_position > 9:
                        pixel_position = 0

                position_label = 'Position: {0}'.format(str(pixel_position))
                text_group.remove(text_area)
                text_area = label.Label(terminalio.FONT, text=position_label, color=0x000000)
                text_group.append(text_area)
