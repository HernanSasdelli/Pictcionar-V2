import os
import re
from tkinter import filedialog, messagebox
from PIL import Image
from core.conversion import cm_a_px
from config import DPI


def limpiar_nombre_archivo(nombre):
    return re.sub(r'[\\/:*?"<>|]', "_", nombre)


def guardar_imagenes_redimensionadas(gui):
    errores = []

    if not gui.datos_imagenes:
        messagebox.showwarning("Sin imágenes", "No hay imágenes para guardar.")
        return

    carpeta_destino = filedialog.askdirectory(title="Seleccionar carpeta de destino")
    if not carpeta_destino:
        return
    bloquear = gui.bloquear_proporcion.get()
    ancho_val = gui.entry_ancho.get().strip()
    alto_val = gui.entry_alto.get().strip()

    try:
        if bloquear:
            if ancho_val:
                ancho = float(ancho_val)
                img_ref = Image.open(gui.datos_imagenes[0]["ruta"])
                original_w, original_h = img_ref.size
                alto = round(ancho * original_h / original_w)
            elif alto_val:
                alto = float(alto_val)
                img_ref = Image.open(gui.datos_imagenes[0]["ruta"])
                original_w, original_h = img_ref.size
                ancho = round(alto * original_w / original_h)
            else:
                raise ValueError("Ambos campos vacíos")
        else:
            ancho = float(ancho_val)
            alto = float(alto_val)
    except ValueError:
        messagebox.showerror("Error", "Medidas inválidas.")
        return

    usar_cm = gui.unidad.get() == "cm"
    dpi = DPI

    try:
        if usar_cm:
            dpi = float(gui.entry_dpi.get())
            ancho = cm_a_px(ancho, dpi)
            alto = cm_a_px(alto, dpi)
        else:
            ancho = int(ancho)
            alto = int(alto)
    except:
        messagebox.showerror("Error", "DPI o dimensiones incorrectas.")
        return

    nombres_usados = set()

    for datos in gui.datos_imagenes:
        try:
            ruta_original = datos["ruta"]
            nombre_raw = datos.get("nombre", os.path.splitext(os.path.basename(ruta_original))[0])
            nombre_base = limpiar_nombre_archivo(nombre_raw)
            ext = os.path.splitext(ruta_original)[1].lower()
            img = Image.open(ruta_original)

            if gui.bloquear_proporcion.get():
                img.thumbnail((ancho, alto))
            else:
                img = img.resize((ancho, alto))

            nombre_final = nombre_base + ext
            contador = 1
            while nombre_final in nombres_usados or os.path.exists(os.path.join(carpeta_destino, nombre_final)):
                nombre_final = f"{nombre_base} ({contador}){ext}"
                contador += 1

            img.save(os.path.join(carpeta_destino, nombre_final))
            nombres_usados.add(nombre_final)

        except Exception as e:
            errores.append(f"{ruta_original} → {e}")

    if errores:
        ruta_log = os.path.join(carpeta_destino, "errores_guardado.txt")
        with open(ruta_log, "w", encoding="utf-8") as f:
            f.write("Errores al guardar imágenes:\n\n")
            for error in errores:
                f.write(f"{error}\n")

        messagebox.showwarning(
            "Guardado parcial",
            f"Se guardaron {len(gui.datos_imagenes) - len(errores)} imágenes.\n"
            f"{len(errores)} fallaron.\nRevisá el archivo:\n{ruta_log}"
        )
    else:
        messagebox.showinfo("Completado", "Todas las imágenes fueron guardadas correctamente.")
