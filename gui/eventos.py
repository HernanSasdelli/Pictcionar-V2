from tkinter import filedialog, Entry, Label, messagebox
import tkinter as tk
import os

 
from PIL import Image, ImageTk
from gui.seleccion import registrar_imagen
from gui.conversion import cm_a_px, validar_dimension



THUMBNAIL_SIZE = (150, 150)

def agregar_imagen(gui):
    rutas = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp")])
    if not rutas:
        return

    import os

    for ruta in rutas:
        if ruta not in [img["ruta"] for img in gui.datos_imagenes]:
            nombre = os.path.splitext(os.path.basename(ruta))[0]
            gui.datos_imagenes.append({"ruta": ruta, "nombre": nombre})


    gui.redibujar_imagenes()
    gui.actualizar_estado()


#Sub-Funciones de redibujar imagenes en interfaz, creada para editar el nombre

def activar_edicion_nombre(event, frame, datos_imagen, idx):
    event.widget.destroy()

    entry = tk.Entry(frame, justify="center", width=18)
    entry.insert(0, datos_imagen["nombre"])
    entry.pack(pady=(2, 0))
    entry.focus_set()

    entry.bind("<Return>", lambda e: guardar_nombre(entry, frame, datos_imagen, idx))
    entry.bind("<FocusOut>", lambda e: guardar_nombre(entry, frame, datos_imagen, idx))

def guardar_nombre(entry, frame, datos_imagen, idx):
    nuevo_nombre = entry.get().strip()
    if nuevo_nombre:
        datos_imagen["nombre"] = nuevo_nombre
    entry.destroy()
    mostrar_nombre(frame, datos_imagen, idx)

def mostrar_nombre(frame, datos_imagen, idx):
    lbl_nombre = tk.Label(
        frame,
        text=datos_imagen["nombre"],
        wraplength=150,
        justify="center",
        bg="#ffffff",
        font=("Arial", 9)
    )
    lbl_nombre.pack(pady=(2, 0))
    from gui.eventos import activar_edicion_nombre  # para evitar import circular al definir todo junto
    lbl_nombre.bind("<Button-1>", lambda e: activar_edicion_nombre(e, frame, datos_imagen, idx))


#selector de medidas
def actualizar_visibilidad_dpi(gui):
    if gui.unidad.get() == "cm":
        gui.label_dpi.pack(side="left", padx=(10, 2))
        gui.entry_dpi.pack(side="left")
    else:
        gui.label_dpi.pack_forget()
        gui.entry_dpi.pack_forget()



def redimensionar_lote(gui):
    unidad = gui.unidad.get()
    dpi = int(gui.entry_dpi.get()) if unidad == "cm" else 96  # fallback si no está usando cm

    ancho_val = gui.entry_ancho.get().strip()
    alto_val = gui.entry_alto.get().strip()
    
    if not gui.datos_imagenes:
        messagebox.showinfo("Área vacía", "No hay imágenes cargadas para redimensionar.")
        return
    if not validar_dimension(ancho_val) or not validar_dimension(alto_val):
        print("Error: valores inválidos.")
        return

    ancho = float(ancho_val)
    alto = float(alto_val)

    if unidad == "cm":
        ancho = cm_a_px(ancho, dpi)
        alto = cm_a_px(alto, dpi)

    mantener = gui.bloquear_proporcion.get()
    foco = gui.entry_ancho if gui.entry_ancho.focus_get() else gui.entry_alto

    nuevas_imagenes = []
    for datos in gui.datos_imagenes:
        ruta = datos["ruta"]
        try:
            img = Image.open(ruta)
            original_w, original_h = img.size

            if mantener:
                if foco == gui.entry_ancho:
                    nuevo_ancho = int(ancho)
                    nuevo_alto = int(round(nuevo_ancho * original_h / original_w))
                else:
                    nuevo_alto = int(alto)
                    nuevo_ancho = int(round(nuevo_alto * original_w / original_h))
            else:
                nuevo_ancho = int(ancho)
                nuevo_alto = int(alto)

            img = img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
            datos["imagen_redimensionada"] = img  # Guardamos redimensionada en memoria

        except FileNotFoundError:
            print(f"⚠️ Archivo no encontrado: {ruta}")
            nombre = os.path.basename(ruta)
            messagebox.showwarning("Imagen no encontrada", f"La imagen '{nombre}' ya no se encuentra en su ubicación original.")
        except Exception as e:
            print(f"Error redimensionando {ruta}: {e}")

    print("Redimensionamiento completo.")