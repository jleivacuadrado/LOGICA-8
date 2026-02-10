
class Memory:
    def __init__(self, size=256):
        self.data = bytearray(size)

    def read(self, addr):
        return self.data[addr]

    def write(self, addr, value):
        self.data[addr] = value & 0xFF