# 🐍 Py2JS Transpiler

**Py2JS** is a comprehensive educational compiler that translates Python source code into modern JavaScript.
Written entirely in Python, it features a full **Graphical User Interface (GUI)**, an **Abstract Syntax Tree (AST) Visualizer**, and a complete transpilation pipeline (Lexer → Parser → Semantic Analysis → Code Generation).

Project developed for the Formal Languages and Compilers course at Politecnio di Bari. 

Group name: Nabuk

---

## ✨ Features

### 🖥️ Graphical Interface (GUI)
- **Interactive Editor**: Built with Tkinter, featuring syntax highlighting for both Python (input) and JavaScript (output).
- **Real-time Feedback**: Status bar indicating compilation success or specific errors.
- **One-Click Execution**: Integrated "Run JS" button to execute the generated code immediately via Node.js.
- **File Management**: Load Python scripts, save AST images, and export JavaScript files.

### ⚙️ Compiler Pipeline
1.  **Lexer (`ply.lex`)**: Handles tokenization, including Python's complex indentation rules via a custom wrapper.
2.  **Parser (`ply.yacc`)**: Constructs the Abstract Syntax Tree (AST) using formal grammar rules.
3.  **Semantic Analyzer**:
    - Performs static type checking (e.g., prevents adding strings to integers).
    - Manages variable scopes (Global vs. Function scope).
    - Validates function arguments and return types.
4.  **Code Generator**:
    - Translates AST into ES6+ JavaScript.
    - Handles variable declarations (`let`).
    - Converts Python constructs (e.g., `range()`, `print()`) to JS equivalents.

### 🌳 Visualization
- **AST Graph**: Uses Graphviz to render the parsed syntax tree, helping users understand how the compiler "sees" the code.

---

## 🛠️ Supported Syntax

Py2JS supports a specific subset of the Python language mapped to JavaScript:

| Concept | Python Input | JavaScript Output |
| :--- | :--- | :--- |
| **Variables** | `x = 42` | `let x = 42;` |
| **Data Types** | `int`, `str`, `bool` | `Number`, `String`, `Boolean` |
| **Arithmetic** | `+`, `-`, `*`, `/` | `+`, `-`, `*`, `/` |
| **Logic** | `and`, `or`, `not` | `&&`, `||`, `!` |
| **Loops** | `for i in range(5):` | `for (let i = 0; i < 5; i++) {` |
| **Conditionals**| `if`, `elif`, `else` | `if`, `else if`, `else` |
| **Functions** | `def add(a, b):` | `function add(a, b) {` |
| **I/O** | `print("Hello")`, `input()` | `console.log("Hello");`, `prompt()` |

---

## 📂 Semantic Analysis and Testing

Regarding the symbol table and semantic analysis, the repository contains two versions:

* **`semantic.py`**: This is the **main and updated file**. It should be used for the standard execution of the project.
* **`semantic_static.py`**: This is the **legacy version**. It is kept in the repository solely for benchmarking and comparison purposes.

### Comparison Tool
We have provided a utility script to verify consistency between the two versions:

* **`tester_symbol_table.py`**: This script allows you to view the final status of the symbol table for the specific version of semantic that you have set. You can compare the two final statuses by running the test one at a time.

---


## 🌐 Virtual Environment (Recommended)

Before installing the dependencies, it is highly recommended to create a virtual environment to keep the project libraries isolated from your global Python system.

1.  **Create the virtual environment:**
    ```bash
    python -m venv venv
    ```

2.  **Activate the environment:**
    -   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    -   **macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```
        
## 📦 Installation

### Prerequisites
To run all features of Py2JS, you need:
1.  **Python 3.10+**
2.  **Graphviz (Software)**: Required for AST visualization. [Download here](https://graphviz.org/download/).
3.  **Node.js**: Required for the "Run JS" feature. [Download here](https://nodejs.org/).

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/piergiuseppe51/FLC_PROJECT.git](https://github.com/piergiuseppe51/FLC_PROJECT.git)
   cd FLC_PROJECT

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    python gui.py
    ```

---

## 🏗️ Build Executable

This project includes **PyInstaller** support to create a standalone executable (`.exe` on Windows).

Run the following command in your terminal:

```bash
pyinstaller --noconsole --onefile --name="Py2JS" --icon="imgs/app_icon.ico" --add-data "imgs;imgs" gui.py
```

---

## 👨‍💻 Authors

- **Andrea Paci**
- **Piergiuseppe Urso**
