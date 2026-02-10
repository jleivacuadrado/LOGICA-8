
PROGRAMS = {
    "1": ("Carga 200, Suma 100, Se detiene.", [0x01, 200, 0x02, 100, 0xFF], 0x00),
    "2": ("Carga 15, Suma 10, Guarda en memoria (en direccion 80), Se detiene.", [0x01, 0x0F, 0x02, 0x0A, 0x03, 0x80, 0xFF], 0x00),
    "3": ("Suma con Overflow (200+100).", [0x01, 200, 0x02, 100, 0xFF], 0x00),
    "4": ("Cuenta Atrás (de 10 a 0). El programa se almacena en la fila 1.", [0x01, 10, 0x05, 1, 0x06, 0x18, 0x04, 0x12, 0xFF], 0x10),
    "5": ("Bucle de incremento en RAM.", [0x01, 0, 0x02, 1, 0x03, 0xFF, 0x04, 0x02], 0x00),
    "6": ("Carga 31, compara mediante XOR (Exclusive-Or) con 74 y muestra en consola resultado en binario y en decimal.", [0x01, 0x1F, 0x09, 0x4A, 0xFF], 0x00),
    "7": ("Multiplicación (5 x 3) usando Registro X como contador.", 
          [
            0x01, 0x00, # 00: LDA #0 (Resultado en A)
            0x0B, 0x03, # 02: LDX #3 (Contador en X)
            0x02, 0x05, # 04: ADD #5 (Bucle: A = A + 5)
            0x0D,       # 06: DEX    (X = X - 1)
            0x06, 0x0B, # 07: BEQ $0C (Si X es 0, salta al STA en la pos 12)
            0x04, 0x04, # 09: JMP $04 (Si no es 0, vuelve al ADD en la pos 4)
            0x03, 0x50, # 0C: STA $50 (Guarda resultado)
            0xFF        # 0E: HALT
          ], 0x00)
}