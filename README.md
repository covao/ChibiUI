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

# --- Build page /Person1 ---
ui.add_navigation('/Person1')
ui.add_textbox("Name", "John Doe")
ui.add_selector("Gender", ["Male", "Female", "Other"], "Male")
ui.add_slider("Age", 0, 100, 1, 30)
ui.add_checkbox("Subscribe", True)
ui.add_browse_file("Select File")
ui.add_button("Submit")

# --- Build page /Person2 ---
ui.add_navigation('/Person2')
ui.add_textbox("Name", "Michelle Lee")
ui.add_selector("Gender", ["Male", "Female", "Other"], "Female")

# Main logic
while ui.alive:
    if ui.value["/Person1/Submit"].get():
        print("Person 1 Info →")
        print("  Name:", ui.value["/Person1/Name"].get())
        print("  Gender:", ui.value["/Person1/Gender"].get())
        print("  Age:", ui.value["/Person1/Age"].get())
        print("  Subscribe:", ui.value["/Person1/Subscribe"].get())
        print("  File:", ui.value["/Person1/Select File"].get())
        ui.value["/Person1/Submit"].set(False)  # reset
~~~ 

