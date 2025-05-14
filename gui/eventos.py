from tkinter import filedialog, Entry, messagebox



import tkinter as tk
import os

from core.renombrador import guardar_nombre, mostrar_nombre

from PIL import Image, ImageTk
from gui.seleccion import registrar_imagen
from core.conversion import cm_a_px, validar_dimension
mostrar_aviso_lote = True



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
    
    mantener = gui.bloquear_proporcion.get()
    print("estado ancho:", gui.entry_ancho.cget("state"))
    print("estado alto:", gui.entry_alto.cget("state"))
    if not ancho_val:
        foco = gui.entry_alto
    else:
        foco = gui.entry_ancho


    if mantener:
        if foco == gui.entry_ancho and not validar_dimension(ancho_val):
            print("Error: valores inválidos.")
            return
        elif foco == gui.entry_alto and not validar_dimension(alto_val):
            print("Error: valores inválidos.")
            return
    else:
        if not validar_dimension(ancho_val) or not validar_dimension(alto_val):
            print("Error: valores inválidos.")
            return

    if mantener:
        if foco == gui.entry_ancho:
            ancho = float(ancho_val)
            if unidad == "cm":
                ancho = cm_a_px(ancho, dpi)
        else:
            alto = float(alto_val)
            if unidad == "cm":
                alto = cm_a_px(alto, dpi)
    else:
        ancho = float(ancho_val)
        alto = float(alto_val)
        if unidad == "cm":
            ancho = cm_a_px(ancho, dpi)
            alto = cm_a_px(alto, dpi)



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



def detectar_cantidad_y_aplicar_comportamiento(gui, campo_modificado):
    if not gui.datos_imagenes or not gui.bloquear_proporcion.get():
        return

    if len(gui.datos_imagenes) == 1:
        modo_imagen_unica(gui, campo_modificado)
    else:
        modo_lote_multiple(gui, campo_modificado)



def modo_imagen_unica(gui, campo_modificado):
    ruta = gui.datos_imagenes[0]["ruta"]
    try:
        img = Image.open(ruta)
        w, h = img.size
        ratio = w / h

        if campo_modificado == "ancho":
            ancho = float(gui.entry_ancho.get())
            alto = round(ancho / ratio)
            gui.entry_alto.config(bg="white")
            gui.entry_alto.delete(0, "end")
            gui.entry_alto.insert(0, str(alto))
        elif campo_modificado == "alto":
            alto = float(gui.entry_alto.get())
            ancho = round(alto * ratio)
            gui.entry_ancho.config(bg="white")
            gui.entry_ancho.delete(0, "end")
            gui.entry_ancho.insert(0, str(ancho))
    except:
        pass  # por si el valor es inválido o la imagen no se abre


def modo_lote_multiple(gui, campo_modificado):
    if campo_modificado == "ancho":
        otro = gui.entry_alto
    else:
        otro = gui.entry_ancho

    otro.delete(0, "end")
    otro.config(bg="#eeeeee")

    # 👉 Llamamos la función de mensaje aparte
    mostrar_aviso_lote_si_corresponde(gui, campo_modificado)


def mostrar_aviso_lote_si_corresponde(gui, campo_modificado):
    global mostrar_aviso_lote
    if not mostrar_aviso_lote:
        return

    campo = "ancho" if campo_modificado == "alto" else "alto"
    texto = f"""“Mantener proporciones” modifica automaticamente el {campo} segun el tamaño original de cada imagen."""

    from tkinter import Toplevel, Label, Button, Checkbutton, IntVar

    ventana = Toplevel(gui.master)
    ventana.title("Atención")
    ventana.resizable(False, False)
    ventana.transient(gui.master)
    ventana.grab_set()
    ventana.focus_force()
    ventana.lift()


    # CENTRAR VENTANA respecto al master
    ventana.update_idletasks()
    x = gui.master.winfo_rootx() + (gui.master.winfo_width() // 2) - 200
    y = gui.master.winfo_rooty() + (gui.master.winfo_height() // 2) - 80
    ventana.geometry(f"400x160+{x}+{y}")

    Label(ventana, text=texto, wraplength=370, justify="left", anchor="w").pack(pady=(15, 10), padx=10)

    no_mostrar_var = IntVar(value=0)
    Checkbutton(ventana, text="No volver a mostrar este mensaje", variable=no_mostrar_var).pack(anchor="w", padx=12)

    def cerrar():
        if no_mostrar_var.get():
            global mostrar_aviso_lote
            mostrar_aviso_lote = False
        ventana.destroy()

    Button(ventana, text="Aceptar", command=cerrar, width=12).pack(pady=(10, 12))


