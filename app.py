import tkinter as tk
import m_scenes
import database as db


window = tk.Tk()
window.title("Music App - Admin")

scene1 = m_scenes.MenuScene(
   master=window
)
scene1.pack()

window.mainloop()