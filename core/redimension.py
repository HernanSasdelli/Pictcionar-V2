
from PIL import Image

def redimensionar_imagen(imagen_original, width, height):
    """
    Redimensiona una imagen al tamaño especificado.
    """
    return imagen_original.resize((width, height))