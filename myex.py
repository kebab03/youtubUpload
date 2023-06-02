import tkinter as tk
import datetime
import pyautogui
import voice_for_file as v2tx
root = tk.Tk()
def key_pressed(event):
 if event.char == "d":
     date = datetime.datetime.now()
     filename = str(date).replace(":", "-")
     filem =filename.split(".")[0]


     v2tx.speak('wher should i save ')
     folder = v2tx.myCommand().lower()
     if "machine" in folder:
             myScreenshot = pyautogui.screenshot()

             myScreenshot.save(r'C:\\Users\\leeon\\Desktop\\New folder (2)\\'+filem+'screenshot.png')
             #'C:\\Users\\leeon\\Desktop\\New folder (2)\\'+filem+'screenshot.png')
             print(event.char)

root.bind("<Key>",key_pressed)
root.mainloop()
