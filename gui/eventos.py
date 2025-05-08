from tkinter import filedialog, Entry, Label, messagebox
import tkinter as tk
import os

 
from PIL import Image, ImageTk
from gui.seleccion import registrar_imagen
from gui.conversion import cm_a_px, validar_dimension
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



#def ajustar_proporcion(gui):
#   if not gui.datos_imagenes:
#        return

#    if not gui.bloquear_proporcion.get():
 #       return  # Si no está tildado, no hacemos nada

    # Tomamos la proporción de la primera imagen cargada
  #  ruta = gui.datos_imagenes[0]["ruta"]
  #  try:
   #     from PIL import Image
   #     img = Image.open(ruta)
  #      original_w, original_h = img.size
   #     ratio = original_w / original_h
   # except:
   #     return

  #  foco = gui.master.focus_get()

   # try:
  #      if foco == gui.entry_ancho:
   #         ancho = float(gui.entry_ancho.get())
   #         alto = round(ancho / ratio)
  #         gui.entry_alto.delete(0, "end")
   #         gui.entry_alto.insert(0, str(alto))
    #    elif foco == gui.entry_alto:
   #         alto = float(gui.entry_alto.get())
    #        ancho = round(alto * ratio)
   #         gui.entry_ancho.delete(0, "end")
  ##          gui.entry_ancho.insert(0, str(ancho))
   # except ValueError:
   #     pass  # Si el valor ingresado no es válido (ej: vacío o texto), no hacemos nada


def detectar_cantidad_y_aplicar_comportamiento(gui, campo_modificado):
    if not gui.datos_imagenes or not gui.bloquear_proporcion.get():
        return

    if len(gui.datos_imagenes) == 1:
        modo_imagen_unica(gui, campo_modificado)
    else:
        modo_lote_multiple(gui, campo_modificado)


from PIL import Image

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
    texto = f"""Cuando seleccionás un lote de imágenes con la opción “Mantener proporciones” activada,
el campo {campo} se calculará automáticamente según el tamaño original de cada imagen."""

    from tkinter import Toplevel, Label, Button, Checkbutton, IntVar

    ventana = Toplevel(gui.master)
    ventana.title("Atención")
    ventana.resizable(False, False)
    ventana.transient(gui.master)
    ventana.grab_set()

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


    
def guardar_imagenes_redimensionadas(gui):
    if not gui.datos_imagenes:
        messagebox.showwarning("Sin imágenes", "No hay imágenes para guardar.")
        return

    carpeta_destino = filedialog.askdirectory(title="Seleccionar carpeta de destino")
    if not carpeta_destino:
        return

    try:
        ancho = float(gui.entry_ancho.get())
        alto = float(gui.entry_alto.get())
    except ValueError:
        messagebox.showerror("Error", "Medidas inválidas.")
        return

    usar_cm = gui.unidad.get() == "cm"
    dpi = 150
    try:
        if usar_cm:
            dpi = float(gui.entry_dpi.get())
            ancho = int((ancho / 2.54) * dpi)
            alto = int((alto / 2.54) * dpi)
        else:
            ancho = int(ancho)
            alto = int(alto)
    except:
        messagebox.showerror("Error", "DPI o dimensiones incorrectas.")
        return

    nombres_usados = set()

    for datos in gui.datos_imagenes:
        ruta_original = datos["ruta"]
        nombre_base = datos.get("nombre", os.path.splitext(os.path.basename(ruta_original))[0])
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

    messagebox.showinfo("Completado", "Todas las imágenes fueron guardadas.")
