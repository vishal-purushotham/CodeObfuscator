# C Code Obfuscator and Deobfuscator

## Overview

The **C Code Obfuscator and Deobfuscator** is a Python-based tool designed to enhance the security and confidentiality of C source code. The obfuscator transforms the original code into a less readable and more complex version by renaming variables, functions, and other identifiers. The deobfuscator reverses this process, restoring the code to its original, readable state.

## Features

- **Variable Renaming:** Consistently renames all variables to obfuscated identifiers.
- **Function Renaming:** (If implemented) Renames functions to obscure names.
- **Consistent Mapping:** Ensures that all instances of a variable are renamed consistently.
- **Deobfuscation:** Reverts obfuscated code back to its original form using the mapping table.
- **Error Handling:** Robust parsing and error reporting for invalid or unexpected code constructs.
- **Extensible Design:** Easily extendable to support additional C language features.

## Installation

### 1. Clone the Repository

```bash
git clone ttps://github.com/vishal-purushotham/CodeObfuscator.git
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

> **Note:** Ensure that `requirements.txt` includes all necessary Python packages.

## Usage

### 1. Prepare Your C Source File

Ensure that you have a C source file (e.g., `sample_code.c`) that you want to obfuscate.

### 2. Run the Obfuscator

```bash
python obfuscator.py sample_code.c
```

This will generate two new files in the project directory:

- `obfuscated_code.c`: The obfuscated version of your original code.
- `deobfuscated_code.c`: The deobfuscated version, which should match the original code.
