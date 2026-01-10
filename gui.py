import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import sys
import os
import re
import subprocess
import tempfile
import shutil

# ---DEPENDENCIES---
try:
    from PIL import Image, ImageTk
except ImportError:
    pass

# ---COMPILER MODULES---
try:
    import lexer as lexer_mod 
    import parser as parser_mod 
    from semantic import SemanticAnalyzer
    from codegen import CodeGenerator
except ImportError as e:
    # Fallback to prevent IDE crash during GUI testing if modules are missing
    lexer_mod = None
    pass

try:
    from ast_viz import ASTVisualizer
except ImportError:
    ASTVisualizer = None

# Global variable to store the path of the currently generated AST image
current_ast_image_path = None


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # IN DEV: Use the directory where this script is located
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

# ==========================================
# SYNTAX HIGHLIGHTER CLASS
# ==========================================

class SyntaxHighlighter:
    """
    Handles real-time syntax highlighting for Python and JavaScript code.
    Based on Regex matching and Tkinter tags.
    """
    def __init__(self, text_widget, lang='python'):
        self.text_widget = text_widget
        self.lang = lang
        
        self.tags = {
            'keyword': '#d73a49',
            'builtin': '#6f42c1',
            'string':  '#22863a',
            'number':  '#005cc5',
            'comment': '#6a737d',
            'bool':    '#005cc5',
            'warning': '#e67e22'
        }
        for tag, color in self.tags.items():
            self.text_widget.tag_config(tag, foreground=color)

    def highlight(self, event=None):
        """Applies highlighting rules to the entire text content."""
        content = self.text_widget.get("1.0", tk.END)
        # Clear old tags
        for tag in self.tags:
            self.text_widget.tag_remove(tag, "1.0", tk.END)
        
        if self.lang == 'python':
            self._highlight_python(content)
        elif self.lang == 'js':
            self._highlight_js(content)

    def _apply_regex(self, pattern, tag, content):
        """Helper to apply a specific tag to all regex matches."""
        for match in re.finditer(pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_widget.tag_add(tag, start, end)

    def _highlight_python(self, content):
        keywords = r'\b(def|return|if|else|elif|while|for|in|and|or|not|class|try|except|import|from)\b'
        self._apply_regex(keywords, 'keyword', content)
        builtins = r'\b(print|range|input|len|str|int)\b'
        self._apply_regex(builtins, 'builtin', content)
        bools = r'\b(True|False|None)\b'
        self._apply_regex(bools, 'bool', content)
        self._apply_regex(r'\b\d+\b', 'number', content)
        self._apply_regex(r'(".*?"|\'.*?\')', 'string', content)
        self._apply_regex(r'#.*', 'comment', content)

    def _highlight_js(self, content):
        keywords = r'\b(function|return|if|else|var|let|const|for|while|switch|case|break)\b'
        self._apply_regex(keywords, 'keyword', content)
        self._apply_regex(r'\b(console|log)\b', 'builtin', content)
        self._apply_regex(r'\b(true|false|null|undefined)\b', 'bool', content)
        self._apply_regex(r'\b\d+\b', 'number', content)
        self._apply_regex(r'(".*?"|\'.*?\')', 'string', content)
        self._apply_regex(r'//.*', 'comment', content)
        self._apply_regex(r'/\* WARNING:.*?\*/', 'warning', content)
        self._apply_regex(r'/\*(?!\s*WARNING:).*?\*/', 'comment', content)

# ==========================================
# CORE LOGIC (Callbacks)
# ==========================================

def compile_source():
    """
    Main compilation workflow:
    1. Lexing & Parsing
    2. Semantic Analysis
    3. Code Generation (Python -> JS)
    """
    source_code = txt_input.get("1.0", tk.END).strip()
    if source_code: source_code += "\n"
    
    if not source_code:
        messagebox.showwarning("Warning", "Source code is empty!")
        return

    txt_output.config(state=tk.NORMAL)
    txt_output.delete("1.0", tk.END)

    if lexer_mod: lexer_mod.errors = []
    if parser_mod: parser_mod.errors = []
    
    try:
        # Parsing
        if lexer_mod and hasattr(lexer_mod, 'lexer'):
            lexer_mod.lexer.lineno = 1
        
        # Safety check for imports
        if not parser_mod: raise Exception("Compiler modules not found.")

        ast = parser_mod.parser.parse(source_code, lexer=lexer_mod.lexer)

        found_errors = []
        if lexer_mod and hasattr(lexer_mod, 'errors'):
            found_errors.extend(lexer_mod.errors)
        if parser_mod and hasattr(parser_mod, 'errors'):
            found_errors.extend(parser_mod.errors)

        if ast is None or len(found_errors) > 0:
            error_text = "/* COMPILATION FAILED */\n\n"
            if found_errors:
                error_text += "\n".join(found_errors)
            else:
                error_text += "Unknown Syntax Error (Parser returned None)"

            raise Exception(error_text)

        # Semantic
        semantic = SemanticAnalyzer()
        semantic.visit(ast)
        
        # CodeGen
        codegen = CodeGenerator() 
        js_code = codegen.generate(ast)
        
        # Output
        txt_output.insert(tk.END, js_code)
        highlighter_js.highlight()
        status_label.config(text="Compilation successful ✅", fg="#27ae60")

        # Activate RUN button
        btn_run.config(state=tk.NORMAL, bg="#34C540") 

    except Exception as e:
        txt_output.insert(tk.END, f"/* ERROR */\n\n{str(e)}")
        status_label.config(text="Error detected ❌", fg="#c0392b")
        # Deactivate RUN button
        btn_run.config(state=tk.DISABLED, bg="#bdc3c7")

def open_file():
    """Opens a file dialog to load Python code into the input box."""
    filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt")])
    if filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
            txt_input.delete("1.0", tk.END)
            txt_input.insert(tk.END, code)
            highlighter_py.highlight()
        status_label.config(text=f"Loaded: {os.path.basename(filepath)}")

def copy_js():
    """Copies the content of the Output box to the system clipboard."""
    js_code = txt_output.get("1.0", tk.END).strip()
    if js_code:
        root.clipboard_clear()
        root.clipboard_append(js_code)
        messagebox.showinfo("Info", "JS Code copied to clipboard!")

def export_js():
    """Saves the generated JavaScript code to a file."""
    js_code = txt_output.get("1.0", tk.END).strip()
    if js_code:
        filepath = filedialog.asksaveasfilename(defaultextension=".js", filetypes=[("JS Files", "*.js")])
        if filepath:
            with open(filepath, "w") as f: f.write(js_code)
            messagebox.showinfo("Info", "File saved successfully.")

def run_js():
    """
    Executes the generated JS code using Node.js (must be installed).
    Captures stdout/stderr and displays it in a new window.
    """
    # Get JS code
    js_code = txt_output.get("1.0", tk.END).strip()
    if not js_code: return

    # Save to temp file
    temp_file = "temp_run.js"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(js_code)

    try:
        # Run with Node.js
        result = subprocess.run(
            ["node", temp_file], 
            capture_output=True, 
            text=True, 
            timeout=5,     # 5s timeout to prevent infinite loops
            shell=True     # Required on Windows
        )
        
        output = result.stdout + result.stderr
        
    except FileNotFoundError:
        output = "ERROR: Node.js not found.\nPlease install Node.js from https://nodejs.org/"
    except subprocess.TimeoutExpired:
        output = "ERROR: Execution timed out (Infinite loop?)"
    except Exception as e:
        output = f"SYSTEM ERROR: {e}"
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    # Show output window
    top = tk.Toplevel(root)
    top.title("Terminal Output")
    top.geometry("600x400")
    top.configure(bg="#1e1e1e")

    tk.Label(top, text=">_ Console Output", fg="#bdc3c7", bg="#1e1e1e", font=("Consolas", 10, "bold")).pack(anchor="w", padx=10, pady=5)

    console_txt = scrolledtext.ScrolledText(top, font=("Consolas", 11), bg="#000000", fg="#00ff00", insertbackground="white")
    console_txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    console_txt.insert(tk.END, output)
    console_txt.config(state=tk.DISABLED)

def show_ast():
    """
    Generates and displays the AST Graph using Graphviz.
    Saves the image in a temp folder and enables the Save button.
    """
    global current_ast_image_path
    
    code = txt_input.get("1.0", tk.END).strip() + "\n"
    
    if len(code) <= 1:
        messagebox.showwarning("Warning", "Python code is empty!")
        return

    # Reset lexer
    if lexer_mod: lexer_mod.lexer.lineno = 1
    
    try:
        ast = parser_mod.parser.parse(code, lexer=lexer_mod.lexer)
    except Exception as e:
        messagebox.showerror("Parser Error", f"Critical exception during parsing:\n{e}")
        return

    if ast is None:
        messagebox.showerror("Syntax Error", 
                             "The parser returned None.\n"
                             "Probable syntax error in Python code.\n"
                             "Check for unclosed parentheses or blocks.")
        return

    # Generate Graph
    if ASTVisualizer:
        viz = ASTVisualizer()
        
        temp_dir = tempfile.gettempdir()
        temp_base_path = os.path.join(temp_dir, "temp_ast_preview")
        
        output_path = viz.generate(ast, output_file=temp_base_path)

        if output_path and os.path.exists(output_path):
            current_ast_image_path = output_path
            
            # Enable Save Button
            btn_save_ast.config(state=tk.NORMAL, cursor="hand2")
            
            try:
                if os.name == 'nt': # Windows
                    os.startfile(output_path)
                else: # Mac / Linux
                    import subprocess
                    subprocess.call(('open', output_path))
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open image:\n{e}")
        else:
            messagebox.showerror("Graphviz Error", "Cannot create PNG file.\nIs Graphviz installed and added to PATH?")
    else:
        messagebox.showerror("Error", "Module ast_visualizer not found.")

def save_ast():
    """Saves the currently generated AST image to a user-defined location."""
    global current_ast_image_path
    
    if not current_ast_image_path or not os.path.exists(current_ast_image_path):
        messagebox.showerror("Error", "No AST image generated to save.")
        return

    target_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        title="Save AST Graph",
        initialfile="ast_graph.png"
    )

    if target_path:
        try:
            shutil.copy(current_ast_image_path, target_path)
            messagebox.showinfo("Success", f"Graph saved to:\n{target_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot save file:\n{e}")

