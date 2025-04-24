#Seleccion multiple de imagenes en el Canva

from tkinter import Frame

imagenes_registradas = []
imagenes_seleccionadas = set()
ultima_seleccion = None

def registrar_imagen(label, ruta, gui):
    label.bind("<Button-1>", lambda event: _seleccionar(label, ruta, gui, event))
    imagenes_registradas.append((label, ruta))

def _seleccionar(label, ruta, gui, event):
    global ultima_seleccion

    if not label.winfo_exists():  # Verifica si el label aún existe
        return

    if event.state & 0x0004:  # Ctrl presionado
        if ruta in imagenes_seleccionadas:
            imagenes_seleccionadas.remove(ruta)
            label.config(highlightbackground="white", highlightthickness=0)
        else:
            imagenes_seleccionadas.add(ruta)
            label.config(highlightbackground="blue", highlightthickness=2)
        ultima_seleccion = ruta

    elif event.state & 0x0001:  # Shift presionado
        if ultima_seleccion is None:
            ultima_seleccion = ruta
            imagenes_seleccionadas.add(ruta)
            label.config(highlightbackground="blue", highlightthickness=2)
        else:
            _seleccionar_rango(ultima_seleccion, ruta)
            _actualizar_estilos()

    else:  # Selección simple
        imagenes_seleccionadas.clear()
        imagenes_seleccionadas.add(ruta)
        ultima_seleccion = ruta
        _actualizar_estilos()

def _seleccionar_rango(inicio_ruta, fin_ruta):
    indices = {ruta: i for i, (_, ruta) in enumerate(imagenes_registradas)}
    i1 = indices.get(inicio_ruta, 0)
    i2 = indices.get(fin_ruta, 0)
    i_min, i_max = sorted([i1, i2])

    imagenes_seleccionadas.clear()
    for i in range(i_min, i_max + 1):
        _, ruta = imagenes_registradas[i]
        imagenes_seleccionadas.add(ruta)

def _actualizar_estilos():
    for label, ruta in imagenes_registradas:
        if not label.winfo_exists():
            continue
        if ruta in imagenes_seleccionadas:
            label.config(highlightbackground="blue", highlightthickness=2)
        else:
            label.config(highlightbackground="white", highlightthickness=0)

def eliminar_seleccionadas(gui):
    global imagenes_registradas

    nuevas = []
    gui.datos_imagenes = [
    datos for datos in gui.datos_imagenes
    if datos["ruta"] not in imagenes_seleccionadas
]


    for label, ruta in imagenes_registradas:
        if ruta in imagenes_seleccionadas:
            try:
                label.destroy()
            except:
                pass
        else:
            nuevas.append((label, ruta))

    imagenes_registradas = nuevas
    imagenes_seleccionadas.clear()
    gui.redibujar_imagenes()
    gui.actualizar_estado()
