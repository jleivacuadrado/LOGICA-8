
class Memory:
    def __init__(self, size=256):
        self.size = size
        self.data = [0x00] * size

    def read(self, addr):
            # Validamos primero el tipo y luego el rango
            if not isinstance(addr, int):
                raise TypeError(f"Dirección no entera: {addr}")
            if not 0 <= addr < self.size:
                raise IndexError(f"Dirección fuera de rango: ${addr:02X}")
            return self.data[addr]

    def write(self, addr, value):
            # 1. Validación de tipo para la dirección
            if not isinstance(addr, int):
                raise TypeError(f"Dirección no entera: ${addr:02X}")
            
            # 2. Validación de rango de memoria (0-255)
            if addr < 0 or addr >= self.size:
                # En lugar de solo fallar, informamos del intento de acceso ilegal
                print(f"DEBUG: intento de escritura en dirección ${addr:02X} (fuera de rango)")
                raise ValueError(f"Dirección de memoria ${addr:02X} fuera de rango (0-255).")
                
            # 3. Validación de tipo para el valor
            if not isinstance(value, int):
                raise TypeError(f"Error de Datos: El valor {value} debe ser un entero.")
                
            # 4. Escritura física con máscara de seguridad de 8 bits
            self.data[addr] = int(value) & 0xFF