def cm_a_px(valor_cm, dpi):
    return int(round((dpi / 2.54) * valor_cm))

def px_a_cm(valor_px, dpi):
    return round((valor_px * 2.54) / dpi, 2)

def validar_dimension(valor):
    try:
        num = float(valor)
        return num > 0
    except ValueError:
        return False
