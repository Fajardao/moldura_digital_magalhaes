import tkinter as tk

tk.TkVersion  # Accessing Tkinter version to ensure the module is loaded correctly

m = tk.Tk()
m.title("Teste GUI")
m.geometry("300x200")
label = tk.Label(m, text="Teste de GUI com Tkinter")
label.pack(pady=20)

m.mainloop()

