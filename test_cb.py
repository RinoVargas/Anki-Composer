import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk()
cb = ttk.Combobox(root, values=["A", "B"])
cb.pack()

def test_unpost(e):
    try:
        root.tk.call('ttk::combobox::Unpost', cb._w)
        print("Unpost successful!")
    except Exception as exc:
        print("Error:", exc)

root.bind("<Configure>", test_unpost)
root.after(1000, lambda: root.destroy())
root.mainloop()
