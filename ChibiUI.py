import tkinter as tk
from tkinter import ttk, filedialog
import threading
import os

class ChibiUI:
    """
    ChibiUI is a simple GUI framework built using Tkinter. It provides methods to create various UI elements and manage navigation paths.

    Methods:
    - __init__(title): Initializes the GUI framework and starts the main thread.
    - create_ui(): Creates the main GUI window and starts the Tkinter event loop.
    - show_content(path): Displays the content for the specified navigation path.
    - add_textbox(label, variable): Adds a textbox widget with a label.
    - add_selector(label, options, variable): Adds a dropdown selector widget.
    - add_slider(label, min_val, max_val, step, variable): Adds a slider widget with a spinbox.
    - add_checkbox(label, variable): Adds a checkbox widget.
    - add_browse_file(label): Adds a file selection widget.
    - add_button(label, value): Adds a button widget.

    Button Usage:
    - Buttons are linked to BooleanVar values. When clicked, the value is set to True.
    - The while loop in the example checks if the button's value is True, performs actions, and resets the value to False.

    Example Main Function:
    - The main function demonstrates how to use the ChibiUI class.
    - It creates navigation paths and adds various widgets like textboxes, sliders, and buttons.
    - The while loop monitors button clicks and prints the corresponding data to the console.
    """

    def close_ui(self):
        """
        Closes the UI window and terminates the application.
        """
        if self.root:
            self.root.quit()
        self.alive = False


    def __init__(self, title='ChibiUI'):
        """
        Initializes the ChibiUI application and starts the GUI thread.

        :param title: Title of the GUI window.
        """
        self.title = title
        self.value = {}
        self.navigation_tree = {}
        self.current_path = '/'
        self.alive = False
        self.root = None
        self.thread = threading.Thread(target=self.create_ui, daemon=True)
        self.thread.start()
        while not self.alive:
            pass

    def __del__(self):
        """
        Destructor method to ensure proper cleanup when the object is destroyed.
        """
        if self.alive:
            self.close_ui()

    def create_ui(self):
        """
        Creates the main GUI window, initializes its components, and starts the event loop.
        """
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close_ui)
        self.root.title(self.title)

        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        nav_frame = tk.Frame(main_paned)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.nav_tree = ttk.Treeview(nav_frame, show='tree')
        self.nav_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.nav_tree.insert('', 'end', '/', text='Root', open=True)
        
        self.nav_tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        content_frame = tk.Frame(main_paned)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(content_frame)
        self.scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        main_paned.add(nav_frame, width=200)
        main_paned.add(content_frame)

        self.navigation_tree['/'] = {'frame': self.scrollable_frame, 'widgets': []}
        
        # Set initial selection to root
        self.nav_tree.selection_set('/')
        self.nav_tree.focus('/')
        self.current_path = '/'

        self.alive = True
        
        # Initialize root content display
        self.root.after(100, lambda: self.show_content('/'))
        
        self.root.mainloop()

    def add_navigation(self, path):
        """
        Adds a new navigation path to the tree and creates corresponding content frame.

        Args:
            path (str): Navigation path (e.g., '/Person1', '/Person/Profile')
        """
        def _add_navigation():
            parts = [p for p in path.split('/') if p]
            current_path = ''
            parent_id = '/'
            
            for part in parts:
                current_path += '/' + part
                
                if not self.nav_tree.exists(current_path):
                    self.nav_tree.insert(parent_id, 'end', current_path, text=part)
                    
                    content_frame = tk.Frame(self.canvas)
                    self.navigation_tree[current_path] = {'frame': content_frame, 'widgets': []}
                
                parent_id = current_path
            
            self.current_path = path
            self.show_content(path)
            
        if hasattr(self, 'root') and self.root:
            self.root.after(0, _add_navigation)

    def on_tree_select(self, event):
        """
        Handle tree selection events.
        
        Args:
            event: The tree selection event
        """
        selection = self.nav_tree.selection()
        if selection:
            selected_path = selection[0]
            if selected_path == '/':
                self.current_path = '/'
            else:
                self.current_path = selected_path
            self.show_content(self.current_path)

    def show_content(self, path):
        """
        Show content for the specified navigation path.

        Args:
            path (str): Navigation path to show content for
        """
        # Don't strip '/' from root path
        if path != '/':
            path = path.rstrip('/')
        
        if path not in self.navigation_tree:
            return
            
        for window_id in self.canvas.find_all():
            self.canvas.delete(window_id)
        
        content_frame = tk.Frame(self.canvas)
        self.navigation_tree[path]['frame'] = content_frame
        
        self.canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        self.scrollable_frame = content_frame
        
        if 'widgets' in self.navigation_tree[path]:
            for widget_info in self.navigation_tree[path]['widgets']:
                if widget_info['type'] == 'textbox':
                    full_key = f"{path}/{widget_info['label']}" if path != '/' else f"/{widget_info['label']}"
                    value = self.value[full_key].get() if full_key in self.value else widget_info['value']
                    self._create_textbox(widget_info['label'], value)
                elif widget_info['type'] == 'selector':
                    full_key = f"{path}/{widget_info['label']}" if path != '/' else f"/{widget_info['label']}"
                    value = self.value[full_key].get() if full_key in self.value else widget_info['value']
                    self._create_selector(widget_info['label'], widget_info['options'], value)
                elif widget_info['type'] == 'slider':
                    full_key = f"{path}/{widget_info['label']}" if path != '/' else f"/{widget_info['label']}"
                    value = self.value[full_key].get() if full_key in self.value else widget_info['value']
                    self._create_slider(widget_info['label'], widget_info['min_val'], widget_info['max_val'], widget_info['step'], value)
                elif widget_info['type'] == 'checkbox':
                    full_key = f"{path}/{widget_info['label']}" if path != '/' else f"/{widget_info['label']}"
                    value = self.value[full_key].get() if full_key in self.value else widget_info['value']
                    self._create_checkbox(widget_info['label'], value)
                elif widget_info['type'] == 'browse_file':
                    self._create_browse_file(widget_info['label'])
                elif widget_info['type'] == 'button':
                    full_key = f"{path}/{widget_info['label']}" if path != '/' else f"/{widget_info['label']}"
                    value = self.value[full_key].get() if full_key in self.value else widget_info['value']
                    self._create_button(widget_info['label'], value, widget_info)
        
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_current_frame(self):
        """
        Get the current content frame based on the current navigation path.

        Returns:
            tkinter.Frame: Current content frame
        """
        if self.current_path in self.navigation_tree:
            return self.navigation_tree[self.current_path]['frame']
        return self.scrollable_frame

    def add_browse_file(self, label):
        """
        Adds a file selection button with an associated text field to the GUI.

        Args:
            label (str): Label for the file selector (can include path like "Person1/Select File")
        """
        # Parse path from label
        if '/' in label:
            path_parts = label.split('/')
            path = '/' + '/'.join(path_parts[:-1])
            actual_label = path_parts[-1]
        else:
            path = '/'
            actual_label = label
        
        # Auto-create navigation tree if it doesn't exist
        self._auto_create_navigation(path)
        
        widget_info = {
            'type': 'browse_file',
            'label': actual_label
        }
        
        if path not in self.navigation_tree:
            self.navigation_tree[path] = {'frame': None, 'widgets': []}
        
        self.navigation_tree[path]['widgets'].append(widget_info)
        
        # Store value with full path for access
        full_key = f"{path}/{actual_label}" if path != '/' else f"/{actual_label}"
        self.value[full_key] = tk.StringVar(value="")
        
        def _add_browse_file():
            self._create_browse_file_at_path(path, actual_label)
            
        if hasattr(self, 'root') and self.root:
            self.root.after(0, _add_browse_file)

    def add_textbox(self, label, variable):
        """
        Adds a textbox with a label to the GUI.

        Args:
            label (str): Label for the textbox (can include path like "Person1/Name")
            variable (str): Default text for the textbox
        """
        # Parse path from label
        if '/' in label:
            path_parts = label.split('/')
            path = '/' + '/'.join(path_parts[:-1])
            actual_label = path_parts[-1]
        else:
            path = '/'
            actual_label = label
        
        # Auto-create navigation tree if it doesn't exist
        self._auto_create_navigation(path)
        
        # Check if widget already exists to prevent duplicates
        if path in self.navigation_tree:
            for existing_widget in self.navigation_tree[path]['widgets']:
                if existing_widget['type'] == 'textbox' and existing_widget['label'] == actual_label:
                    return  # Widget already exists, don't add duplicate
        
        widget_info = {
            'type': 'textbox',
            'label': actual_label,
            'value': variable
        }
        
        if path not in self.navigation_tree:
            self.navigation_tree[path] = {'frame': None, 'widgets': []}
        
        self.navigation_tree[path]['widgets'].append(widget_info)
        
        # Store value with full path for access
        full_key = f"{path}/{actual_label}" if path != '/' else f"/{actual_label}"
        if full_key not in self.value:
            self.value[full_key] = tk.StringVar(value=variable)
        
        def _add_textbox():
            self._create_textbox_at_path(path, actual_label, variable)
            
        if hasattr(self, 'root') and self.root:
            self.root.after(0, _add_textbox)

    def add_selector(self, label, options, variable):
        """
        Adds a dropdown selector (combobox) to the GUI.

        Args:
            label (str): Label for the selector (can include path like "Person1/Gender")
            options (list): List of options for selection
            variable (str): Default selected value
        """
        # Parse path from label
        if '/' in label:
            path_parts = label.split('/')
            path = '/' + '/'.join(path_parts[:-1])
            actual_label = path_parts[-1]
        else:
            path = '/'
            actual_label = label
        
        # Auto-create navigation tree if it doesn't exist
        self._auto_create_navigation(path)
        
        widget_info = {
            'type': 'selector',
            'label': actual_label,
            'options': options,
            'value': variable
        }
        
        if path not in self.navigation_tree:
            self.navigation_tree[path] = {'frame': None, 'widgets': []}
        
        self.navigation_tree[path]['widgets'].append(widget_info)
        
        # Store value with full path for access
        full_key = f"{path}/{actual_label}" if path != '/' else f"/{actual_label}"
        self.value[full_key] = tk.StringVar(value=variable)
        
        def _add_selector():
            self._create_selector_at_path(path, actual_label, options, variable)
            
        if hasattr(self, 'root') and self.root:
            self.root.after(0, _add_selector)

    def add_slider(self, label, min_val, max_val, step, variable):
        """
        Adds a slider with an associated spinbox to the GUI.

        Args:
            label (str): Label for the slider (can include path like "Person1/Age")
            min_val (float): Minimum value of the slider
            max_val (float): Maximum value of the slider
            step (float): Step increment for the slider
            variable (float): Default value for the slider
        """
        # Parse path from label
        if '/' in label:
            path_parts = label.split('/')
            path = '/' + '/'.join(path_parts[:-1])
            actual_label = path_parts[-1]
        else:
            path = '/'
            actual_label = label
        
        # Auto-create navigation tree if it doesn't exist
        self._auto_create_navigation(path)
        
        widget_info = {
            'type': 'slider',
            'label': actual_label,
            'min_val': min_val,
            'max_val': max_val,
            'step': step,
            'value': variable
        }
        
        if path not in self.navigation_tree:
            self.navigation_tree[path] = {'frame': None, 'widgets': []}
        
        self.navigation_tree[path]['widgets'].append(widget_info)
        
        # Store value with full path for access
        full_key = f"{path}/{actual_label}" if path != '/' else f"/{actual_label}"
        self.value[full_key] = tk.DoubleVar(value=variable)
        
        def _add_slider():
            self._create_slider_at_path(path, actual_label, min_val, max_val, step, variable)
            
        if hasattr(self, 'root') and self.root:
            self.root.after(0, _add_slider)

    def add_checkbox(self, label, variable):
        """
        Adds a checkbox to the GUI.

        Args:
            label (str): Label for the checkbox (can include path like "Person1/Subscribe")
            variable (bool): Default boolean value for the checkbox
        """
        # Parse path from label
        if '/' in label:
            path_parts = label.split('/')
            path = '/' + '/'.join(path_parts[:-1])
            actual_label = path_parts[-1]
        else:
            path = '/'
            actual_label = label
        
        # Auto-create navigation tree if it doesn't exist
        self._auto_create_navigation(path)
        
        widget_info = {
            'type': 'checkbox',
            'label': actual_label,
            'value': variable
        }
        
        if path not in self.navigation_tree:
            self.navigation_tree[path] = {'frame': None, 'widgets': []}
        
        self.navigation_tree[path]['widgets'].append(widget_info)
        
        # Store value with full path for access
        full_key = f"{path}/{actual_label}" if path != '/' else f"/{actual_label}"
        self.value[full_key] = tk.BooleanVar(value=variable)
        
        def _add_checkbox():
            self._create_checkbox_at_path(path, actual_label, variable)
            
        if hasattr(self, 'root') and self.root:
            self.root.after(0, _add_checkbox)

    def add_button(self, label, value=False):
        """
        Adds a button to the GUI.

        Args:
            label (str): Label for the button (can include path like "Person1/Submit")
            value (bool): Initial value for the button (default: False)
        """
        # Parse path from label
        if '/' in label:
            path_parts = label.split('/')
            path = '/' + '/'.join(path_parts[:-1])
            actual_label = path_parts[-1]
        else:
            path = '/'
            actual_label = label
        
        # Auto-create navigation tree if it doesn't exist
        self._auto_create_navigation(path)
        
        widget_info = {
            'type': 'button',
            'label': actual_label,
            'value': value,
        }
        
        if path not in self.navigation_tree:
            self.navigation_tree[path] = {'frame': None, 'widgets': []}
        
        self.navigation_tree[path]['widgets'].append(widget_info)
        
        # Store value with full path for access
        full_key = f"{path}/{actual_label}" if path != '/' else f"/{actual_label}"
        self.value[full_key] = tk.BooleanVar(value=value)
        
        def _add_button():
            self._create_button_at_path(path, actual_label, value, widget_info)
            
        if hasattr(self, 'root') and self.root:
            self.root.after(0, _add_button)

    def _recreate_widget(self, widget_info):
        """
        Recreate a widget based on stored information.
        
        Args:
            widget_info (dict): Dictionary containing widget information
        """
        widget_type = widget_info['type']
        
        if widget_type == 'textbox':
            self._create_textbox(widget_info['label'], widget_info['value'])
        elif widget_type == 'selector':
            self._create_selector(widget_info['label'], widget_info['options'], widget_info['value'])
        elif widget_type == 'slider':
            self._create_slider(widget_info['label'], widget_info['min_val'], 
                               widget_info['max_val'], widget_info['step'], widget_info['value'])
        elif widget_type == 'checkbox':
            self._create_checkbox(widget_info['label'], widget_info['value'])
        elif widget_type == 'browse_file':
            self._create_browse_file(widget_info['label'])
        elif widget_type == 'button':
            self._create_button(widget_info['label'], widget_info['value'], widget_info)

    def _auto_create_navigation(self, path):
        """
        Automatically creates navigation tree structure for the given path.
        
        Args:
            path (str): Navigation path to create (e.g., '/Person1' or '/Person1/Profile')
        """
        if path == '/':
            return
            
        parts = [p for p in path.split('/') if p]
        current_path = ''
        parent_id = '/'
        
        for part in parts:
            current_path += '/' + part
            
            # Create tree item if it doesn't exist
            if hasattr(self, 'nav_tree') and not self.nav_tree.exists(current_path):
                self.nav_tree.insert(parent_id, 'end', current_path, text=part)
            
            # Create navigation tree entry if it doesn't exist
            if current_path not in self.navigation_tree:
                content_frame = tk.Frame(self.canvas)
                self.navigation_tree[current_path] = {'frame': content_frame, 'widgets': []}
            
            parent_id = current_path

    def _create_textbox_at_path(self, path, label, variable):
        """
        Create textbox widget at specific path.
        
        Args:
            path (str): Navigation path
            label (str): Widget label
            variable (str): Widget value
        """
        if path == self.current_path:
            self._create_textbox(label, variable)

    def _create_textbox(self, label, value):
        """Create a textbox widget."""
        frame = tk.Frame(self.get_current_frame())
        frame.pack(pady=5, fill=tk.X)
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        
        # Use existing StringVar if available
        full_key = f"{self.current_path}/{label}" if self.current_path != '/' else f"/{label}"
        if full_key in self.value:
            entry_var = self.value[full_key]
        else:
            entry_var = tk.StringVar(master=self.root, value=value)
            self.value[full_key] = entry_var
            
        entry = tk.Entry(frame, textvariable=entry_var)
        entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)

    def _create_selector_at_path(self, path, label, options, variable):
        """
        Create selector widget at specific path.
        
        Args:
            path (str): Navigation path
            label (str): Widget label
            options (list): Selector options
            variable (str): Widget value
        """
        if path == self.current_path:
            self._create_selector(label, options, variable)

    def _create_selector(self, label, options, value):
        """Create a selector widget."""
        frame = tk.Frame(self.get_current_frame())
        frame.pack(pady=5, fill=tk.X)
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        var = tk.StringVar(master=self.root, value=value)
        dropdown = ttk.Combobox(frame, textvariable=var, values=options)
        dropdown.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        self.value[f"{self.current_path}/{label}"] = var

    def _create_slider_at_path(self, path, label, min_val, max_val, step, variable):
        """
        Create slider widget at specific path.
        
        Args:
            path (str): Navigation path
            label (str): Widget label
            min_val (float): Minimum value
            max_val (float): Maximum value
            step (float): Step value
            variable (float): Widget value
        """
        if path == self.current_path:
            self._create_slider(label, min_val, max_val, step, variable)

    def _create_slider(self, label, min_val, max_val, step, value):
        """Create a slider widget."""
        frame = tk.Frame(self.get_current_frame())
        frame.pack(pady=5, fill=tk.X)
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        var = tk.DoubleVar(master=self.root, value=value)
        slider = tk.Scale(frame, from_=min_val, to=max_val, resolution=step, orient=tk.HORIZONTAL, variable=var)
        slider.pack(side=tk.LEFT, expand=True, fill=tk.X)
        spinbox = tk.Spinbox(frame, from_=min_val, to=max_val, increment=step, textvariable=var, width=5)
        spinbox.pack(side=tk.RIGHT)
        self.value[f"{self.current_path}/{label}"] = var

    def _create_checkbox_at_path(self, path, label, variable):
        """
        Create checkbox widget at specific path.
        
        Args:
            path (str): Navigation path
            label (str): Widget label
            variable (bool): Widget value
        """
        if path == self.current_path:
            self._create_checkbox(label, variable)

    def _create_checkbox(self, label, value):
        """Create a checkbox widget."""
        var = tk.BooleanVar(master=self.root, value=value)
        check = tk.Checkbutton(self.get_current_frame(), text=label, variable=var)
        check.pack(anchor='w')
        self.value[f"{self.current_path}/{label}"] = var

    def _create_browse_file_at_path(self, path, label):
        """
        Create browse file widget at specific path.
        
        Args:
            path (str): Navigation path
            label (str): Widget label
        """
        if path == self.current_path:
            self._create_browse_file(label)

    def _create_browse_file(self, label):
        """Create a browse file widget."""
        frame = tk.Frame(self.get_current_frame())
        frame.pack(pady=5, fill=tk.X)
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        var = tk.StringVar(master=self.root)
        entry = tk.Entry(frame, textvariable=var)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        button = tk.Button(frame, text="Browse", command=lambda: var.set(filedialog.askopenfilename()))
        button.pack(side=tk.RIGHT)
        self.value[f"{self.current_path}/{label}"] = var

    def _create_button_at_path(self, path, label, value, widget_info):
        """
        Create button widget at specific path.
        
        Args:
            path (str): Navigation path
            label (str): Widget label
            value (bool): Widget value
            widget_info (dict): Widget information
        """
        if path == self.current_path:
            self._create_button(label, value, widget_info)

    def _create_button(self, label, value=False, widget_info=None):
        """Create a button widget."""
        var = tk.BooleanVar(master=self.root, value=value)

        def button_click():
            var.set(True)
            if widget_info and 'command' in widget_info:
                widget_info['command']()

        button = tk.Button(self.get_current_frame(), text=label, command=button_click)
        button.pack(pady=5)
        self.value[f"{self.current_path}/{label}"] = var

if __name__ == "__main__":
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