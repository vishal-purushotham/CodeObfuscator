# C Code Obfuscator & Deobfuscator ⚙️

The **C Code Obfuscator and Deobfuscator** is a Python-based tool designed to enhance the security and confidentiality of C source code. The obfuscator transforms the original code into a less readable and more complex version by renaming variables, functions, and other identifiers. The deobfuscator reverses this process, restoring the code to its original, readable state.

---

## Features 🔍

- 🔒 **Variable Renaming**: Consistently renames all variables to obfuscated identifiers.
- 🎨 **Function Renaming**: (If implemented) Renames functions to obscure names.
- 🔄 **Consistent Mapping**: Ensures that all instances of a variable are renamed consistently.
- 🔬 **Deobfuscation**: Reverts obfuscated code back to its original form using the mapping table.
- ⚡ **Error Handling**: Robust parsing and error reporting for invalid or unexpected code constructs.
- 🔗 **Web Interface**: Upload and process files via an interactive web page.
- 🔧 **Extensible Design**: Easily extendable to support additional C language features.

---

## Installation 

### 1. Clone the Repository 
```bash
git clone https://github.com/vishal-purushotham/CodeObfuscator.git
cd CodeObfuscator
```

### 2. Set Up a Virtual Environment (Optional but Recommended) 
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies 
```bash
pip install -r requirements.txt
```
> **Note**: Ensure that requirements.txt includes all necessary Python packages.

---

## Usage 

### 1. Launch the Web Interface 
```bash
cd webapp
```

Run the following command to start the app:
```bash
python app.py
```

### 2. Upload Your C Source File 
Access the web page at `http://127.0.0.1:5000` and upload your C source file for obfuscation. 

### 3. Obfuscation & Deobfuscation 
- Once uploaded, the tool will:
  - Generate an **obfuscated version** of your C code.
  - Provide a **zipped file** containing:
    - The **deobfuscated code**.
    - The **mapper.json** file for identifier mapping.
- To deobfuscate:
  - Upload the obfuscated `.c` file and the `mapper.json` file on the same page.

---

## Interactive Web Features 🌟

- **Sleek & Fun UI**: 
  - Buttons with animations 
  - Real-time progress updates 
- **Friendly Notifications**:
  - Success ✅ and error ❌ alerts.
- **Download Links**: Easily download your zipped files with a single click.

---

## Example Workflow 

1. Prepare Your C Source File (e.g., `sample_code.c`).
2. Run the app and upload your file.
3. Download the **zipped results**.
4. Use the `mapper.json` file to deobfuscate, if needed.

