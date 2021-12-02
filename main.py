#! /usr/bin/env python3

import sys

try:
    import smbus2
    have_i2c = True
    i2c_port = 1
    i2c_bus = smbus2.SMBus(i2c_port)
except:
    have_i2c = False


class Accel:
    def __init__(self, i2c_addr, trace=False):
        self.i2c_addr = i2c_addr
        self.trace = trace

    def read_byte(self, offset):
        if have_i2c:
            val = i2c_bus.read_byte_data(self.i2c_addr, offset)
        else:
            val = 0x33

        if self.trace:
            print(f'read(0x{self.i2c_addr:x}, 0x{offset}) => 0x{val:x}')

        return val

    
    def read_bytes(self, offset, nbytes):
        if have_i2c:
            buf = i2c_bus.read_i2c_block_data(self.i2c_addr, offset, nbytes)
        else:
            buf = [1] * nbytes

        if self.trace:
            print(f'read(0x{self.i2c_addr:x}, 0x{offset}, {nbytes}) => '
                  + ' '.join([hex(val) for val in buf]))

        return buf

    def write_byte(self, offset, val):
        if self.trace:
            print(f'write(0x{self.i2c_addr:x}, 0x{offset}, 0x{val})')
        if have_i2c:
            i2c_bus.write_byte_data(self.i2c_addr, offset, val)


class Accel_LIS3DH(Accel):
    def __init__(self, lsb, trace=False):
        i2c_addr = 0x18 | lsb
        super().__init__(i2c_addr, trace)

        val = self.read_byte(0xf)
        assert val == 0x33, 'unexpected value in ID register'

        # CTRL_REG1: ODR=200Hz, XYZ enable
        self.write_byte(0x20, 0x67)

    def read_accel(self):
        def decode_s16(lo, hi):
            val = (hi << 8) | lo
            if val & 0x8000:
                val |= -1 << 16
            return val

        # 6 bytes: OUT_X_L...OUT_Z_H
        raw = self.read_bytes(0x28, 6)
        x = decode_s16(raw[0], raw[1])
        y = decode_s16(raw[2], raw[3])
        z = decode_s16(raw[4], raw[5])
        return x, y, z

accel1 = Accel_LIS3DH(1, trace=True)
print(accel1.read_accel())


    
