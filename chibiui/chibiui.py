
import threading
import time

class chibiui:
    """
    Outline: ChibiUI is a simple GUI framework using Tkinter.

    Methods:
    - __init__(title, nogui): Start the GUI thread and initialize the window.
    - create_ui(): Create the main window and start the event loop.
    - close_ui(): Close the window and exit the app.
    - add_textbox(label, value): Add a textbox with a label.
    - add_selector(label, options, value): Add a dropdown selector.
    - add_slider(label, min_val, max_val, step, variable): Add a slider with a spinbox.
    - add_checkbox(label, variable): Add a checkbox.
    - add_browse_file(label): Add a file selection widget.
    - add_button(label, value): Add a button.
    - navigate_to(path): Move to a specific path in the navigation tree.
    - get(path): Get the value of a widget.
    - set(path, value): Set the value of a widget.

    Usage Example:
        ui = chibiui"ChibiUI Example")
        ui.add_textbox("Title", "Personal Data")
        # ...
    """

    def close_ui(self):
        """
        Closes the UI window and terminates the application.
        """
        if not self.alive:
            return
        self.alive = False
        try:
            if self.root and self.root.winfo_exists():
                self.root.quit()
                self.root.destroy()
        except tk.TclError:
            # Widget already destroyed
            pass

    def __init__(self, title='ChibiUI', nogui=False):
        """
        Initializes the ChibiUI application. If nogui=True, run in headless mode (no tkinter import or GUI).

        Args:
            title (str): Title of the GUI window.
            nogui (bool): If True, run in headless mode. Default is False.
        """
        if not nogui:
            global tk, ttk, filedialog
            import tkinter as tk
            from tkinter import ttk, filedialog
        self.title = title
        self.value = {}
        self.navigation_tree = {}
        self.current_path = '/'
        self.alive = False
        self.nogui = nogui
        self.root = None
        if not self.nogui:
            self.thread = threading.Thread(target=self.create_ui, daemon=True)
            self.thread.start()
            while not self.alive:
                pass
        else:
            self.alive = True

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
        if self.nogui:
            return
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close_ui)
        self.root.title(self.title)
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        nav_frame = tk.Frame(main_paned, relief=tk.SOLID, borderwidth=1)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.nav_tree = ttk.Treeview(nav_frame, show='tree')
        self.nav_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.nav_tree.insert('', 'end', '/', text='Root', open=True)
        self.nav_tree.bind('<<TreeviewSelect>>', self._on_tree_select)
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
        self.root.mainloop()

    def _add_navigation(self, path):
        """
        Adds a new navigation path to the tree and creates corresponding content frame.

        Args:
            path (str): Navigation path (e.g., '/Person1', '/Person/Profile')
        """
        def __add_navigation():
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
            self._show_content(path)
            
        if hasattr(self, 'root') and self.root:
            self.root.after(0, __add_navigation)

    def _on_tree_select(self, event):
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
            self._show_content(self.current_path)

    def _show_content(self, path):
        """
        Show content for the specified navigation path.

        Args:
            path (str): Navigation path to show content for
        """
        path = self._normalize_path(path)
        
        if path not in self.navigation_tree:
            return
            
        for window_id in self.canvas.find_all():
            self.canvas.delete(window_id)
        
        content_frame = tk.Frame(self.canvas)
        self.navigation_tree[path]['frame'] = content_frame
        
        self.canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        self.scrollable_frame = content_frame
        
        if 'widgets' in self.navigation_tree[path]:
            for i, widget_info in enumerate(self.navigation_tree[path]['widgets']):
                if widget_info['type'] == 'textbox':
                    full_key = self._get_full_key(path, widget_info['label'])
                    value = self.value[full_key].get() if full_key in self.value else widget_info['value']
                    self._create_textbox(widget_info['label'], value)
                elif widget_info['type'] == 'selector':
                    full_key = self._get_full_key(path, widget_info['label'])
                    value = self.value[full_key].get() if full_key in self.value else widget_info['value']
                    self._create_selector(widget_info['label'], widget_info['options'], value)
                elif widget_info['type'] == 'slider':
                    full_key = self._get_full_key(path, widget_info['label'])
                    value = self.value[full_key].get() if full_key in self.value else widget_info['value']
                    self._create_slider(widget_info['label'], widget_info['min_val'], widget_info['max_val'], widget_info['step'], value)
                elif widget_info['type'] == 'checkbox':
                    full_key = self._get_full_key(path, widget_info['label'])
                    value = self.value[full_key].get() if full_key in self.value else widget_info['value']
                    self._create_checkbox(widget_info['label'], value)
                elif widget_info['type'] == 'browse_file':
                    self._create_browse_file(widget_info['label'])
                elif widget_info['type'] == 'button':
                    full_key = self._get_full_key(path, widget_info['label'])
                    value = self.value[full_key].get() if full_key in self.value else widget_info['value']
                    self._create_button(widget_info['label'], value, widget_info)
        
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _get_current_frame(self):
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
        Add a file selection button and a text field to the GUI.

        Args:
            label (str): The label for the file selector. You can use a path like "Person1/Select File".
        """
        path, actual_label = self._parse_label(label)
        
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
        full_key = self._get_full_key(path, actual_label)
        self.value[full_key] = tk.StringVar(value="")
        
        def _add_browse_file():
            if path == self.current_path:
                self._create_browse_file(actual_label)
            
        if hasattr(self, 'root') and self.root:
            self.root.after(0, _add_browse_file)

    def _add_widget(self, widget_type, label, **kwargs):
        """
        Generalized method to add a widget to the navigation tree.

        Args:
            widget_type (str): Type of the widget (e.g., 'textbox', 'selector', 'button')
            label (str): Label for the widget
            **kwargs: Additional parameters for the widget (e.g., options, value)
        """
        # Parse path from label
        path, actual_label = self._parse_label(label)

        # Auto-create navigation tree if it doesn't exist
        self._auto_create_navigation(path)

        # Check if widget already exists to prevent duplicates
        if path in self.navigation_tree:
            for existing_widget in self.navigation_tree[path]['widgets']:
                if existing_widget['type'] == widget_type and existing_widget['label'] == actual_label:
                    return  # Widget already exists, don't add duplicate

        # Add widget info to navigation tree
        widget_info = {'type': widget_type, 'label': actual_label, **kwargs}
        if path not in self.navigation_tree:
            self.navigation_tree[path] = {'frame': None, 'widgets': []}
        self.navigation_tree[path]['widgets'].append(widget_info)

        # Store value with full path for access
        full_key = self._get_full_key(path, actual_label)
        if 'value' in kwargs and full_key not in self.value:
            if self.nogui:
                # In headless mode, just store the value directly
                self.value[full_key] = kwargs['value']
            else:
                if widget_type == 'textbox':
                    self.value[full_key] = tk.StringVar(value=kwargs['value'])
                elif widget_type == 'selector':
                    self.value[full_key] = tk.StringVar(value=kwargs['value'])
                elif widget_type == 'button':
                    self.value[full_key] = tk.BooleanVar(value=kwargs['value'])
                else:
                    raise ValueError(f"Unsupported widget type: {widget_type}")
        # Only refresh display if this is the current path
        if not self.nogui and path == self.current_path:
            self._show_content(self.current_path)

    def add_textbox(self, label, value=""):
        """
        Add a textbox widget.

        Args:
            label (str): The label for the textbox.
            value (str, optional): The default value. Default is empty string.
        """
        self._add_widget('textbox', label, value=value)

    def add_selector(self, label, options= ["A", "B"], value="A"):
        """
        Add a dropdown selector widget.

        Args:
            label (str): The label for the selector.
            options (list): List of options.
            value (str, optional): The default value. Default is empty string.
        """
        self._add_widget('selector', label, options=options, value=value)

    def add_button(self, label, value=False):
        """
        Add a button widget.

        Args:
            label (str): The label for the button.
            value (bool, optional): The default value. Default is False.
        """
        self._add_widget('button', label, value=value)

    def add_slider(self, label, min_val=0, max_val=100, step=1, value=0):
        """
        Add a slider with a spinbox.

        Args:
            label (str): The label for the slider.
            min_val (float, optional): Minimum value. Default is 0.
            max_val (float, optional): Maximum value. Default is 100.
            step (float, optional): Step size. Default is 1.
            value (float, optional): Default value. Default is 0.
        """
        path, actual_label = self._parse_label(label)
        self._auto_create_navigation(path)
        widget_info = {
            'type': 'slider',
            'label': actual_label,
            'min_val': min_val,
            'max_val': max_val,
            'step': step,
            'value': value
        }
        if path not in self.navigation_tree:
            self.navigation_tree[path] = {'frame': None, 'widgets': []}
        self.navigation_tree[path]['widgets'].append(widget_info)
        full_key = self._get_full_key(path, actual_label)
        if self.nogui:
            self.value[full_key] = value
        else:
            self.value[full_key] = tk.DoubleVar(value=value)
        if not self.nogui and path == self.current_path:
            self._show_content(self.current_path)

    def add_checkbox(self, label, value=False):
        """
        Add a checkbox widget.

        Args:
            label (str): The label for the checkbox.
            value (bool, optional): Default value. Default is False.
        """
        path, actual_label = self._parse_label(label)
        self._auto_create_navigation(path)
        widget_info = {
            'type': 'checkbox',
            'label': actual_label,
            'value': value
        }
        if path not in self.navigation_tree:
            self.navigation_tree[path] = {'frame': None, 'widgets': []}
        self.navigation_tree[path]['widgets'].append(widget_info)
        full_key = self._get_full_key(path, actual_label)
        if self.nogui:
            self.value[full_key] = value
        else:
            self.value[full_key] = tk.BooleanVar(value=value)
        if not self.nogui and path == self.current_path:
            self._show_content(self.current_path)

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
        elif widget_info['type'] == 'browse_file':
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

    def get(self, path):
        """
        Get the value of a widget at the specified path.

        Args:
            path (str): The path to the widget (e.g., "/Main", "/Person1/Name")

        Returns:
            The value of the widget, or None if the path doesn't exist
        """
        if not self.alive:
            return None
        path = self._normalize_path(path)
        if path in self.value:
            v = self.value[path]
            if self.nogui:
                return v
            try:
                return v.get()
            except Exception:
                return None
        return None

    def set(self, path, value):
        """
        Set the value of a widget at the specified path.

        Args:
            path (str): The path to the widget (e.g., "/Main", "/Person1/Name")
            value: The value to set
        """
        if not self.alive:
            return
        path = self._normalize_path(path)
        if path in self.value:
            if self.nogui:
                self.value[path] = value
            else:
                try:
                    self.value[path].set(value)
                except Exception:
                    pass
        else:
            print(f"Warning: Path '{path}' not found")

    def navigate_to(self, path):
        """
        Navigate to a specific path in the navigation tree.

        Args:
            path (str): The path to navigate to (e.g., "/Person1", "Person2")
        """
        path = self._normalize_path(path)
        
        # Check if path exists in navigation tree
        if path in self.navigation_tree:
            # Update current path
            self.current_path = path
            
            # Select the item in the tree view
            if hasattr(self, 'nav_tree') and self.nav_tree.exists(path):
                self.nav_tree.selection_set(path)
                self.nav_tree.focus(path)
                
            # Show content for the selected path
            self._show_content(path)
            return True
        else:
            print(f"Warning: Path '{path}' not found in navigation tree")
            return False


    def _get_full_key(self, path, label):
        """
        Generate a full key for a widget based on path and label.

        Args:
            path (str): The path of the widget.
            label (str): The label of the widget.

        Returns:
            str: The full key for the widget.
        """
        return f"{path}/{label}" if path != '/' else f"/{label}"

    def _normalize_path(self, path):
        """
        Normalize a path by removing trailing slashes except for root path.

        Args:
            path (str): The path to normalize.

        Returns:
            str: The normalized path.
        """
        # Don't strip '/' from root path
        if not path.startswith('/'):
            path = '/' + path
        if path != '/':
            path = path.rstrip('/')
        return path

    def _parse_label(self, label):
        """
        Parse a label to extract the path and actual label.

        Args:
            label (str): The label to parse (e.g., 'Person1/Name').

        Returns:
            tuple: A tuple containing the path and the actual label.
        """
        if not label.startswith('/'):
            label = '/' + label
        if '/' in label:
            path_parts = label.split('/')
            # Remove empty parts from the beginning
            path_parts = [p for p in path_parts if p]
            if len(path_parts) > 1:
                path = '/' + '/'.join(path_parts[:-1])
                actual_label = path_parts[-1]
            else:
                path = '/'
                actual_label = path_parts[0] if path_parts else label
        else:
            path = '/'
            actual_label = label
        return path, actual_label

    def _create_textbox(self, label, value):
        """Create a textbox widget."""
        frame = tk.Frame(self._get_current_frame())
        frame.pack(pady=5, fill=tk.X)
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        
        # Use existing StringVar if available
        full_key = self._get_full_key(self.current_path, label)
        if full_key in self.value:
            entry_var = self.value[full_key]
        else:
            entry_var = tk.StringVar(master=self.root, value=value)
            self.value[full_key] = entry_var
            
        entry = tk.Entry(frame, textvariable=entry_var)
        entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)

    def _create_selector(self, label, options, value):
        """Create a selector widget."""
        frame = tk.Frame(self._get_current_frame())
        frame.pack(pady=5, fill=tk.X)
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        var = tk.StringVar(master=self.root, value=value)
        dropdown = ttk.Combobox(frame, textvariable=var, values=options)
        dropdown.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        
        # Store the variable for data access
        key = self._get_full_key(self.current_path, label)
        self.value[key] = var

    def _create_slider(self, label, min_val, max_val, step, value):
        """Create a slider widget."""
        frame = tk.Frame(self._get_current_frame())
        frame.pack(pady=5, fill=tk.X)
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        
        # Ensure initial value is aligned with step
        if step > 0:
            value = round(value / step) * step
        
        var = tk.DoubleVar(master=self.root, value=value)
        slider = tk.Scale(frame, from_=min_val, to=max_val, resolution=step, orient=tk.HORIZONTAL, variable=var)
        slider.pack(side=tk.LEFT, expand=True, fill=tk.X)
        spinbox = tk.Spinbox(frame, from_=min_val, to=max_val, increment=step, textvariable=var, width=5)
        spinbox.pack(side=tk.RIGHT)
        
        # Store the variable for data access
        key = self._get_full_key(self.current_path, label)
        self.value[key] = var

    def _create_checkbox(self, label, value):
        """Create a checkbox widget."""
        var = tk.BooleanVar(master=self.root, value=value)
        check = tk.Checkbutton(self._get_current_frame(), text=label, variable=var)
        check.pack(anchor='w')
        
        # Store the variable for data access
        key = self._get_full_key(self.current_path, label)
        self.value[key] = var

    def _create_browse_file(self, label):
        """Create a browse file widget."""
        frame = tk.Frame(self._get_current_frame())
        frame.pack(pady=5, fill=tk.X)
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        var = tk.StringVar(master=self.root)
        entry = tk.Entry(frame, textvariable=var)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        button = tk.Button(frame, text="Browse", command=lambda: var.set(filedialog.askopenfilename()))
        button.pack(side=tk.RIGHT)
        
        # Store the variable for data access
        key = self._get_full_key(self.current_path, label)
        self.value[key] = var

    def _create_button(self, label, value=False, widget_info=None):
        """Create a button widget."""
        
        # Generate key for the button
        button_key = self._get_full_key(self.current_path, label)
        
        # Use existing BooleanVar if available, otherwise create new one
        if button_key in self.value:
            var = self.value[button_key]
        else:
            var = tk.BooleanVar(master=self.root, value=value)
            self.value[button_key] = var

        def button_click():
            var.set(True)
            if widget_info and 'command' in widget_info:
                widget_info['command']()

        button = tk.Button(self._get_current_frame(), text=label, command=button_click)
        button.pack(pady=5)

if __name__ == "__main__":
    ui = chibiui("ChibiUI Example")
    ui.add_textbox("Title", "Personal Data")
    
    # Navigation tree items are automatically created from the path
    ui.add_textbox("Person/Name", "John Doe")
    ui.add_selector("Person/Gender", ["Male", "Female", "Other"], "Male")
    ui.add_slider("Person/Age", 0, 100, 1, 30)
    ui.add_checkbox("Person/Add File", True)
    ui.add_browse_file("Person/Select File")
    ui.add_button("Person/Submit", False)

    ui.add_textbox("Option/Country", "Japan")

    while ui.alive: # Main loop to keep the UI running
        if ui.get("Person/Submit"): # Check if the button is pressed
            print("Submit button pressed!")
            print("Title:", ui.get("/Title"))

            print("-- Personal Info --")
            print("Name:", ui.get("Person/Name"))
            print("Gender:", ui.get("Person/Gender"))
            print("Age:", ui.get("Person/Age"))
            print("Select File:", ui.get("Person/Select File"))
            print("Country:", ui.get("Option/Country"))
            print("---")

            ui.set("Person/Submit", False) # Reset the button value
        
        # Add a small delay to prevent high CPU usage
        time.sleep(0.01)

    print('End')
