from tkinter import Tk
from ttkthemes import ThemedTk
from tkinter import ttk

app = ThemedTk(theme="arc")  # try 'arc', 'plastik', 'equilux', etc.
app.geometry("400x200")

entry = ttk.Entry(app)
entry.pack(pady=20)

button = ttk.Button(app, text="Submit")
button.pack()

app.mainloop()
