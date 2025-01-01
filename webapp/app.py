import sys
import os
import json
import zipfile
from flask import Flask, request, render_template, send_file, redirect, url_for, flash, session

# Add the src directory to the system path
sys.path.append(os.path.abspath('../src'))

from lexer import Lexer
from code_parser import Parser  # Updated import as per your request
from obfuscator import Obfuscator
from deobfuscator import Deobfuscator
from code_generator import CodeGenerator
import tempfile

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'  # Replace with a secure key in production

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'c', 'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Render the home page with upload forms."""
    return render_template('index.html')

@app.route('/obfuscate', methods=['POST'])
def obfuscate():
    """Handle the obfuscation process."""
    if 'source_file' not in request.files:
        flash('No file part in the request.')
        return redirect(request.url)
    
    file = request.files['source_file']
    
    if file.filename == '':
        flash('No selected file.')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        source_code = file.read().decode('utf-8')
        
        # Obfuscation Process
        try:
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            obfuscator = Obfuscator()
            obf_ast = obfuscator.obfuscate(ast)
            
            # Store the identifier_map
            identifier_map = obfuscator.identifier_map
            
            generator = CodeGenerator()
            obf_code = generator.generate(obf_ast)
            
            # Save obfuscated code to a temporary file
            obf_filename = 'obfuscated_code.c'
            obf_filepath = os.path.join(app.config['UPLOAD_FOLDER'], obf_filename)
            with open(obf_filepath, 'w') as f:
                f.write(obf_code)
            
            # Serialize the identifier_map to JSON
            identifier_map_filename = 'identifier_map.json'
            identifier_map_path = os.path.join(app.config['UPLOAD_FOLDER'], identifier_map_filename)
            with open(identifier_map_path, 'w') as map_file:
                json.dump(identifier_map, map_file, indent=4)
            
            # Create a ZIP archive containing both files
            zip_filename = 'obfuscated_code.zip'
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(obf_filepath, obf_filename)
                zipf.write(identifier_map_path, identifier_map_filename)
            
            # Send the ZIP file to the user
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=zip_filename
            )
        
        except Exception as e:
            flash(f'Obfuscation failed: {str(e)}')
            return redirect(url_for('home'))
    else:
        flash('Invalid file type. Only `.c` files are allowed.')
        return redirect(request.url)

@app.route('/deobfuscate', methods=['POST'])
def deobfuscate():
    """Handle the deobfuscation process."""
    if 'obf_file' not in request.files or 'map_file' not in request.files:
        flash('Please upload both the obfuscated file and the identifier mapping file.')
        return redirect(request.url)
    
    obf_file = request.files['obf_file']
    map_file = request.files['map_file']
    
    if obf_file.filename == '' or map_file.filename == '':
        flash('No selected files.')
        return redirect(request.url)
    
    if obf_file and allowed_file(obf_file.filename) and map_file and allowed_file(map_file.filename):
        try:
            # Read the obfuscated code
            obf_code = obf_file.read().decode('utf-8')
        except UnicodeDecodeError:
            flash('Failed to decode the obfuscated file. Ensure it is a valid UTF-8 encoded `.c` file.')
            return redirect(request.url)
        
        try:
            # Load the identifier_map from the uploaded JSON file
            identifier_map = json.loads(map_file.read().decode('utf-8'))
        except json.JSONDecodeError:
            flash('Invalid identifier mapping file. Please provide a valid JSON file.')
            return redirect(request.url)
        
        # Deobfuscation Process
        try:
            lexer = Lexer(obf_code)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            obf_ast = parser.parse()
            
            deobfuscator = Deobfuscator(identifier_map)
            deobf_ast = deobfuscator.deobfuscate(obf_ast)
            
            generator = CodeGenerator()
            original_code = generator.generate(deobf_ast)
            
            # Save deobfuscated code to a temporary file
            deobf_filename = 'deobfuscated_code.c'
            deobf_filepath = os.path.join(app.config['UPLOAD_FOLDER'], deobf_filename)
            with open(deobf_filepath, 'w') as f:
                f.write(original_code)
                
            # Send the deobfuscated code to the user
            return send_file(
                deobf_filepath,
                as_attachment=True,
                download_name=deobf_filename
            )
        
        except Exception as e:
            flash(f'Deobfuscation failed: {str(e)}')
            return redirect(url_for('home'))
    else:
        flash('Invalid file types. Please ensure you upload a `.c` file and a `.json` mapping file.')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
