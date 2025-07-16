# ChibiUI

ChibiUI is a tiny GUI framework that sits on top of Python’s built‑in Tkinter. Just copy a single file (ChibiUI.py) into your project and you’ll have a modern window with tree‑style navigation and a handy set of widgets—no event‑loop boilerplate needed.

✨ Features
- Data‑entry forms and parameter dialogs
- Lightweight GUI wrappers around CLI tools
- Tree Navigation
- Tkinter ships with Python; no extra packages required.


## 🚀 Quick Start
~~~ python
from ChibiUI import ChibiUI
ui = ChibiUI("ChibiUI Example")

# Root level widgets
ui.add_textbox("Main", "Welcome to ChibiUI")

# Navigation tree items are automatically created from the path
ui.add_textbox("Person1/Name", "John Doe")
ui.add_selector("Person1/Gender", ["Male", "Female", "Other"], "Male")
ui.add_slider("Person1/Age", 0, 100, 1, 30)
ui.add_checkbox("Person1/Subscribe", True)
ui.add_browse_file("Person1/Select File")
ui.add_button("Person1/Submit", False)

ui.add_textbox("Person2/Name", "Michel Lee")
ui.add_selector("Person2/Gender", ["Male", "Female", "Other"], "Female")


while ui.alive:
    # Check if the Submit button is pressed,print person's info
    if ui.value["/Person1/Submit"].get():
        print("Person 1 Info:")
        print("Name:", ui.value["/Person1/Name"].get())
        print("Gender:", ui.value["/Person1/Gender"].get())
        print("Age:", ui.value["/Person1/Age"].get())
        print("Subscribe:", ui.value["/Person1/Subscribe"].get())
        print("Select File:", ui.value["/Person1/Select File"].get())
        ui.value["/Person1/Submit"].set(False)
        print("---")

    import time
    time.sleep(0.1)  # Add a small delay to avoid excessive CPU usage

print('End')
~~~ 
![ChibiUI](ChibiUI.gif)
