from PIL import Image
from config import DPI

def guardar_imagen(imagen, ruta, dpi=DPI):
    """
    Guarda la imagen en formato JPEG con el DPI definido.
    """
    imagen.convert("RGB").save(ruta, dpi=dpi)