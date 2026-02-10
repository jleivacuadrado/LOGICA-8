
def parse_value(s):
    """
    Convierte strings en enteros de 8 bits de forma estricta:
    - 0x... : Hexadecimal
    - %...  : Binario
    - Sin prefijo: Decimal
    """
    s = s.strip().lower()
    try:
        if s.startswith('0x'):
            return int(s[2:], 16)
        elif s.startswith('%'):
            return int(s[1:], 2)
        else:
            # Si no hay prefijo, asumimos DECIMAL puro
            return int(s, 10)
    except ValueError:
        return None


# Mapeo de instrucciones en ensamblador a OpCodes
ASM_TO_HEX = {
    "LDA": 0x01, "ADD": 0x02, "STA": 0x03, "JMP": 0x04,
    "SUB": 0x05, "BEQ": 0x06, "AND": 0x07, "OR": 0x08,
    "XOR": 0x09, "NOT": 0x0A, "LDX": 0x0B, "INX": 0x0C,
    "DEX": 0x0D, "HALT": 0xFF
}

# Lista de instrucciones que NO llevan valor adicional (solo ocupan 1 byte)
SINGLE_BYTE_INSTR = ["INX", "DEX", "NOT", "HALT"]


def assembler():
    print("\n--- LOGICA-8 - ENSAMBLADOR ---")
    print("Escribe una instrucción por línea (ej: LDA 0x05).")
    print("Escribe 'FIN' para terminar y cargar.")
    print("-" * 35)
    
    codigo_usuario = []
    bytecode_final = []
    direccion_actual = 0
    
    while True:
        linea = input(f"${direccion_actual:02X} > ").upper().strip()
        if linea == "FIN": break
        if not linea: continue
        
        partes = linea.split()
        mnemonico = partes[0]
        
        if mnemonico in ASM_TO_HEX:
            opcode = ASM_TO_HEX[mnemonico]
            
            # Caso A: Instrucciones simples (1 byte)
            if mnemonico in SINGLE_BYTE_INSTR:
                print(f"      [ TRADUCCIÓN: {opcode:02X} ]")
                bytecode_final.append(opcode)
                direccion_actual += 1
            
            # Caso B: Instrucciones con valor (2 bytes)
            elif len(partes) > 1:
                valor = parse_value(partes[1])
                if valor is not None and 0 <= valor <= 255:
                    print(f"      [ TRADUCCIÓN: {opcode:02X} {valor:02X} ]")
                    bytecode_final.extend([opcode, valor])
                    direccion_actual += 2
                else:
                    print("      [ ERROR: Valor no válido ]")
            else:
                print(f"      [ ERROR: {mnemonico} necesita un valor ]")
        else:
            print(f"      [ ERROR: Instrucción desconocida ]")
            
    return bytecode_final