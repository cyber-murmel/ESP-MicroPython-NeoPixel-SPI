# NeoPixel SPI driver for MicroPython on ESP32
# MIT license; Copyright (c) 2020 Markus Blechschmidt

from machine import Pin, SPI

bitpair_map = {
    0b00 : bytes([0b10001000]),
    0b01 : bytes([0b10001110]),
    0b10 : bytes([0b11101000]),
    0b11 : bytes([0b11101110])
}

nibble_map = [bitpair_map[val>>2] + bitpair_map[val&0b11] for val in range(0, 0x10)]
del(bitpair_map)

byte_map = [nibble_map[val>>4] + nibble_map[val&0b1111] for val in range(0, 0x100)]
del(nibble_map)

byte_inv_map = {byte_map[i]: i for i in range(0, 0x100)}

class NeoPixel:
    ORDER = (0, 1, 2, 3)

    def __init__(self, pin, n, bpp=3):
        if Pin(13) == pin:
            self.spi = SPI(1, baudrate=3200000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=Pin(14), mosi=Pin(13), miso=Pin(12)) # HSPI
        else if Pin(23) == pin:
            self.spi = SPI(2, baudrate=3200000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=Pin(18), mosi=Pin(23), miso=Pin(19)) # VSPI
        else:
            raise ValueError("Pin must be 13 or 23")
        self.n = n
        self.bpp = bpp
        self.buf = bytes([0b10001000]) * 4 * n * bpp

    def __setitem__(self, index, color):
        color = b''.join([byte_map[byte] for byte in color])
        self.buf = self.buf[:4 * index * self.bpp] + color + self.buf[4 * (index+1) * self.bpp:]

    def __getitem__(self, index):
        offset = 4 * index * self.bpp
        return tuple(byte_inv_map(self.buf[offset + 4*self.ORDER[i]:offset + 4*self.ORDER[i]+4]) for i in range(self.bpp))

    def fill(self, color):
        color = b''.join([byte_map[byte] for byte in color])
        self.buf = color*n

    def write(self):
        self.spi.write(self.buf)
