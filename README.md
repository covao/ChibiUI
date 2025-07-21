# ChibiUI

ChibiUI is a tiny Python GUI framework that makes it easy to build user interfaces with Tkinter. It wraps Tkinter so you can create scrollable, auto-layout GUIs with very little code.

## ✨ Features
- Lightweight wrapper for Tkinter
- Scrollable and auto layout
- Tree navigation with simple path syntax
- Minimal API, easy to use
- Headless mode for testing without a GUI

## 🚀 Quick Start
~~~python
from chibiui import chibiui
ui = chibiui("ChibiUI Example")
ui.add_textbox("Title", "Personal Data")

# Navigation tree items are created automatically from the path
ui.add_textbox("Person/Name", "John Doe")
ui.add_selector("Person/Gender", ["Male", "Female", "Other"], "Male")
ui.add_slider("Person/Age", 0, 100, 1, 30)
ui.add_checkbox("Person/Add File", True)
ui.add_browse_file("Person/Select File")
ui.add_button("Person/Submit", False)

ui.add_textbox("Option/Country", "Japan")

while ui.alive:
    if ui.get("Person/Submit"):
        print("Submit button pressed!")
        print("Title:", ui.get("Title"))
        print("-- Personal Info --")
        print("Name:", ui.get("Person/Name"))
        print("Gender:", ui.get("Person/Gender"))
        print("Age:", ui.get("Person/Age"))
        print("Select File:", ui.get("Person/Select File"))
        print("Country:", ui.get("Option/Country"))
        print("---")
        ui.set("/Person/Submit", False)
    # Prevent high CPU usage
    time.sleep(0.01)
print("End")
~~~


### Method Overview
- `chibiui(title, nogui=False)`: Create the UI. Set nogui=True for headless mode.
- `add_textbox(path, value)`: Add a text input field.
- `add_selector(path, options, value)`: Add a dropdown selector.
- `add_slider(path, min_val, max_val, step, value)`: Add a slider input.
- `add_checkbox(path, value)`: Add a checkbox.
- `add_browse_file(label)`: Add a file selection button and text field.
- `add_button(path, value)`: Add a button.
- `get(path)`: Get the value for a path.
- `set(path, value)`: Set the value for a path.
- `alive`: True if the UI is running.

![ChibiUI](ChibiUI.gif)