def clear_input():
    txt_input.delete("1.0", tk.END)
    highlighter_py.highlight()

def clear_output():
    txt_output.config(state=tk.NORMAL)
    txt_output.delete("1.0", tk.END)
    btn_run.config(state=tk.DISABLED, bg="#bdc3c7")

# ==========================================
# GUI SETUP & LAYOUT
# ==========================================
BG_COLOR = "#f0f2f5"
CARD_BG = "#ffffff"
BTN_BLUE = "#1976D2"
BORDER_COLOR = "#d1d5db"
FONT_CODE = ("Consolas", 11)

root = tk.Tk()
root.title("Py2JS Transpiler")
root.geometry("1050x720")
root.configure(bg=BG_COLOR)

# ---WINDOW ICON---
try:
    icon_path = resource_path("imgs/app_icon.ico")
    root.iconbitmap(icon_path)
except Exception:
    pass

# ---LOAD HEADER ICONS---
try:
    path_py = resource_path("imgs/python_icon.png")
    py_img_raw = Image.open(path_py).resize((35, 35), Image.Resampling.LANCZOS)
    py_icon = ImageTk.PhotoImage(py_img_raw)
    
    path_js = resource_path("imgs/js_icon.png")
    js_img_raw = Image.open(path_js).resize((35, 35), Image.Resampling.LANCZOS)
    js_icon = ImageTk.PhotoImage(js_img_raw)
