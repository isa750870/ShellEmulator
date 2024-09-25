import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

class ShellGUI:
    def __init__(self, root, command_callback):
        self.root = root
        self.root.title("Эмулятор оболочки ОС")
        self.command_callback = command_callback

        # Текстовое поле для вывода
        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=25, width=100, state='disabled')
        self.output_area.pack(padx=10, pady=10)

        # Поле ввода команд
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(padx=10, pady=(0,10))

        self.input_label = tk.Label(self.input_frame, text="$ ")
        self.input_label.pack(side=tk.LEFT)

        self.command_entry = tk.Entry(self.input_frame, width=80)
        self.command_entry.pack(side=tk.LEFT, padx=(5,0))
        self.command_entry.bind("<Return>", self.on_enter)

    def on_enter(self, event):
        command = self.command_entry.get()
        self.append_output(f"$ {command}\n")
        self.command_entry.delete(0, tk.END)
        try:
            response = self.command_callback(command)
            if response:
                self.append_output(response + "\n")
        except Exception as e:
            self.append_output(f"Ошибка: {str(e)}\n")

    def append_output(self, text):
        self.output_area.configure(state='normal')
        self.output_area.insert(tk.END, text)
        self.output_area.configure(state='disabled')
        self.output_area.see(tk.END)

    def start(self):
        self.root.mainloop()