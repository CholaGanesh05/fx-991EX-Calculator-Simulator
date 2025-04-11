import tkinter as tk
from tkinter import messagebox, ttk, colorchooser, filedialog
import math
import cmath
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import json
import os
from datetime import datetime

class FX991EXCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Casio fx-991EX ClassWiz Advanced")
        self.root.geometry("380x700")
        self.root.configure(bg="#f0f0f0")
        
        # Set icon (placeholder - you would use a real icon file)
        # self.root.iconbitmap('calculator_icon.ico')
        
        # Load settings or use defaults
        self.load_settings()

        # Application state
        self.current_input = ""
        self.result_shown = False
        self.shift_active = False
        self.alpha_active = False
        self.angle_mode = self.settings.get("angle_mode", "DEG")  # DEG, RAD, GRAD
        self.calculation_mode = self.settings.get("calculation_mode", "COMP")  # COMP, STAT, etc.
        self.decimal_places = self.settings.get("decimal_places", 10)
        self.ans = 0
        self.memory = 0
        self.memories = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
        self.history = []
        self.max_history = 50
        self.display_line1 = ""
        self.display_line2 = "0"
        self.qr_visible = False
        self.stat_data = []
        self.matrix_data = {"A": np.zeros((2, 2)), "B": np.zeros((2, 2)), "C": np.zeros((2, 2))}
        self.matrix_dims = {"A": (2, 2), "B": (2, 2), "C": (2, 2)}
        self.equation_coefficients = []
        
        # Themes
        self.themes = {
            "Default": {
                "bg_main": "#f0f0f0",
                "bg_display": "#ffffff",
                "fg_display": "#000000",
                "bg_button": "#e0e0e0",
                "fg_button": "#000000",
                "bg_number": "#ffffff",
                "fg_number": "#000000",
                "bg_function": "#d0d0d0",
                "fg_function": "#000000",
                "bg_operator": "#ffcc99",
                "fg_operator": "#000000",
                "bg_command": "#b0c4de",
                "fg_command": "#000000",
                "bg_equals": "#ff6666",
                "fg_equals": "#ffffff",
                "shift_color": "#ff9900",
                "alpha_color": "#009900"
            },
            "Dark": {
                "bg_main": "#2c2c2c",
                "bg_display": "#1c1c1c",
                "fg_display": "#ffffff",
                "bg_button": "#3c3c3c",
                "fg_button": "#ffffff",
                "bg_number": "#4c4c4c",
                "fg_number": "#ffffff",
                "bg_function": "#505050",
                "fg_function": "#ffffff",
                "bg_operator": "#ff9966",
                "fg_operator": "#000000",
                "bg_command": "#6699cc",
                "fg_command": "#ffffff",
                "bg_equals": "#cc3333",
                "fg_equals": "#ffffff",
                "shift_color": "#ffcc66",
                "alpha_color": "#99cc99"
            },
            "Blue": {
                "bg_main": "#d4e6f1",
                "bg_display": "#f5f8fa",
                "fg_display": "#1a5276",
                "bg_button": "#d6eaf8",
                "fg_button": "#1a5276",
                "bg_number": "#eaf2f8",
                "fg_number": "#1a5276",
                "bg_function": "#aed6f1",
                "fg_function": "#154360",
                "bg_operator": "#3498db",
                "fg_operator": "#ffffff",
                "bg_command": "#2980b9",
                "fg_command": "#ffffff",
                "bg_equals": "#2471a3",
                "fg_equals": "#ffffff",
                "shift_color": "#f39c12",
                "alpha_color": "#27ae60"
            },
            "Vintage": {
                "bg_main": "#f5eacb",
                "bg_display": "#fef9e7",
                "fg_display": "#784212",
                "bg_button": "#f8efd4",
                "fg_button": "#784212",
                "bg_number": "#fcf3cf",
                "fg_number": "#784212",
                "bg_function": "#f5cba7",
                "fg_function": "#784212",
                "bg_operator": "#d35400",
                "fg_operator": "#ffffff",
                "bg_command": "#b9770e",
                "fg_command": "#ffffff",
                "bg_equals": "#a04000",
                "fg_equals": "#ffffff",
                "shift_color": "#ba4a00",
                "alpha_color": "#196f3d"
            }
        }
        
        # Use current theme
        self.current_theme = self.settings.get("theme", "Default")
        self.theme = self.themes[self.current_theme]
        
        # Create UI elements
        self.create_display()
        self.create_indicators()
        self.create_keyboard()
        self.create_menu()
        self.create_qr_display()
        self.create_status_bar()
        
        # Initial window size setup
        if self.settings.get("fullscreen", False):
            self.root.attributes("-fullscreen", True)
        
        # Bind keyboard keys
        self.bind_keyboard_keys()
        
        # Apply theme
        self.apply_theme()

    def load_settings(self):
        """Load user settings from file"""
        try:
            if os.path.exists("calculator_settings.json"):
                with open("calculator_settings.json", "r") as f:
                    self.settings = json.load(f)
            else:
                self.settings = {
                    "angle_mode": "DEG",
                    "calculation_mode": "COMP",
                    "decimal_places": 10,
                    "theme": "Default",
                    "fullscreen": False,
                    "history_enabled": True
                }
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = {
                "angle_mode": "DEG",
                "calculation_mode": "COMP",
                "decimal_places": 10,
                "theme": "Default",
                "fullscreen": False,
                "history_enabled": True
            }

    def save_settings(self):
        """Save user settings to file"""
        try:
            settings_to_save = {
                "angle_mode": self.angle_mode,
                "calculation_mode": self.calculation_mode,
                "decimal_places": self.decimal_places,
                "theme": self.current_theme,
                "fullscreen": self.root.attributes("-fullscreen"),
                "history_enabled": self.settings.get("history_enabled", True)
            }
            with open("calculator_settings.json", "w") as f:
                json.dump(settings_to_save, f)
        except Exception as e:
            messagebox.showerror("Settings Error", f"Error saving settings: {e}")

    def create_display(self):
        """Create the calculator display area with enhanced visuals"""
        display_frame = tk.Frame(self.root, bg=self.theme["bg_main"], bd=2, relief=tk.RIDGE)
        display_frame.pack(pady=10, padx=10, fill=tk.BOTH)

        # Input history display
        self.input_display = tk.Label(
            display_frame, 
            text="", 
            font=("Consolas", 12), 
            bg=self.theme["bg_display"], 
            fg=self.theme["fg_display"], 
            anchor="e", 
            justify="right",
            height=1,
            padx=5
        )
        self.input_display.pack(fill=tk.X, padx=5, pady=(5, 0))

        # Main display
        self.main_display = tk.Label(
            display_frame, 
            text="0", 
            font=("Consolas", 24, "bold"), 
            bg=self.theme["bg_display"], 
            fg=self.theme["fg_display"], 
            anchor="e", 
            justify="right",
            height=2,
            padx=5
        )
        self.main_display.pack(fill=tk.BOTH, padx=5, pady=(0, 5))
        
        # Secondary info display
        self.info_frame = tk.Frame(display_frame, bg=self.theme["bg_display"])
        self.info_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.secondary_display = tk.Label(
            self.info_frame,
            text="",
            font=("Consolas", 10),
            bg=self.theme["bg_display"],
            fg="#666666",
            anchor="w",
            padx=5
        )
        self.secondary_display.pack(side=tk.LEFT)
        
        # Add visual calculator mode indicator
        self.mode_badge = tk.Label(
            self.info_frame,
            text=self.calculation_mode,
            font=("Consolas", 10, "bold"),
            bg="#3498db",
            fg="white",
            padx=5,
            pady=2,
            relief=tk.FLAT,
            bd=0
        )
        self.mode_badge.pack(side=tk.RIGHT, padx=(0, 5))

    def create_indicators(self):
        """Create status indicators for calculator modes with improved visuals"""
        indicator_frame = tk.Frame(self.root, bg=self.theme["bg_main"])
        indicator_frame.pack(padx=10, pady=(0, 5), fill=tk.X)

        # Left indicators
        left_frame = tk.Frame(indicator_frame, bg=self.theme["bg_main"])
        left_frame.pack(side=tk.LEFT)
        
        # Create indicator badges
        self.shift_indicator = tk.Label(
            left_frame, text="SHIFT", 
            fg="#aaaaaa", bg=self.theme["bg_main"], 
            font=("Arial", 9, "bold"),
            padx=5, pady=1,
            relief=tk.FLAT
        )
        self.shift_indicator.pack(side=tk.LEFT, padx=2)

        self.alpha_indicator = tk.Label(
            left_frame, text="ALPHA", 
            fg="#aaaaaa", bg=self.theme["bg_main"], 
            font=("Arial", 9, "bold"),
            padx=5, pady=1,
            relief=tk.FLAT
        )
        self.alpha_indicator.pack(side=tk.LEFT, padx=2)

        # Right indicators
        right_frame = tk.Frame(indicator_frame, bg=self.theme["bg_main"])
        right_frame.pack(side=tk.RIGHT)
        
        self.mode_indicator = tk.Label(
            right_frame, text=self.calculation_mode, 
            fg=self.theme["fg_button"], bg=self.theme["bg_main"], 
            font=("Arial", 9, "bold")
        )
        self.mode_indicator.pack(side=tk.RIGHT, padx=5)

        self.angle_indicator = tk.Label(
            right_frame, text=self.angle_mode, 
            fg=self.theme["fg_button"], bg=self.theme["bg_main"], 
            font=("Arial", 9)
        )
        self.angle_indicator.pack(side=tk.RIGHT, padx=5)

    def create_keyboard(self):
        """Create the calculator keyboard with improved visual design"""
        # Create a notebook for different keyboard layouts
        self.keyboard_notebook = ttk.Notebook(self.root)
        self.keyboard_notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Main keyboard tab
        main_keyboard_frame = tk.Frame(self.keyboard_notebook, bg=self.theme["bg_main"])
        self.keyboard_notebook.add(main_keyboard_frame, text="Main")
        
        # Button styling
        btn_colors = {
            "default": {"bg": self.theme["bg_button"], "fg": self.theme["fg_button"]},
            "number": {"bg": self.theme["bg_number"], "fg": self.theme["fg_number"]},
            "function": {"bg": self.theme["bg_function"], "fg": self.theme["fg_function"]},
            "operator": {"bg": self.theme["bg_operator"], "fg": self.theme["fg_operator"]},
            "command": {"bg": self.theme["bg_command"], "fg": self.theme["fg_command"]},
            "equals": {"bg": self.theme["bg_equals"], "fg": self.theme["fg_equals"]},
            "memory": {"bg": self.theme["bg_function"], "fg": self.theme["fg_function"]}
        }

        # Button definitions [text, button_type, shift_text, alpha_text]
        buttons = [
            [("SHIFT", "command", "", ""), ("ALPHA", "command", "", ""), ("MODE", "command", "SET UP", ""), 
             ("DEL", "function", "INS", ""), ("AC", "function", "OFF", "")],
            
            [("x⁻¹", "function", "x!", "A"), ("√", "function", "∛", "B"), 
             ("x²", "function", "x³", "C"), ("^", "function", "log₂", "D"), 
             ("log", "function", "10^", "E")],
            
            [("ln", "function", "e^", "F"), ("(−)", "function", "°'\"", "G"), 
             ("hyp", "function", "d/c", "H"), ("sin", "function", "sin⁻¹", "I"), 
             ("cos", "function", "cos⁻¹", "J")],
            
            [("tan", "function", "tan⁻¹", "K"), ("RCL", "memory", "STO", "L"), 
             ("ENG", "function", "FIX", "M"), ("(", "function", "{", "N"), 
             (")", "function", "}", "O")],
            
            [("7", "number", "π", "P"), ("8", "number", "e", "Q"), 
             ("9", "number", "j", "R"), ("DEL", "function", "INS", "S"), 
             ("AC", "function", "OFF", "T")],
            
            [("4", "number", "∠", "U"), ("5", "number", "i", "V"), 
             ("6", "number", ":", "W"), ("×", "operator", "%", "X"), 
             ("÷", "operator", "mod", "Y")],
            
            [("1", "number", "⏎", "Z"), ("2", "number", "□", "space"), 
             ("3", "number", "$", ","), ("−", "operator", "m", ":"), 
             ("+", "operator", "M", ";")],
            
            [("0", "number", "∞", "."), (".", "number", "Ran#", "="), 
             ("×10^", "function", "Abs", "+"), ("Ans", "function", "DRG", "-"), 
             ("=", "equals", "⇒", "?")]
        ]

        # Create buttons with improved appearance
        self.button_widgets = {}
        
        for i, row in enumerate(buttons):
            for j, (text, btn_type, shift_text, alpha_text) in enumerate(row):
                # Create button frame to hold main text and smaller shift/alpha text
                btn_frame = tk.Frame(
                    main_keyboard_frame, 
                    bg=btn_colors[btn_type]["bg"], 
                    bd=1, 
                    relief=tk.RAISED,
                    highlightbackground="#cccccc",
                    highlightthickness=1
                )
                btn_frame.grid(row=i, column=j, padx=2, pady=2, sticky="nsew")
                
                # Button with main text
                btn = tk.Button(
                    btn_frame, 
                    text=text, 
                    font=("Arial", 12, "bold"), 
                    bg=btn_colors[btn_type]["bg"],
                    fg=btn_colors[btn_type]["fg"],
                    activebackground=self.get_active_color(btn_colors[btn_type]["bg"]),
                    bd=0,
                    highlightthickness=0,
                    relief=tk.FLAT,
                    padx=3,
                    pady=3,
                    cursor="hand2",
                    command=lambda t=text: self.button_click(t)
                )
                btn.pack(expand=True, fill=tk.BOTH)
                
                # Add shift text if applicable
                if shift_text:
                    shift_label = tk.Label(
                        btn_frame, 
                        text=shift_text, 
                        font=("Arial", 7), 
                        bg=btn_colors[btn_type]["bg"],
                        fg=self.theme["shift_color"]
                    )
                    shift_label.place(x=2, y=2)
                
                # Add alpha text if applicable
                if alpha_text:
                    alpha_label = tk.Label(
                        btn_frame, 
                        text=alpha_text, 
                        font=("Arial", 7), 
                        bg=btn_colors[btn_type]["bg"],
                        fg=self.theme["alpha_color"]
                    )
                    alpha_label.place(x=2, y=18)
                
                self.button_widgets[text] = btn

            # Configure grid weights
            main_keyboard_frame.grid_rowconfigure(i, weight=1)
        
        for j in range(5):
            main_keyboard_frame.grid_columnconfigure(j, weight=1)
            
        # Add additional keyboard tabs
        self.create_scientific_keyboard()
        self.create_matrix_keyboard()
        self.create_equation_keyboard()

    def create_scientific_keyboard(self):
        """Create a tab with advanced scientific functions"""
        sci_keyboard_frame = tk.Frame(self.keyboard_notebook, bg=self.theme["bg_main"])
        self.keyboard_notebook.add(sci_keyboard_frame, text="Scientific")
        
        # Scientific functions
        scientific_buttons = [
            [("sinh", "function"), ("cosh", "function"), ("tanh", "function"), ("d/dx", "function"), ("∫", "function")],
            [("sinh⁻¹", "function"), ("cosh⁻¹", "function"), ("tanh⁻¹", "function"), ("x!", "function"), ("nPr", "function")],
            [("Σ", "function"), ("Π", "function"), ("rand", "function"), ("nCr", "function"), ("|x|", "function")],
            [("gcd", "function"), ("lcm", "function"), ("mod", "function"), ("floor", "function"), ("ceil", "function")],
            [("sin⁻¹", "function"), ("cos⁻¹", "function"), ("tan⁻¹", "function"), ("log₂", "function"), ("logₓ", "function")],
            [("e^x", "function"), ("10^x", "function"), ("x^3", "function"), ("∛", "function"), ("Pol(", "function")],
            [("Rec(", "function"), ("→r∠θ", "function"), ("→a+bi", "function"), ("arg", "function"), ("conj", "function")]
        ]
        
        for i, row in enumerate(scientific_buttons):
            for j, (text, btn_type) in enumerate(row):
                btn = tk.Button(
                    sci_keyboard_frame, 
                    text=text, 
                    font=("Arial", 11), 
                    bg=self.theme["bg_function"],
                    fg=self.theme["fg_function"],
                    activebackground=self.get_active_color(self.theme["bg_function"]),
                    relief=tk.RAISED,
                    bd=1,
                    padx=3,
                    pady=8,
                    cursor="hand2",
                    command=lambda t=text: self.scientific_function(t)
                )
                btn.grid(row=i, column=j, padx=2, pady=2, sticky="nsew")
                
                # Add to widgets dictionary
                self.button_widgets[text] = btn
            
            # Configure grid weights
            sci_keyboard_frame.grid_rowconfigure(i, weight=1)
        
        for j in range(5):
            sci_keyboard_frame.grid_columnconfigure(j, weight=1)

    def create_matrix_keyboard(self):
        """Create a tab for matrix operations"""
        matrix_keyboard_frame = tk.Frame(self.keyboard_notebook, bg=self.theme["bg_main"])
        self.keyboard_notebook.add(matrix_keyboard_frame, text="Matrix")
        
        # Matrix selector
        matrix_select_frame = tk.Frame(matrix_keyboard_frame, bg=self.theme["bg_main"])
        matrix_select_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(matrix_select_frame, text="Select Matrix:", bg=self.theme["bg_main"]).pack(side=tk.LEFT)
        
        self.matrix_var = tk.StringVar(value="A")
        matrices = ["A", "B", "C"]
        for matrix in matrices:
            rb = tk.Radiobutton(
                matrix_select_frame, 
                text=matrix, 
                variable=self.matrix_var, 
                value=matrix,
                bg=self.theme["bg_main"],
                command=self.update_matrix_display
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Matrix dimensions
        dim_frame = tk.Frame(matrix_keyboard_frame, bg=self.theme["bg_main"])
        dim_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(dim_frame, text="Rows:", bg=self.theme["bg_main"]).pack(side=tk.LEFT)
        self.rows_var = tk.IntVar(value=2)
        rows_spin = tk.Spinbox(dim_frame, from_=1, to=4, width=3, textvariable=self.rows_var, command=self.resize_matrix)
        rows_spin.pack(side=tk.LEFT, padx=5)
        
        tk.Label(dim_frame, text="Columns:", bg=self.theme["bg_main"]).pack(side=tk.LEFT, padx=(10, 0))
        self.cols_var = tk.IntVar(value=2)
        cols_spin = tk.Spinbox(dim_frame, from_=1, to=4, width=3, textvariable=self.cols_var, command=self.resize_matrix)
        cols_spin.pack(side=tk.LEFT, padx=5)
        
        # Matrix display area
        self.matrix_display_frame = tk.Frame(matrix_keyboard_frame, bg=self.theme["bg_main"])
        self.matrix_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Matrix entries
        self.matrix_entries = []
        
        # Matrix operations
        op_frame = tk.Frame(matrix_keyboard_frame, bg=self.theme["bg_main"])
        op_frame.pack(fill=tk.X, padx=10, pady=5)
        
        matrix_ops = [
            ("Det", self.matrix_determinant),
            ("Inv", self.matrix_inverse),
            ("Trans", self.matrix_transpose),
            ("A×B", self.matrix_multiply),
            ("Solve", self.matrix_solve)
        ]
        
        for text, cmd in matrix_ops:
            btn = tk.Button(
                op_frame,
                text=text,
                font=("Arial", 10),
                bg=self.theme["bg_function"],
                fg=self.theme["fg_function"],
                command=cmd,
                padx=5,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Initialize matrix display
        self.update_matrix_display()

    def create_equation_keyboard(self):
        """Create a tab for equation solving"""
        equation_frame = tk.Frame(self.keyboard_notebook, bg=self.theme["bg_main"])
        self.keyboard_notebook.add(equation_frame, text="Equation")
        
        # Equation type selector
        eq_type_frame = tk.Frame(equation_frame, bg=self.theme["bg_main"])
        eq_type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(eq_type_frame, text="Equation Type:", bg=self.theme["bg_main"]).pack(side=tk.LEFT)
        
        self.eq_type_var = tk.StringVar(value="Linear")
        eq_types = [("Linear", "Linear"), ("Quadratic", "Quadratic"), ("Cubic", "Cubic"), ("System 2×2", "System2"), ("System 3×3", "System3")]
        for text, value in eq_types:
            rb = tk.Radiobutton(
                eq_type_frame, 
                text=text, 
                variable=self.eq_type_var, 
                value=value,
                bg=self.theme["bg_main"],
                command=self.update_equation_interface
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Equation coefficients area
        self.eq_display_frame = tk.Frame(equation_frame, bg=self.theme["bg_main"])
        self.eq_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Equation operations
        op_frame = tk.Frame(equation_frame, bg=self.theme["bg_main"])
        op_frame.pack(fill=tk.X, padx=10, pady=5)
        
        solve_btn = tk.Button(
            op_frame,
            text="Solve Equation",
            font=("Arial", 12, "bold"),
            bg=self.theme["bg_equals"],
            fg=self.theme["fg_equals"],
            command=self.solve_equation,
            padx=10,
            pady=5
        )
        solve_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Initialize equation interface
        self.update_equation_interface()

    def create_qr_display(self):
        """Create hidden QR code display area"""
        self.qr_frame = tk.Frame(self.root, bg=self.theme["bg_main"])
        
        self.qr_canvas = tk.Canvas(self.qr_frame, width=200, height=200, bg="white", highlightthickness=0)
        self.qr_canvas.pack(padx=10, pady=10)
        
        close_btn = tk.Button(
            self.qr_frame, 
            text="Close QR", 
            command=self.toggle_qr_display,
            bg=self.theme["bg_command"],
            fg=self.theme["fg_command"]
        )
        close_btn.pack(pady=(0, 10))

    def create_status_bar(self):
        """Create status bar for additional information"""
        self.status_bar = tk.Frame(self.root, bg="#e0e0e0", height=20)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_text = tk.Label(
            self.status_bar, 
            text="Ready", 
            bg="#e0e0e0", 
            fg="#555555",
            font=("Arial", 8),
            anchor="w"
        )
        self.status_text.pack(side=tk.LEFT, padx=5)
        
        # Add battery indicator (simulated)
        self.battery_indicator = tk.Label(
            self.status_bar,
            text="🔋 100%",
            bg="#e0e0e0",
            fg="#555555",
            font=("Arial", 8)
        )
        self.battery_indicator.pack(side=tk.RIGHT, padx=5)
        
        # Add time display
        self.time_display = tk.Label(
            self.status_bar,
            text=datetime.now().strftime("%H:%M"),
            bg="#e0e0e0",
            fg="#555555",
            font=("Arial", 8)
        )
        self.time_display.pack(side=tk.RIGHT, padx=5)
        
        # Update time periodically
        self.update_time()

    def create_menu(self):
        """Create enhanced application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Calculation", command=self.clear_all)
        file_menu.add_command(label="Copy Result", command=self.copy_result)
        file_menu.add_command(label="Paste", command=self.paste_from_clipboard)
        file_menu.add_separator()
        file_menu.add_command(label="Save History", command=self.save_history)
        file_menu.add_command(label="Load History", command=self.load_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        edit_menu.add_command(label="Clear History", command=self.clear_history)
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences", command=self.show_preferences)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Mode menu
        mode_menu = tk.Menu(menubar, tearoff=0)
        mode_menu.add_command(label="COMP", command=lambda: self.set_calculation_mode("COMP"))
        mode_menu.add_command(label="STAT", command=lambda: self.set_calculation_mode("STAT"))
        mode_menu.add_command(label="TABLE", command=lambda: self.set_calculation_mode("TABLE"))
        mode_menu.add_command(label="EQN", command=lambda: self.set_calculation_mode("EQN"))
        mode_menu.add_separator()
        mode_menu.add_command(label="Matrix", command=lambda: self.set_calculation_mode("MATRIX"))
        mode_menu.add_command(label="Vector", command=lambda: self.set_calculation_mode("VECTOR"))
        mode_menu.add_command(label="Distribution", command=lambda: self.set_calculation_mode("DISTRIB"))
        menubar.add_cascade(label="Mode", menu=mode_menu)
        
        # Angle unit menu
        angle_menu = tk.Menu(menubar, tearoff=0)
        angle_menu.add_command(label="Degrees (DEG)", command=lambda: self.set_angle_mode("DEG"))
        angle_menu.add_command(label="Radians (RAD)", command=lambda: self.set_angle_mode("RAD"))
        angle_menu.add_command(label="Gradians (GRAD)", command=lambda: self.set_angle_mode("GRAD"))
        menubar.add_cascade(label="Angle", menu=angle_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Fullscreen", command=self.toggle_fullscreen)
        view_menu.add_separator()
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for theme_name in self.themes.keys():
            theme_menu.add_command(
                label=theme_name,
                command=lambda t=theme_name: self.set_theme(t)
            )
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        
        view_menu.add_command(label="Show QR Code", command=self.toggle_qr_display)
        view_menu.add_command(label="Show History", command=self.show_history)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def get_active_color(self, base_color):
        """Get a slightly darker color for button active state"""
        if base_color.startswith("#"):
            # Convert hex to RGB
            r = int(base_color[1:3], 16)
            g = int(base_color[3:5], 16)
            b = int(base_color[5:7], 16)
            # Darken by 20%
            r = max(0, int(r * 0.8))
            g = max(0, int(g * 0.8))
            b = max(0, int(b * 0.8))
            return f"#{r:02x}{g:02x}{b:02x}"
        return base_color

    def bind_keyboard_keys(self):
        """Bind keyboard keys to calculator functions"""
        # Number keys
        for num in range(10):
            self.root.bind(str(num), lambda e, n=num: self.button_click(str(n)))
        
        # Basic operations
        self.root.bind("+", lambda e: self.button_click("+"))
        self.root.bind("-", lambda e: self.button_click("−"))
        self.root.bind("*", lambda e: self.button_click("×"))
        self.root.bind("/", lambda e: self.button_click("÷"))
        self.root.bind("^", lambda e: self.button_click("^"))
        
        # Other keys
        self.root.bind(".", lambda e: self.button_click("."))
        self.root.bind("(", lambda e: self.button_click("("))
        self.root.bind(")", lambda e: self.button_click(")"))
        self.root.bind("=", lambda e: self.button_click("="))
        self.root.bind("<Return>", lambda e: self.button_click("="))
        self.root.bind("<BackSpace>", lambda e: self.button_click("DEL"))
        self.root.bind("<Escape>", lambda e: self.button_click("AC"))
        
        # Special keys
        self.root.bind("<Shift_L>", lambda e: self.toggle_shift())
        self.root.bind("<Shift_R>", lambda e: self.toggle_shift())
        self.root.bind("<Control_L>", lambda e: self.toggle_alpha())
        self.root.bind("<Control_R>", lambda e: self.toggle_alpha())

    def apply_theme(self):
        """Apply the current theme to all UI elements"""
        theme = self.themes[self.current_theme]
        
        # Main window
        self.root.configure(bg=theme["bg_main"])
        
        # Display
        self.input_display.configure(bg=theme["bg_display"], fg=theme["fg_display"])
        self.main_display.configure(bg=theme["bg_display"], fg=theme["fg_display"])
        self.secondary_display.configure(bg=theme["bg_display"], fg="#666666")
        self.info_frame.configure(bg=theme["bg_display"])
        
        # Indicators
        self.shift_indicator.configure(bg=theme["bg_main"])
        self.alpha_indicator.configure(bg=theme["bg_main"])
        self.mode_indicator.configure(bg=theme["bg_main"], fg=theme["fg_button"])
        self.angle_indicator.configure(bg=theme["bg_main"], fg=theme["fg_button"])
        
        # Update all buttons
        btn_colors = {
            "default": {"bg": theme["bg_button"], "fg": theme["fg_button"]},
            "number": {"bg": theme["bg_number"], "fg": theme["fg_number"]},
            "function": {"bg": theme["bg_function"], "fg": theme["fg_function"]},
            "operator": {"bg": theme["bg_operator"], "fg": theme["fg_operator"]},
            "command": {"bg": theme["bg_command"], "fg": theme["fg_command"]},
            "equals": {"bg": theme["bg_equals"], "fg": theme["fg_equals"]},
            "memory": {"bg": theme["bg_function"], "fg": theme["fg_function"]}
        }
        
        for btn_text, btn in self.button_widgets.items():
            btn_type = "default"
            if btn_text in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]:
                btn_type = "number"
            elif btn_text in ["+", "−", "×", "÷", "^"]:
                btn_type = "operator"
            elif btn_text in ["="]:
                btn_type = "equals"
            elif btn_text in ["SHIFT", "ALPHA", "MODE", "DEL", "AC"]:
                btn_type = "command"
            elif btn_text in ["RCL"]:
                btn_type = "memory"
            else:
                btn_type = "function"
            
            btn.configure(
                bg=btn_colors[btn_type]["bg"],
                fg=btn_colors[btn_type]["fg"],
                activebackground=self.get_active_color(btn_colors[btn_type]["bg"])
            )

    def update_display(self):
        """Update the calculator display"""
        self.input_display.config(text=self.display_line1)
        self.main_display.config(text=self.display_line2)
        
        # Update secondary display with mode info
        mode_info = f"{self.calculation_mode} | {self.angle_mode} | FIX {self.decimal_places}"
        if self.shift_active:
            mode_info += " | SHIFT"
        if self.alpha_active:
            mode_info += " | ALPHA"
        self.secondary_display.config(text=mode_info)
        
        # Update mode badge
        self.mode_badge.config(text=self.calculation_mode)
        
        # Update indicators
        self.shift_indicator.config(
            fg=self.theme["shift_color"] if self.shift_active else "#aaaaaa"
        )
        self.alpha_indicator.config(
            fg=self.theme["alpha_color"] if self.alpha_active else "#aaaaaa"
        )
        self.angle_indicator.config(text=self.angle_mode)
        self.mode_indicator.config(text=self.calculation_mode)

    def button_click(self, button_text):
        """Handle button clicks"""
        if button_text == "SHIFT":
            self.toggle_shift()
            return
        elif button_text == "ALPHA":
            self.toggle_alpha()
            return
        elif button_text == "MODE":
            self.show_mode_menu()
            return
        elif button_text == "DEL":
            self.delete_char()
            return
        elif button_text == "AC":
            self.clear_all()
            return
        elif button_text == "=":
            self.calculate_result()
            return
        
        # Handle shifted or alpha functions
        if self.shift_active:
            # Look up shifted function
            for btn in self.button_widgets.values():
                if hasattr(btn, 'shift_text') and btn.shift_text == button_text:
                    button_text = btn.shift_text
                    break
            self.toggle_shift(False)
        elif self.alpha_active:
            # Look up alpha function
            for btn in self.button_widgets.values():
                if hasattr(btn, 'alpha_text') and btn.alpha_text == button_text:
                    button_text = btn.alpha_text
                    break
            self.toggle_alpha(False)
        
        # Handle the button input
        if self.result_shown and button_text in "0123456789.(":
            self.current_input = ""
            self.result_shown = False
        
        if button_text == "Ans":
            self.current_input += str(self.ans)
        elif button_text == "×10^":
            self.current_input += "e"
        elif button_text == "(−)":
            if self.current_input and self.current_input[-1] in "0123456789":
                self.current_input += "*(-1)"
            else:
                self.current_input += "-"
        else:
            self.current_input += button_text
        
        self.display_line1 = self.current_input
        self.display_line2 = self.current_input[-20:]  # Show last 20 chars
        self.update_display()

    def toggle_shift(self, state=None):
        """Toggle shift mode"""
        if state is None:
            self.shift_active = not self.shift_active
        else:
            self.shift_active = state
        self.update_display()

    def toggle_alpha(self, state=None):
        """Toggle alpha mode"""
        if state is None:
            self.alpha_active = not self.alpha_active
        else:
            self.alpha_active = state
        self.update_display()

    def delete_char(self):
        """Delete the last character from input"""
        if self.current_input:
            self.current_input = self.current_input[:-1]
            self.display_line1 = self.current_input
            self.display_line2 = self.current_input[-20:] if self.current_input else "0"
            self.result_shown = False
            self.update_display()

    def clear_all(self):
        """Clear all input and reset calculator"""
        self.current_input = ""
        self.display_line1 = ""
        self.display_line2 = "0"
        self.result_shown = False
        self.update_display()

    def calculate_result(self):
        """Calculate and display the result"""
        try:
            # Replace display symbols with Python-compatible ones
            expr = self.current_input
            expr = expr.replace("×", "*")
            expr = expr.replace("÷", "/")
            expr = expr.replace("^", "**")
            
            # Handle angle mode conversions for trig functions
            if self.angle_mode == "DEG":
                expr = re.sub(r'sin\(', 'math.sin(math.radians(', expr)
                expr = re.sub(r'cos\(', 'math.cos(math.radians(', expr)
                expr = re.sub(r'tan\(', 'math.tan(math.radians(', expr)
            elif self.angle_mode == "GRAD":
                expr = re.sub(r'sin\(', 'math.sin(math.pi*', expr) + '/200)'
                expr = re.sub(r'cos\(', 'math.cos(math.pi*', expr) + '/200)'
                expr = re.sub(r'tan\(', 'math.tan(math.pi*', expr) + '/200)'
            
            # Evaluate the expression
            result = eval(expr, {"__builtins__": None}, 
                         {"math": math, "cmath": cmath, "np": np, "stats": stats, "ans": self.ans})
            
            # Format the result
            if isinstance(result, (int, float)):
                if abs(result) > 1e10 or (abs(result) < 1e-4 and result != 0):
                    formatted_result = "{:.{}e}".format(result, self.decimal_places)
                else:
                    formatted_result = "{:.{}f}".format(result, self.decimal_places).rstrip('0').rstrip('.')
            else:
                formatted_result = str(result)
            
            self.display_line2 = formatted_result
            self.ans = result
            self.result_shown = True
            
            # Add to history
            self.add_to_history(f"{self.current_input} = {formatted_result}")
            
        except Exception as e:
            self.display_line2 = "Error"
            messagebox.showerror("Calculation Error", f"Invalid expression: {e}")
        
        self.update_display()

    def add_to_history(self, entry):
        """Add an entry to the calculation history"""
        if not self.settings.get("history_enabled", True):
            return
            
        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def show_history(self):
        """Show calculation history in a new window"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Calculation History")
        history_window.geometry("400x500")
        
        scrollbar = tk.Scrollbar(history_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_list = tk.Listbox(
            history_window, 
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            selectbackground="#3498db",
            selectforeground="white"
        )
        history_list.pack(fill=tk.BOTH, expand=True)
        
        for entry in reversed(self.history):
            history_list.insert(tk.END, entry)
        
        scrollbar.config(command=history_list.yview)
        
        # Add context menu
        context_menu = tk.Menu(history_window, tearoff=0)
        context_menu.add_command(label="Copy", command=lambda: self.copy_history_item(history_list))
        context_menu.add_command(label="Insert", command=lambda: self.insert_history_item(history_list))
        context_menu.add_separator()
        context_menu.add_command(label="Clear History", command=lambda: self.clear_history(history_window))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        history_list.bind("<Button-3>", show_context_menu)

    def copy_history_item(self, history_list):
        """Copy selected history item to clipboard"""
        try:
            selection = history_list.get(history_list.curselection())
            self.root.clipboard_clear()
            self.root.clipboard_append(selection.split(" = ")[0])
        except:
            pass

    def insert_history_item(self, history_list):
        """Insert selected history item into calculator"""
        try:
            selection = history_list.get(history_list.curselection())
            expr = selection.split(" = ")[0]
            self.current_input = expr
            self.display_line1 = expr
            self.display_line2 = expr[-20:]
            self.result_shown = False
            self.update_display()
        except:
            pass

    def clear_history(self, window=None):
        """Clear the calculation history"""
        self.history = []
        if window:
            window.destroy()

    def save_history(self):
        """Save calculation history to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, "w") as f:
                    for entry in self.history:
                        f.write(entry + "\n")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save history: {e}")

    def load_history(self):
        """Load calculation history from file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, "r") as f:
                    self.history = [line.strip() for line in f.readlines()]
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load history: {e}")

    def copy_result(self):
        """Copy the current result to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.display_line2)

    def paste_from_clipboard(self):
        """Paste from clipboard to calculator input"""
        try:
            clipboard_content = self.root.clipboard_get()
            if clipboard_content:
                self.current_input += clipboard_content
                self.display_line1 = self.current_input
                self.display_line2 = self.current_input[-20:]
                self.result_shown = False
                self.update_display()
        except:
            pass

    def set_angle_mode(self, mode):
        """Set the angle calculation mode (DEG, RAD, GRAD)"""
        self.angle_mode = mode
        self.update_display()

    def set_calculation_mode(self, mode):
        """Set the calculation mode (COMP, STAT, etc.)"""
        self.calculation_mode = mode
        self.update_display()
        self.keyboard_notebook.select(self.calculation_mode.lower())

    def show_mode_menu(self):
        """Show a popup menu for mode selection"""
        mode_menu = tk.Menu(self.root, tearoff=0)
        mode_menu.add_command(label="COMP", command=lambda: self.set_calculation_mode("COMP"))
        mode_menu.add_command(label="STAT", command=lambda: self.set_calculation_mode("STAT"))
        mode_menu.add_command(label="TABLE", command=lambda: self.set_calculation_mode("TABLE"))
        mode_menu.add_command(label="EQN", command=lambda: self.set_calculation_mode("EQN"))
        mode_menu.add_separator()
        mode_menu.add_command(label="Matrix", command=lambda: self.set_calculation_mode("MATRIX"))
        
        try:
            mode_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            mode_menu.grab_release()

    def set_theme(self, theme_name):
        """Set the calculator theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.theme = self.themes[theme_name]
            self.apply_theme()
            self.settings["theme"] = theme_name
            self.save_settings()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current_state)
        self.settings["fullscreen"] = not current_state
        self.save_settings()

    def toggle_qr_display(self):
        """Toggle QR code display"""
        if self.qr_visible:
            self.qr_frame.pack_forget()
        else:
            # Generate a simple QR code (simulated)
            self.qr_canvas.delete("all")
            self.qr_canvas.create_rectangle(0, 0, 200, 200, fill="white")
            
            # Draw a simple QR pattern (just for show)
            for i in range(0, 200, 10):
                for j in range(0, 200, 10):
                    if (i + j) % 20 == 0:
                        self.qr_canvas.create_rectangle(i, j, i+10, j+10, fill="black")
            
            self.qr_frame.pack(pady=10)
        
        self.qr_visible = not self.qr_visible

    def update_time(self):
        """Update the time display in status bar"""
        now = datetime.now().strftime("%H:%M")
        self.time_display.config(text=now)
        self.root.after(60000, self.update_time)  # Update every minute

    def show_preferences(self):
        """Show preferences dialog"""
        pref_window = tk.Toplevel(self.root)
        pref_window.title("Preferences")
        pref_window.geometry("400x300")
        
        # Decimal places setting
        tk.Label(pref_window, text="Decimal Places:").pack(pady=(10, 0))
        decimal_spin = tk.Spinbox(
            pref_window, 
            from_=0, 
            to=15, 
            width=5,
            textvariable=tk.IntVar(value=self.decimal_places))
        decimal_spin.pack()
        
        # History checkbox
        history_var = tk.BooleanVar(value=self.settings.get("history_enabled", True))
        history_check = tk.Checkbutton(
            pref_window, 
            text="Enable Calculation History", 
            variable=history_var
        )
        history_check.pack(pady=10)
        
        # Save button
        save_btn = tk.Button(
            pref_window,
            text="Save Preferences",
            command=lambda: self.save_preferences(
                int(decimal_spin.get()),
                history_var.get(),
                pref_window
            )
        )
        save_btn.pack(pady=20)

    def save_preferences(self, decimal_places, history_enabled, window):
        """Save preferences from dialog"""
        self.decimal_places = decimal_places
        self.settings["decimal_places"] = decimal_places
        self.settings["history_enabled"] = history_enabled
        self.save_settings()
        window.destroy()
        self.update_display()

    def show_about(self):
        """Show about dialog"""
        about_text = (
            "Casio fx-991EX ClassWiz Emulator\n"
            "Version 1.0\n\n"
            "A Python-based emulator of the popular scientific calculator\n"
            "Created with Tkinter\n\n"
            "© 2023 Calculator Emulator Project"
        )
        messagebox.showinfo("About", about_text)

    def show_help(self):
        """Show help dialog"""
        help_text = (
            "Calculator Help\n\n"
            "Basic Operations:\n"
            "- Use number buttons for input\n"
            "- +, -, ×, ÷ for basic arithmetic\n"
            "- = to calculate result\n\n"
            "Special Functions:\n"
            "- SHIFT: Access secondary functions\n"
            "- ALPHA: Access alpha characters\n"
            "- MODE: Change calculation mode\n\n"
            "Advanced Features:\n"
            "- Matrix operations in Matrix mode\n"
            "- Equation solving in Equation mode\n"
            "- Scientific functions in Scientific tab"
        )
        messagebox.showinfo("Help", help_text)

    def scientific_function(self, func_name):
        """Handle scientific function button presses"""
        if func_name == "sinh":
            self.current_input += "math.sinh("
        elif func_name == "cosh":
            self.current_input += "math.cosh("
        elif func_name == "tanh":
            self.current_input += "math.tanh("
        elif func_name == "sinh⁻¹":
            self.current_input += "math.asinh("
        elif func_name == "cosh⁻¹":
            self.current_input += "math.acosh("
        elif func_name == "tanh⁻¹":
            self.current_input += "math.atanh("
        elif func_name == "x!":
            self.current_input += "math.factorial("
        elif func_name == "nPr":
            self.current_input += "math.perm("
        elif func_name == "nCr":
            self.current_input += "math.comb("
        elif func_name == "|x|":
            self.current_input += "abs("
        elif func_name == "gcd":
            self.current_input += "math.gcd("
        elif func_name == "lcm":
            self.current_input += "math.lcm("
        elif func_name == "mod":
            self.current_input += "%"
        elif func_name == "floor":
            self.current_input += "math.floor("
        elif func_name == "ceil":
            self.current_input += "math.ceil("
        elif func_name == "log₂":
            self.current_input += "math.log2("
        elif func_name == "logₓ":
            self.current_input += "math.log("
        elif func_name == "e^x":
            self.current_input += "math.exp("
        elif func_name == "10^x":
            self.current_input += "10**"
        elif func_name == "x^3":
            self.current_input += "**3"
        elif func_name == "∛":
            self.current_input += "**(1/3)"
        elif func_name == "Pol(":
            self.current_input += "math.polar("
        elif func_name == "Rec(":
            self.current_input += "math.rect("
        elif func_name == "→r∠θ":
            self.current_input += "abs("
        elif func_name == "→a+bi":
            self.current_input += "complex("
        elif func_name == "arg":
            self.current_input += "cmath.phase("
        elif func_name == "conj":
            self.current_input += "np.conj("
        elif func_name == "rand":
            self.current_input += "random.random()"
        elif func_name == "d/dx":
            self.current_input += "derivative("
        elif func_name == "∫":
            self.current_input += "integrate("
        elif func_name == "Σ":
            self.current_input += "sum("
        elif func_name == "Π":
            self.current_input += "product("
        
        self.display_line1 = self.current_input
        self.display_line2 = self.current_input[-20:]
        self.result_shown = False
        self.update_display()

    def update_matrix_display(self):
        """Update the matrix display based on current selection and dimensions"""
        # Clear existing entries
        for widget in self.matrix_display_frame.winfo_children():
            widget.destroy()
        
        # Get current matrix and dimensions
        matrix_name = self.matrix_var.get()
        rows = self.rows_var.get()
        cols = self.cols_var.get()
        
        # Update matrix dimensions
        self.matrix_dims[matrix_name] = (rows, cols)
        
        # Resize matrix data if needed
        current_matrix = self.matrix_data[matrix_name]
        if current_matrix.shape != (rows, cols):
            new_matrix = np.zeros((rows, cols))
            min_rows = min(rows, current_matrix.shape[0])
            min_cols = min(cols, current_matrix.shape[1])
            new_matrix[:min_rows, :min_cols] = current_matrix[:min_rows, :min_cols]
            self.matrix_data[matrix_name] = new_matrix
        
        # Create entry widgets for the matrix
        self.matrix_entries = []
        for i in range(rows):
            row_entries = []
            for j in range(cols):
                entry = tk.Entry(
                    self.matrix_display_frame,
                    width=6,
                    font=("Arial", 10),
                    justify="center"
                )
                entry.insert(0, str(self.matrix_data[matrix_name][i, j]))
                entry.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)
        
        # Add update button
        update_btn = tk.Button(
            self.matrix_display_frame,
            text="Update Matrix",
            command=self.update_matrix_values,
            bg=self.theme["bg_command"],
            fg=self.theme["fg_command"]
        )
        update_btn.grid(row=rows, columnspan=cols, pady=5)

    def update_matrix_values(self):
        """Update matrix values from entry widgets"""
        matrix_name = self.matrix_var.get()
        rows, cols = self.matrix_dims[matrix_name]
        
        for i in range(rows):
            for j in range(cols):
                try:
                    value = float(self.matrix_entries[i][j].get())
                    self.matrix_data[matrix_name][i, j] = value
                except ValueError:
                    messagebox.showerror("Error", "Invalid matrix entry")
                    return

    def resize_matrix(self):
        """Resize the current matrix"""
        self.update_matrix_display()

    def matrix_determinant(self):
        """Calculate determinant of current matrix"""
        matrix_name = self.matrix_var.get()
        matrix = self.matrix_data[matrix_name]
        
        try:
            det = np.linalg.det(matrix)
            self.show_matrix_result(f"det({matrix_name}) = {det:.4f}")
        except np.linalg.LinAlgError:
            messagebox.showerror("Error", "Matrix must be square to calculate determinant")

    def matrix_inverse(self):
        """Calculate inverse of current matrix"""
        matrix_name = self.matrix_var.get()
        matrix = self.matrix_data[matrix_name]
        
        try:
            inv = np.linalg.inv(matrix)
            self.show_matrix_result(f"Inverse of {matrix_name}:", inv)
        except np.linalg.LinAlgError:
            messagebox.showerror("Error", "Matrix is singular or not square")

    def matrix_transpose(self):
        """Calculate transpose of current matrix"""
        matrix_name = self.matrix_var.get()
        matrix = self.matrix_data[matrix_name]
        transpose = matrix.T
        self.show_matrix_result(f"Transpose of {matrix_name}:", transpose)

    def matrix_multiply(self):
        """Multiply two matrices"""
        try:
            result = np.matmul(self.matrix_data["A"], self.matrix_data["B"])
            self.show_matrix_result("A × B =", result)
        except ValueError:
            messagebox.showerror("Error", "Matrix dimensions incompatible for multiplication")

    def matrix_solve(self):
        """Solve system of linear equations"""
        matrix_name = self.matrix_var.get()
        matrix = self.matrix_data[matrix_name]
        
        # For simplicity, assume right-hand side is matrix B
        try:
            solution = np.linalg.solve(matrix, self.matrix_data["B"])
            self.show_matrix_result("Solution:", solution)
        except np.linalg.LinAlgError:
            messagebox.showerror("Error", "Cannot solve system (singular matrix or wrong dimensions)")

    def show_matrix_result(self, title, matrix=None):
        """Show matrix calculation result"""
        result_window = tk.Toplevel(self.root)
        result_window.title("Matrix Result")
        
        tk.Label(result_window, text=title, font=("Arial", 12, "bold")).pack(pady=5)
        
        if matrix is not None:
            if isinstance(matrix, np.ndarray):
                # Display matrix
                frame = tk.Frame(result_window)
                frame.pack(pady=10)
                
                for i in range(matrix.shape[0]):
                    for j in range(matrix.shape[1]):
                        tk.Label(
                            frame,
                            text=f"{matrix[i,j]:.4f}",
                            relief=tk.RIDGE,
                            width=8,
                            padx=5,
                            pady=5
                        ).grid(row=i, column=j, padx=2, pady=2)
            else:
                # Display scalar result
                tk.Label(result_window, text=str(matrix)).pack()
        
        tk.Button(
            result_window,
            text="Close",
            command=result_window.destroy
        ).pack(pady=10)

    def update_equation_interface(self):
        """Update the equation interface based on selected type"""
        for widget in self.eq_display_frame.winfo_children():
            widget.destroy()
        
        eq_type = self.eq_type_var.get()
        
        if eq_type == "Linear":
            self.create_linear_equation_interface()
        elif eq_type == "Quadratic":
            self.create_quadratic_equation_interface()
        elif eq_type == "Cubic":
            self.create_cubic_equation_interface()
        elif eq_type == "System2":
            self.create_system2_equation_interface()
        elif eq_type == "System3":
            self.create_system3_equation_interface()

    def create_linear_equation_interface(self):
        """Create interface for linear equation (ax + b = 0)"""
        tk.Label(self.eq_display_frame, text="ax + b = 0", font=("Arial", 12)).pack(pady=10)
        
        coeff_frame = tk.Frame(self.eq_display_frame)
        coeff_frame.pack(pady=5)
        
        tk.Label(coeff_frame, text="a:").grid(row=0, column=0, padx=5)
        self.a_entry = tk.Entry(coeff_frame, width=10)
        self.a_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(coeff_frame, text="b:").grid(row=1, column=0, padx=5)
        self.b_entry = tk.Entry(coeff_frame, width=10)
        self.b_entry.grid(row=1, column=1, padx=5)
        
        self.equation_coefficients = [self.a_entry, self.b_entry]

    def create_quadratic_equation_interface(self):
        """Create interface for quadratic equation (ax² + bx + c = 0)"""
        tk.Label(self.eq_display_frame, text="ax² + bx + c = 0", font=("Arial", 12)).pack(pady=10)
        
        coeff_frame = tk.Frame(self.eq_display_frame)
        coeff_frame.pack(pady=5)
        
        tk.Label(coeff_frame, text="a:").grid(row=0, column=0, padx=5)
        self.a_entry = tk.Entry(coeff_frame, width=10)
        self.a_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(coeff_frame, text="b:").grid(row=1, column=0, padx=5)
        self.b_entry = tk.Entry(coeff_frame, width=10)
        self.b_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(coeff_frame, text="c:").grid(row=2, column=0, padx=5)
        self.c_entry = tk.Entry(coeff_frame, width=10)
        self.c_entry.grid(row=2, column=1, padx=5)
        
        self.equation_coefficients = [self.a_entry, self.b_entry, self.c_entry]

    def create_cubic_equation_interface(self):
        """Create interface for cubic equation (ax³ + bx² + cx + d = 0)"""
        tk.Label(self.eq_display_frame, text="ax³ + bx² + cx + d = 0", font=("Arial", 12)).pack(pady=10)
        
        coeff_frame = tk.Frame(self.eq_display_frame)
        coeff_frame.pack(pady=5)
        
        tk.Label(coeff_frame, text="a:").grid(row=0, column=0, padx=5)
        self.a_entry = tk.Entry(coeff_frame, width=10)
        self.a_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(coeff_frame, text="b:").grid(row=1, column=0, padx=5)
        self.b_entry = tk.Entry(coeff_frame, width=10)
        self.b_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(coeff_frame, text="c:").grid(row=2, column=0, padx=5)
        self.c_entry = tk.Entry(coeff_frame, width=10)
        self.c_entry.grid(row=2, column=1, padx=5)
        
        tk.Label(coeff_frame, text="d:").grid(row=3, column=0, padx=5)
        self.d_entry = tk.Entry(coeff_frame, width=10)
        self.d_entry.grid(row=3, column=1, padx=5)
        
        self.equation_coefficients = [self.a_entry, self.b_entry, self.c_entry, self.d_entry]
    def create_system2_equation_interface(self):
        """Create interface for 2x2 system of equations"""
        tk.Label(self.eq_display_frame, text="System of 2 Equations", font=("Arial", 12)).pack(pady=10)
        
        # Equation 1: a1x + b1y = c1
        eq1_frame = tk.Frame(self.eq_display_frame)
        eq1_frame.pack(pady=5)
        
        tk.Label(eq1_frame, text="a₁:").grid(row=0, column=0, padx=5)
        self.a1_entry = tk.Entry(eq1_frame, width=8)
        self.a1_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(eq1_frame, text="x + b₁:").grid(row=0, column=2, padx=5)
        self.b1_entry = tk.Entry(eq1_frame, width=8)
        self.b1_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(eq1_frame, text="y = c₁:").grid(row=0, column=4, padx=5)
        self.c1_entry = tk.Entry(eq1_frame, width=8)
        self.c1_entry.grid(row=0, column=5, padx=5)
        
        # Equation 2: a2x + b2y = c2
        eq2_frame = tk.Frame(self.eq_display_frame)
        eq2_frame.pack(pady=5)
        
        tk.Label(eq2_frame, text="a₂:").grid(row=0, column=0, padx=5)
        self.a2_entry = tk.Entry(eq2_frame, width=8)
        self.a2_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(eq2_frame, text="x + b₂:").grid(row=0, column=2, padx=5)
        self.b2_entry = tk.Entry(eq2_frame, width=8)
        self.b2_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(eq2_frame, text="y = c₂:").grid(row=0, column=4, padx=5)
        self.c2_entry = tk.Entry(eq2_frame, width=8)
        self.c2_entry.grid(row=0, column=5, padx=5)
        
        self.equation_coefficients = [
            self.a1_entry, self.b1_entry, self.c1_entry,
            self.a2_entry, self.b2_entry, self.c2_entry
        ]

    def create_system3_equation_interface(self):
        """Create interface for 3x3 system of equations"""
        tk.Label(self.eq_display_frame, text="System of 3 Equations", font=("Arial", 12)).pack(pady=10)
        
        # Equation 1: a1x + b1y + c1z = d1
        eq1_frame = tk.Frame(self.eq_display_frame)
        eq1_frame.pack(pady=5)
        
        tk.Label(eq1_frame, text="a₁:").grid(row=0, column=0, padx=5)
        self.a1_entry = tk.Entry(eq1_frame, width=6)
        self.a1_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(eq1_frame, text="x + b₁:").grid(row=0, column=2, padx=5)
        self.b1_entry = tk.Entry(eq1_frame, width=6)
        self.b1_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(eq1_frame, text="y + c₁:").grid(row=0, column=4, padx=5)
        self.c1_entry = tk.Entry(eq1_frame, width=6)
        self.c1_entry.grid(row=0, column=5, padx=5)
        
        tk.Label(eq1_frame, text="z = d₁:").grid(row=0, column=6, padx=5)
        self.d1_entry = tk.Entry(eq1_frame, width=6)
        self.d1_entry.grid(row=0, column=7, padx=5)
        
        # Equation 2: a2x + b2y + c2z = d2
        eq2_frame = tk.Frame(self.eq_display_frame)
        eq2_frame.pack(pady=5)
        
        tk.Label(eq2_frame, text="a₂:").grid(row=0, column=0, padx=5)
        self.a2_entry = tk.Entry(eq2_frame, width=6)
        self.a2_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(eq2_frame, text="x + b₂:").grid(row=0, column=2, padx=5)
        self.b2_entry = tk.Entry(eq2_frame, width=6)
        self.b2_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(eq2_frame, text="y + c₂:").grid(row=0, column=4, padx=5)
        self.c2_entry = tk.Entry(eq2_frame, width=6)
        self.c2_entry.grid(row=0, column=5, padx=5)
        
        tk.Label(eq2_frame, text="z = d₂:").grid(row=0, column=6, padx=5)
        self.d2_entry = tk.Entry(eq2_frame, width=6)
        self.d2_entry.grid(row=0, column=7, padx=5)
        
        # Equation 3: a3x + b3y + c3z = d3
        eq3_frame = tk.Frame(self.eq_display_frame)
        eq3_frame.pack(pady=5)
        
        tk.Label(eq3_frame, text="a₃:").grid(row=0, column=0, padx=5)
        self.a3_entry = tk.Entry(eq3_frame, width=6)
        self.a3_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(eq3_frame, text="x + b₃:").grid(row=0, column=2, padx=5)
        self.b3_entry = tk.Entry(eq3_frame, width=6)
        self.b3_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(eq3_frame, text="y + c₃:").grid(row=0, column=4, padx=5)
        self.c3_entry = tk.Entry(eq3_frame, width=6)
        self.c3_entry.grid(row=0, column=5, padx=5)
        
        tk.Label(eq3_frame, text="z = d₃:").grid(row=0, column=6, padx=5)
        self.d3_entry = tk.Entry(eq3_frame, width=6)
        self.d3_entry.grid(row=0, column=7, padx=5)
        
        self.equation_coefficients = [
            self.a1_entry, self.b1_entry, self.c1_entry, self.d1_entry,
            self.a2_entry, self.b2_entry, self.c2_entry, self.d2_entry,
            self.a3_entry, self.b3_entry, self.c3_entry, self.d3_entry
        ]

    def solve_equation(self):
        """Solve the current equation based on selected type"""
        try:
            # Get coefficients from entries
            coefficients = []
            for entry in self.equation_coefficients:
                value = entry.get()
                if not value:
                    value = "0"  # Default to 0 if empty
                coefficients.append(float(value))
            
            eq_type = self.eq_type_var.get()
            result_window = tk.Toplevel(self.root)
            result_window.title("Equation Solution")
            
            if eq_type == "Linear":
                # ax + b = 0
                a, b = coefficients
                if a == 0:
                    if b == 0:
                        solution = "Infinite solutions (0 = 0)"
                    else:
                        solution = "No solution (contradiction)"
                else:
                    x = -b / a
                    solution = f"x = {x:.6f}"
                
                tk.Label(result_window, text=solution, font=("Arial", 14)).pack(pady=20)
            
            elif eq_type == "Quadratic":
                # ax² + bx + c = 0
                a, b, c = coefficients
                discriminant = b**2 - 4*a*c
                
                if discriminant > 0:
                    x1 = (-b + math.sqrt(discriminant)) / (2*a)
                    x2 = (-b - math.sqrt(discriminant)) / (2*a)
                    solution = f"x₁ = {x1:.6f}\nx₂ = {x2:.6f}"
                elif discriminant == 0:
                    x = -b / (2*a)
                    solution = f"x = {x:.6f} (double root)"
                else:
                    real = -b / (2*a)
                    imag = math.sqrt(-discriminant) / (2*a)
                    solution = f"x₁ = {real:.6f} + {imag:.6f}i\nx₂ = {real:.6f} - {imag:.6f}i"
                
                tk.Label(result_window, text=solution, font=("Arial", 14)).pack(pady=20)
            
            elif eq_type == "Cubic":
                # ax³ + bx² + cx + d = 0
                a, b, c, d = coefficients
                # Using numpy roots function for simplicity
                roots = np.roots([a, b, c, d])
                solution = ""
                for i, root in enumerate(roots):
                    if np.isreal(root):
                        solution += f"x_{i+1} = {root.real:.6f}\n"
                    else:
                        solution += f"x_{i+1} = {root.real:.6f} + {root.imag:.6f}i\n"
                
                tk.Label(result_window, text=solution.strip(), font=("Arial", 14)).pack(pady=20)
            
            elif eq_type == "System2":
                # 2x2 system
                a1, b1, c1, a2, b2, c2 = coefficients
                # Solve using numpy
                A = np.array([[a1, b1], [a2, b2]])
                B = np.array([c1, c2])
                try:
                    solution = np.linalg.solve(A, B)
                    result_text = f"x = {solution[0]:.6f}\ny = {solution[1]:.6f}"
                except np.linalg.LinAlgError:
                    det = np.linalg.det(A)
                    if det == 0:
                        if a1/a2 == b1/b2 == c1/c2:
                            result_text = "Infinite solutions (dependent system)"
                        else:
                            result_text = "No solution (inconsistent system)"
                    else:
                        result_text = "Error solving system"
                
                tk.Label(result_window, text=result_text, font=("Arial", 14)).pack(pady=20)
            
            elif eq_type == "System3":
                # 3x3 system
                a1, b1, c1, d1, a2, b2, c2, d2, a3, b3, c3, d3 = coefficients
                A = np.array([[a1, b1, c1], [a2, b2, c2], [a3, b3, c3]])
                B = np.array([d1, d2, d3])
                try:
                    solution = np.linalg.solve(A, B)
                    result_text = f"x = {solution[0]:.6f}\ny = {solution[1]:.6f}\nz = {solution[2]:.6f}"
                except np.linalg.LinAlgError:
                    det = np.linalg.det(A)
                    if det == 0:
                        result_text = "System may have no solution or infinite solutions"
                    else:
                        result_text = "Error solving system"
                
                tk.Label(result_window, text=result_text, font=("Arial", 14)).pack(pady=20)
            
            # Add close button
            tk.Button(
                result_window,
                text="Close",
                command=result_window.destroy
            ).pack(pady=10)
            
            # Add to history
            self.add_to_history(f"Solved {eq_type} equation: {solution}")
        
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric coefficients")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def run(self):
        """Run the calculator application"""
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    calculator = FX991EXCalculator(root)
    calculator.run()
 
