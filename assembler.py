
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
    print("\n--- LOGICA-8 - ASSEMBLER ---")
    print("Intruduce instrucciones, 'ETIQUETA:' definir saltos o 'FIN' para compilar.")
    print("-" * 40)
    
    lineas_brutas = []
    while True:
        linea = input("> ").strip()
        if linea.upper() == "FIN": break
        if not linea: continue
        lineas_brutas.append(linea)
    
    labels = {}
    direccion_actual = 0
    instrucciones_limpias = []

    # --- PASADA 1: Mapeo de Etiquetas y Validación ---
    for linea in lineas_brutas:
        # Limpiar espacios y separar por tokens
        tokens = linea.replace(':', ': ').split()
        if not tokens: continue
        
        primer_token = tokens[0].upper()
        
        if primer_token.endswith(':'):
            label_name = primer_token[:-1]
            if label_name in labels:
                print(f"ERROR: Etiqueta duplicada '{label_name}'")
                return None
            labels[label_name] = direccion_actual
            # Si hay algo después de los ":" en la misma línea, es una instrucción
            if len(tokens) > 1:
                tokens = tokens[1:] 
            else:
                continue # Línea de solo etiqueta, no suma dirección
        
        # Calcular tamaño de la instrucción
        mnemonico = tokens[0].upper()
        if mnemonico in ASM_TO_HEX:
            instrucciones_limpias.append((direccion_actual, tokens))
            direccion_actual += 1 if mnemonico in SINGLE_BYTE_INSTR else 2
        else:
            print(f"ERROR: Instrucción desconocida '{mnemonico}'")
            return None

    # --- PASADA 2: Generación de Bytecode ---
    bytecode = []
    print(f"\n{'DIR':<5} | {'ASM':<15} | {'HEX'}")
    print("-" * 35)

    for addr, tokens in instrucciones_limpias:
        mnemonico = tokens[0].upper()
        opcode = ASM_TO_HEX[mnemonico]
        
        if mnemonico in SINGLE_BYTE_INSTR:
            print(f"${addr:02X} | {mnemonico:<15} | {opcode:02X}")
            bytecode.append(opcode)
        else:
            if len(tokens) < 2:
                print(f"ERROR: '{mnemonico}' requiere un argumento.")
                return None
            
            arg = tokens[1].upper()
            # ¿Es una etiqueta o un número literal?
            if arg in labels:
                valor = labels[arg]
            else:
                valor = parse_value(arg)
            
            if valor is not None and 0 <= valor <= 255:
                print(f"${addr:02X} | {mnemonico} {arg:<11} | {opcode:02X} {valor:02X}")
                bytecode.extend([opcode, valor])
            else:
                print(f"ERROR: Argumento o etiqueta inválida '{arg}'")
                return None
                
    return bytecode