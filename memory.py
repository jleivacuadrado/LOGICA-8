
class Memory:
    def __init__(self, size=256):
        self.size = size
        self.data = [0x00] * size

    def read(self, addr):
        if not 0 <= addr < 256:
            print(f"DEBUG: intento de lectura en dirección {addr}), PC={self.PC}")
            raise IndexError(f"Dirección fuera de rango: {addr}")
        if not isinstance(addr, int):
            raise TypeError(f"Dirección no entera: {addr}")
        return self.data[addr]

    def write(self, addr, value):
        if not isinstance(addr, int):
            raise TypeError(f"Dirección no entera: {addr}")
        if addr < 0 or addr >= self.size:
            raise ValueError(f"Dirección fuera de rango: {addr}")
        if not isinstance(value, int):
            raise TypeError(f"Valor no entero: {value}")
        self.data[addr] = value & 0xFF