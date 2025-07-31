import tkinter as tk
from tkinter import ttk

class TablaView:
    def vaciar(self):
        self.tree.delete(*self.tree.get_children())
    def __init__(self, parent):
        # --- Definir columnas por defecto usando el header del CSV proporcionado, pero con números del 21 al 42 ---
        self.default_columns = [
            'N° ORDEN', 'CLIENTE', 'CÓDIGO', 'COLOR', 'MARCA', 'CAPELLADA', 'FORRO', 'SUELA'
        ] + [str(n) for n in range(21, 43)] + ['TOTAL']

        self.frame = tk.Frame(parent)
        self.frame.pack(expand=True, fill='both')

        self.tree = ttk.Treeview(self.frame, columns=self.default_columns, show='headings')

        # Scrollbars
        vsb = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        # Asignar ancho menor y centrado a las columnas numéricas
        numeric_cols = {str(n) for n in range(21, 43)}
        small_width = 40
        normal_width = 80
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), background='#e0e0e0', foreground='#222')

        for col in self.default_columns:
            if col in numeric_cols:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=small_width, anchor='center')
            else:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=normal_width, anchor='center')

    def mostrar_datos(self, df):
        self.tree.delete(*self.tree.get_children())
        numeric_cols = {str(n) for n in range(21, 43)}
        small_width = 40
        normal_width = 80
        self.tree['columns'] = list(df.columns)
        self.tree['show'] = 'headings'
        for col in df.columns:
            if col in numeric_cols:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=small_width, anchor='center')
            else:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=normal_width, anchor='center')
        for _, row in df.iterrows():
            self.tree.insert('', 'end', values=list(row))

        # --- Footer de sumas ---
        # Solo si hay filas
        if not df.empty:
            sumas = []
            for col in df.columns:
                if col in numeric_cols or col == 'TOTAL':
                    try:
                        suma = df[col].astype(float).sum()
                        suma = int(suma) if suma == int(suma) else round(suma, 2)
                        sumas.append(suma)
                    except Exception:
                        sumas.append('')
                else:
                    sumas.append('')
            # Insertar como última fila, con estilo diferente si se desea
            self.tree.insert('', 'end', values=sumas, tags=('footer',))
            self.tree.tag_configure(
                'footer',
                background='#b6d7a8',  # verde suave
                font=('Arial', 10, 'bold'),
                foreground='#222'
            )

    def get_frame(self):
        return self.frame
    
    def get_tree(self):
        return self.tree
