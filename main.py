import tkinter as tk
from tkinter import Menu, messagebox
from gui.interfaz import RedimensionadorGUI


def crear_menu(root):
    barra_menu = Menu(root)

    menu_archivo = Menu(barra_menu, tearoff=0)
    menu_archivo.add_command(label="Guardar imágenes", command=lambda: messagebox.showinfo("Guardar", "Guardar no implementado aún"))
    menu_archivo.add_separator()
    menu_archivo.add_command(label="Salir", command=root.quit)

    barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

    root.config(menu=barra_menu)


def main():
    root = tk.Tk()
    root.title("Pictcionar V2")


    ancho = 840
    alto = 580
    root.withdraw()
    root.update_idletasks()
    x = (root.winfo_screenwidth() - ancho) // 2
    y = (root.winfo_screenheight() - alto) // 2
    root.geometry(f"{ancho}x{alto}+{x}+{y}")
    root.deiconify()
    root.minsize(ancho, alto)

    crear_menu(root)

    app = RedimensionadorGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()
