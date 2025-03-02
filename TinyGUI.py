import tkinter as tk
from tkinter import ttk, filedialog
import threading

class TinyGUI:
    """
    A simple GUI framework using Tkinter with scrollable support.
    This class creates a GUI in a separate thread and provides methods to add various UI elements.
    """

    def __init__(self, title='TinyGUI'):
        """
        Initializes the TinyGUI application and starts the GUI thread.

        :param title: Title of the GUI window.
        """
        self.title = title
        self.value = {}
        self.gui_ready = threading.Event()
        # Start the GUI thread (non-daemon so that the GUI persists after the main thread ends)
        self.thread = threading.Thread(target=self.create_gui)
        self.thread.start()
        self.gui_ready.wait()  # Wait until GUI initialization is complete

    def create_gui(self):
        """
        Creates the main GUI window, initializes its components, and starts the event loop.
        """
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close_gui)  # Set close event handler
        self.root.title(self.title)
        self.alive = True

        # Create a canvas and a scrollbar for scrollable content
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure the scrollable frame's scrolling region
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Create a window within the canvas to hold the scrollable frame
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar into the main window
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.gui_ready.set()  # Notify that GUI initialization is complete
        self.root.mainloop()

    def close_gui(self):
        """
        Closes the GUI window.
        """
        self.alive = False
        self.root.destroy()  # Properly destroy the GUI window

    def add_browse_file(self, label):
        """
        Adds a file selection button with an associated text field to the GUI.

        :param label: Label for the file selector.
        """
        def _add_browse_file():
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(pady=5, fill=tk.X)
            tk.Label(frame, text=label).pack(side=tk.LEFT)
            var = tk.StringVar(master=self.root)
            entry = tk.Entry(frame, textvariable=var)
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            button = tk.Button(frame, text="Browse", command=lambda: var.set(filedialog.askopenfilename()))
            button.pack(side=tk.RIGHT)
            self.value[label] = var
        self.root.after(0, _add_browse_file)

    def add_textbox(self, label, variable):
        """
        Adds a textbox with a label to the GUI.

        :param label: Label for the textbox.
        :param variable: Default text for the textbox.
        """
        def _add_textbox():
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(pady=5, fill=tk.X)
            tk.Label(frame, text=label).pack(side=tk.LEFT)
            entry_var = tk.StringVar(master=self.root, value=variable)
            entry = tk.Entry(frame, textvariable=entry_var)
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            self.value[label] = entry_var
        self.root.after(0, _add_textbox)

    def add_selector(self, label, options, variable):
        """
        Adds a dropdown selector (combobox) to the GUI.

        :param label: Label for the selector.
        :param options: List of options for selection.
        :param variable: Default selected value.
        """
        def _add_selector():
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(pady=5, fill=tk.X)
            tk.Label(frame, text=label).pack(side=tk.LEFT)
            var = tk.StringVar(master=self.root, value=variable)
            dropdown = ttk.Combobox(frame, textvariable=var, values=options)
            dropdown.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            self.value[label] = var
        self.root.after(0, _add_selector)

    def add_slider(self, label, min_val, max_val, step, variable):
        """
        Adds a slider with an associated spinbox to the GUI.

        :param label: Label for the slider.
        :param min_val: Minimum value of the slider.
        :param max_val: Maximum value of the slider.
        :param step: Step increment for the slider.
        :param variable: Default value for the slider.
        """
        def _add_slider():
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(pady=5, fill=tk.X)
            tk.Label(frame, text=label).pack(side=tk.LEFT)
            var = tk.DoubleVar(master=self.root, value=variable)
            slider = tk.Scale(frame, from_=min_val, to=max_val, resolution=step, orient=tk.HORIZONTAL, variable=var)
            slider.pack(side=tk.LEFT, expand=True, fill=tk.X)
            spinbox = tk.Spinbox(frame, from_=min_val, to=max_val, increment=step, textvariable=var, width=5)
            spinbox.pack(side=tk.RIGHT)
            self.value[label] = var
        self.root.after(0, _add_slider)

    def add_checkbox(self, label, variable):
        """
        Adds a checkbox to the GUI.

        :param label: Label for the checkbox.
        :param variable: Default boolean value for the checkbox.
        """
        def _add_checkbox():
            var = tk.BooleanVar(master=self.root, value=variable)
            check = tk.Checkbutton(self.scrollable_frame, text=label, variable=var)
            check.pack(anchor='w')
            self.value[label] = var
        self.root.after(0, _add_checkbox)

    def add_button(self, label, command):
        """
        Adds a button to the GUI.

        :param label: Label for the button.
        :param command: Function to execute when the button is clicked.
        """
        def _add_button():
            var = tk.BooleanVar(master=self.root, value=False)
            # When the button is clicked, set the BooleanVar to True and execute the command.
            button = tk.Button(self.scrollable_frame, text=label, command=lambda: var.set(True) or command())
            button.pack(pady=5)
            self.value[label] = var
        self.root.after(0, _add_button)

    def get_values(self):
        """
        Retrieves all values from the GUI's Tkinter variables.

        :return: Dictionary mapping element labels to their current values.
        """
        return {key: var.get() for key, var in self.value.items() 
                if isinstance(var, (tk.StringVar, tk.DoubleVar, tk.BooleanVar))}

if __name__ == "__main__":
    gui = TinyGUI("Sample TinyGUI")
    gui.add_textbox("Name", "John Doe")
    gui.add_selector("Gender", ["Male", "Female", "Other"], "Male")
    gui.add_slider("Age", 0, 100, 1, 30)
    gui.add_checkbox("Subscribe", True)
    gui.add_browse_file("Select File")
    gui.add_button("Submit", lambda: None)  # Button sets a BooleanVar to True when clicked

    # Main loop to check for the submit button press and retrieve GUI values
    while gui.alive:
        if "Submit" in gui.value and gui.value["Submit"].get():
            print(gui.get_values())
            gui.value["Submit"].set(False)
    print('End')
