def activar_scroll(canvas, master):
    def _on_mousewheel(event):
        # Windows y macOS: scroll vertical
        if event.state & 0x1:  # Shift presionado
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_linux_scroll_up(event):
        canvas.yview_scroll(-1, "units")

    def _on_linux_scroll_down(event):
        canvas.yview_scroll(1, "units")

    def _on_linux_scroll_left(event):
        canvas.xview_scroll(-1, "units")

    def _on_linux_scroll_right(event):
        canvas.xview_scroll(1, "units")

    # Windows / macOS (event.delta)
    master.bind_all("<MouseWheel>", _on_mousewheel)

    # Linux (event.button)
    master.bind_all("<Button-4>", _on_linux_scroll_up)
    master.bind_all("<Button-5>", _on_linux_scroll_down)
    master.bind_all("<Shift-Button-4>", _on_linux_scroll_left)
    master.bind_all("<Shift-Button-5>", _on_linux_scroll_right)