except Exception as e:
    print(f"Icons not found: {e}")
    py_icon = None
    js_icon = None


# ---HEADER LAYOUT (3 Columns)---
header_frame = tk.Frame(root, bg=BG_COLOR)
header_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
header_frame.columnconfigure(0, weight=1)
header_frame.columnconfigure(1, weight=0)
header_frame.columnconfigure(2, weight=1)

# 1. Python Side (Left)
h_py_frame = tk.Frame(header_frame, bg=BG_COLOR)
h_py_frame.grid(row=0, column=0) 

if py_icon:
    tk.Label(h_py_frame, image=py_icon, bg=BG_COLOR).pack(side=tk.LEFT, padx=10)
tk.Label(h_py_frame, text="Python", font=("Segoe UI", 18, "bold"), bg=BG_COLOR, fg="#333").pack(side=tk.LEFT)

# 2. Arrow (Center)
tk.Label(header_frame, text="➔", font=("Arial", 24), bg=BG_COLOR, fg="#bdc3c7").grid(row=0, column=1, padx=(32, 0))

# 3. JavaScript Side (Right)
h_js_frame = tk.Frame(header_frame, bg=BG_COLOR)
h_js_frame.grid(row=0, column=2)

tk.Label(h_js_frame, text="JavaScript", font=("Segoe UI", 18, "bold"), bg=BG_COLOR, fg="#333").pack(side=tk.LEFT)
if js_icon:
    tk.Label(h_js_frame, image=js_icon, bg=BG_COLOR).pack(side=tk.LEFT, padx=10)


# ---TRASH ICON---
try:
    trash_path = resource_path("imgs/trash.png")
    pil_img = Image.open(trash_path).resize((20, 20), Image.Resampling.LANCZOS)
    icon_trash = ImageTk.PhotoImage(pil_img)
