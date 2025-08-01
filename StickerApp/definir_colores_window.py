def centrar_ventana(win, parent=None):
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    if parent and parent.winfo_ismapped():
        x = parent.winfo_rootx() + (parent.winfo_width()//2) - (w//2)
        y = parent.winfo_rooty() + (parent.winfo_height()//2) - (h//2)
    else:
        x = win.winfo_screenwidth()//2 - w//2
        y = win.winfo_screenheight()//2 - h//2
    win.geometry(f'+{x}+{y}')
import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox

class DefinirColoresWindow(tk.Toplevel):
    def __init__(self, master, colores_nuevos, callback_guardar):
        super().__init__(master)
        self.title('Definir nuevos colores')
        self.colores_nuevos = sorted(colores_nuevos, key=lambda x: x.upper())
        self.callback_guardar = callback_guardar
        self.resultado = {}
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.transient(master)
        self.grab_set()
        self.focus_set()

        # --- Centrar respecto a ventana padre ---
        w, h = 420, min(500, 60 + 50*len(colores_nuevos))
        self.geometry(f'{w}x{h}')
        centrar_ventana(self, master)

        tk.Label(self, text='Define el color para cada nombre detectado:', font=('Arial', 11, 'bold')).pack(pady=(14,8))

        # --- Buscador de colores ---
        buscador_frame = tk.Frame(self)
        buscador_frame.pack(fill='x', padx=10, pady=(0,2))
        tk.Label(buscador_frame, text='🔍', font=('Arial', 11)).pack(side='left', padx=(0,2))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(buscador_frame, textvariable=self.search_var, width=18, font=('Arial', 11))
        search_entry.pack(side='left', fill='x', expand=True)

        # --- Scrollable frame ---
        container = tk.Frame(self)
        container.pack(expand=True, fill='both', padx=10, pady=0)
        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        vscroll = tk.Scrollbar(container, orient='vertical', command=canvas.yview, width=18, relief='flat', bd=0, troughcolor='#e0e0e0', bg='#bdbdbd', activebackground='#888888', highlightthickness=0)
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        canvas.create_window((0,0), window=self.scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.pack(side='left', fill='both', expand=True)
        vscroll.pack(side='right', fill='y')

        # Permitir scroll con la rueda del mouse SOLO en el canvas de esta ventana
        def _on_mousewheel(event):
            if event.num == 5 or event.delta == -120:
                canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta == 120:
                canvas.yview_scroll(-1, "units")
        # Windows y Mac
        canvas.bind('<MouseWheel>', _on_mousewheel)
        # Linux
        canvas.bind('<Button-4>', _on_mousewheel)
        canvas.bind('<Button-5>', _on_mousewheel)

        # --- Filtrado dinámico del listado de colores ---
        self.filas_colores = {}
        def actualizar_listado(*args):
            filtro = self.search_var.get().strip().lower()
            for color in list(self.filas_colores.keys()):
                if color not in self.colores_nuevos:
                    self.filas_colores[color].grid_remove()
                    self.filas_colores.pop(color)
                    continue
                fila = self.filas_colores[color]
                if not filtro or filtro in color.lower():
                    fila.grid()
                else:
                    fila.grid_remove()
        self.search_var.trace_add('write', actualizar_listado)

        # --- Centrado vertical/horizontal de los elementos ---
        self.scrollable_frame.grid_rowconfigure(tuple(range(len(colores_nuevos))), weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.entries = {}
        from PIL import Image, ImageTk
        import os
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icons', 'pincel.png')
        borrar_path = os.path.join(os.path.dirname(__file__), 'assets', 'icons', 'borrar.png')
        pincel_img = None
        borrar_img = None
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            img = img.resize((22, 22), Image.LANCZOS)
            pincel_img = ImageTk.PhotoImage(img)
        if os.path.exists(borrar_path):
            img = Image.open(borrar_path)
            img = img.resize((22, 22), Image.LANCZOS)
            borrar_img = ImageTk.PhotoImage(img)
        for i, color in enumerate(self.colores_nuevos):
            fila = tk.Frame(self.scrollable_frame)
            fila.grid(row=i, column=0, pady=6, padx=10, sticky='nsew')
            fila.grid_columnconfigure((0,1,2,3), weight=1)
            fila.grid_rowconfigure(0, weight=1)
            # Centrado horizontal y vertical usando grid
            lbl = tk.Label(fila, text=color, width=18, anchor='center')
            lbl.grid(row=0, column=0, padx=(0,8), sticky='nsew')
            if pincel_img:
                btn = tk.Button(fila, image=pincel_img, command=lambda c=color: self.elegir_color(c))
                btn.image = pincel_img
            else:
                btn = tk.Button(fila, text='🎨', command=lambda c=color: self.elegir_color(c))
            btn.grid(row=0, column=1, padx=5, sticky='nsew')
            color_preview = tk.Label(fila, text='      ', bg='#888888', relief='groove')
            color_preview.grid(row=0, column=2, padx=5, sticky='nsew')
            # Botón borrar
            def borrar_color(c=color):
                if messagebox.askyesno('Borrar color', f'¿Seguro que deseas borrar el color "{c}"?'):
                    if c in self.colores_nuevos:
                        self.colores_nuevos.remove(c)
                    self.entries.pop(c, None)
                    self.filas_colores[c].grid_remove()
                    self.filas_colores.pop(c, None)
                    actualizar_listado()
            if borrar_img:
                btn_borrar = tk.Button(fila, image=borrar_img, command=borrar_color, relief='flat', bd=0)
                btn_borrar.image = borrar_img
            else:
                btn_borrar = tk.Button(fila, text='🗑️', command=borrar_color, relief='flat', bd=0)
            btn_borrar.grid(row=0, column=3, padx=5, sticky='nsew')
            self.entries[color] = {'btn': btn, 'preview': color_preview, 'hex': None}
            self.filas_colores[color] = fila

        self.btn_guardar = tk.Button(self, text='Guardar', command=self.guardar_colores, state='disabled')
        self.btn_guardar.pack(pady=(8,4), fill='x', expand=True)

        # --- Forzar foco y bloqueo hasta guardar ---
        self.wait_visibility()
        self.focus()
        self.lift()
        self.grab_set()
        self.saved = False

    def elegir_color(self, color):
        rgb, hexcolor = colorchooser.askcolor(title=f'Selecciona el color para {color}', parent=self)
        if hexcolor:
            self.entries[color]['hex'] = hexcolor
            self.entries[color]['preview'].config(bg=hexcolor)
        self.verificar_completos()

    def verificar_completos(self):
        completos = all(self.entries[c]['hex'] for c in self.colores_nuevos)
        self.btn_guardar.config(state='normal' if completos else 'disabled')
        self.completos = completos

    def guardar_colores(self):
        for color in self.colores_nuevos:
            self.resultado[color] = self.entries[color]['hex']
        self.callback_guardar(self.resultado)
        self.saved = True
        self.grab_release()
        self.destroy()

    def on_close(self):
        # Solo bloquear si hay colores nuevos sin definir
        nuevos = [c for c in self.colores_nuevos if self.entries[c]['hex'] is None]
        if nuevos:
            messagebox.showwarning('Colores incompletos', 'Debes definir todos los colores nuevos antes de cerrar esta ventana.')
            self.focus()
            return
        # Si solo se editaron colores existentes, preguntar si desea guardar
        if not self.saved:
            if messagebox.askyesno('Guardar cambios', '¿Desea guardar los cambios en la paleta de colores?'):
                self.guardar_colores()
                return
        self.grab_release()
        self.destroy()