except Exception as e:
    icon_trash = None


# ---MAIN CONTAINER---
main_container = tk.Frame(root, bg=BG_COLOR)
main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

main_container.columnconfigure(0, weight=1)
main_container.columnconfigure(1, weight=1)
main_container.rowconfigure(1, weight=1) 

# ---LEFT SIDE (PYTHON INPUT)---
if icon_trash:
    btn_clean_py = tk.Button(main_container, image=icon_trash, command=clear_input, 
                             bg=BG_COLOR, activebackground=BG_COLOR, 
                             bd=0, highlightthickness=0, relief=tk.FLAT, cursor="hand2")
else:
    btn_clean_py = tk.Button(main_container, text="🗑️", command=clear_input, bg=BG_COLOR, bd=0)

btn_clean_py.grid(row=0, column=0, sticky="sw", padx=(0, 0), pady=(0, 5))

frame_py = tk.Frame(main_container, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1)
frame_py.grid(row=1, column=0, sticky="nsew", padx=(0, 15))

txt_input = scrolledtext.ScrolledText(frame_py, font=FONT_CODE, bg=CARD_BG, fg="#333", relief=tk.FLAT, undo=True)
txt_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


# ---RIGHT SIDE (JS OUTPUT)---
if icon_trash:
    btn_clean_js = tk.Button(main_container, image=icon_trash, command=clear_output, 
                             bg=BG_COLOR, activebackground=BG_COLOR, 
                             bd=0, highlightthickness=0, relief=tk.FLAT, cursor="hand2")
else:
    btn_clean_js = tk.Button(main_container, text="🗑️", command=clear_output, bg=BG_COLOR, bd=0)

btn_clean_js.grid(row=0, column=1, sticky="se", padx=(0, 0), pady=(0, 5))

frame_js = tk.Frame(main_container, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1)
frame_js.grid(row=1, column=1, sticky="nsew", padx=(15, 0))

txt_output = scrolledtext.ScrolledText(frame_js, font=FONT_CODE, bg=CARD_BG, fg="#333", relief=tk.FLAT)
txt_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Initialize Highlighters
highlighter_py = SyntaxHighlighter(txt_input, 'python')
highlighter_js = SyntaxHighlighter(txt_output, 'js')
txt_input.bind('<KeyRelease>', highlighter_py.highlight)


# ---BOTTOM BAR (CONTROLS)---
bottom_bar = tk.Frame(root, bg=BG_COLOR)
bottom_bar.pack(fill=tk.X, pady=20, padx=20)

# Left Group (Open, AST)
f_left = tk.Frame(bottom_bar, bg=BG_COLOR)
f_left.pack(side=tk.LEFT)

tk.Button(f_left, text="📂 Open File", command=open_file, bg="white", relief=tk.GROOVE).pack(side=tk.LEFT, padx=5)

# AST Buttons (Tree + Disk)
btn_show_ast = tk.Button(f_left, text="🌳 Show AST", command=show_ast, 
                         bg="white", relief=tk.GROOVE, cursor="hand2")
btn_show_ast.pack(side=tk.LEFT, padx=(5, 0))

btn_save_ast = tk.Button(f_left, text="💾", command=save_ast, 
                         bg="white", relief=tk.GROOVE, 
                         state=tk.DISABLED, cursor="arrow")
btn_save_ast.pack(side=tk.LEFT, padx=(0, 5))

# Center Button (Convert)
tk.Button(bottom_bar, text="Convert", command=compile_source, bg=BTN_BLUE, fg="white", 
          font=("Segoe UI", 12, "bold"), width=15, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, expand=True, padx=(15, 0))

# Right Group (Run, Copy, Export)
f_right = tk.Frame(bottom_bar, bg=BG_COLOR)
f_right.pack(side=tk.RIGHT)

btn_run = tk.Button(f_right, text="▶ Run JS", command=run_js, 
                    bg="#908A8A", fg="white", 
                    font=("Segoe UI", 10, "bold"), relief=tk.FLAT, cursor="hand2",
                    state=tk.DISABLED) 
btn_run.pack(side=tk.LEFT, padx=(0, 10))

tk.Button(f_right, text="📋 Copy", command=copy_js, bg="white", relief=tk.GROOVE).pack(side=tk.LEFT, padx=5)
tk.Button(f_right, text="↗ Export", command=export_js, bg="white", relief=tk.GROOVE).pack(side=tk.LEFT)

# Status Bar
status_label = tk.Label(root, text="Ready", font=("Arial", 9), bg=BG_COLOR, fg="#777", anchor="e")
status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5))

root.mainloop()