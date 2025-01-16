# webapp/app.py

import os
import sys
import logging
import tempfile
import zipfile
import json
from flask import (
    Flask,
    request,
    render_template,
    send_file,
    redirect,
    url_for,
    flash
)

# Add the src directory to the system path
sys.path.append(os.path.abspath('../src'))

from lexer import Lexer
from code_parser import Parser
from obfuscator import Obfuscator
from deobfuscator import Deobfuscator
from code_generator import CodeGenerator

app = Flask(__name__)

# **Secret Key Setup**
# It's crucial to use a secure and unpredictable secret key in production.
# For demonstration purposes, we're setting it directly.
# In production, consider using environment variables or a secure secrets manager.
app.secret_key = 'your_secure_secret_key'  # Replace with a strong, random key in production

# **Logging Configuration**
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Logs to a file named app.log
        logging.StreamHandler()          # Logs to the console
    ]
)

# **Upload Configuration**
UPLOAD_FOLDER = tempfile.gettempdir()  # Temporary directory for file uploads
ALLOWED_EXTENSIONS = {'c', 'json'}      # Allowed file extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """
    Render the home page with upload forms.

    Returns:
        Rendered HTML template for the home page.
    """
    return render_template('index.html')

@app.route('/obfuscate', methods=['POST'])
def obfuscate():
    """
    Handle the obfuscation process.

    Steps:
    1. Validate the uploaded file.
    2. Perform tokenization, parsing, and obfuscation.
    3. Generate obfuscated code and identifier map.
    4. Create a ZIP archive containing the obfuscated code and mapping.
    5. Provide a download link to the user.

    Returns:
        Rendered HTML template with tokens, parse tree, and download link.
    """
    if 'source_file' not in request.files:
        flash('No file part in the request.')
        return redirect(request.url)
    
    file = request.files['source_file']
    
    if file.filename == '':
        flash('No selected file.')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            # Read and decode the source code from the uploaded file
            source_code = file.read().decode('utf-8')
            logging.debug("Source Code Received for Obfuscation.")
            
            # **Obfuscation Process**
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            logging.debug(f"Tokenization Complete. Tokens: {tokens}")
            
            parser = Parser(tokens)
            ast = parser.parse()
            logging.debug("Parsing Complete. AST Generated.")
            
            obfuscator = Obfuscator()
            obf_ast = obfuscator.obfuscate(ast)
            logging.debug("Obfuscation Complete.")
            
            # Store the identifier_map for deobfuscation
            identifier_map = obfuscator.identifier_map
            logging.debug(f"Identifier Map: {identifier_map}")
            
            generator = CodeGenerator()
            obf_code = generator.generate(obf_ast)
            logging.debug("Code Generation Complete.")
            
            # Generate Parse Tree for visualization or analysis
            parse_tree = parser.get_parse_tree()
            logging.debug("Parse Tree Generated.")
            
            # **File Handling**
            # Define filenames for the obfuscated code and identifier map
            obf_filename = 'obfuscated_code.c'
            identifier_map_filename = 'identifier_map.json'
            zip_filename = 'obfuscated_code.zip'
            
            # Write obfuscated code to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.c') as obf_file:
                obf_file.write(obf_code)
                obf_filepath = obf_file.name
            logging.debug(f"Obfuscated code written to {obf_filepath}")
            
            # Serialize the identifier_map to JSON and write to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as map_file:
                json.dump(identifier_map, map_file, indent=4)
                identifier_map_path = map_file.name
            logging.debug(f"Identifier map written to {identifier_map_path}")
            
            # **Create ZIP Archive**
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(obf_filepath, arcname=obf_filename)
                zipf.write(identifier_map_path, arcname=identifier_map_filename)
            logging.debug(f"ZIP Archive Created at {zip_path}")
            
            # **Clean Up Temporary Files**
            os.remove(obf_filepath)
            os.remove(identifier_map_path)
            logging.debug("Temporary Files Removed.")
            
            # **Serialize parse_tree for JSON**
            parse_tree_json = json.dumps(parse_tree, indent=4)
            logging.debug(f"Serialized Parse Tree: {parse_tree_json}")
            
            # **Render Template with Results**
            return render_template(
                'index.html',
                tokens=tokens,
                parse_tree=parse_tree_json,                # Pass as JSON string
                download_link=url_for('download_zip', filename=zip_filename)
            )
        
        except Exception as e:
            logging.exception('Obfuscation failed.')
            flash(f'Obfuscation failed: {str(e)}')
            return redirect(url_for('home'))
    else:
        flash('Invalid file type. Only `.c` files are allowed.')
        return redirect(request.url)

@app.route('/deobfuscate', methods=['POST'])
def deobfuscate():
    """
    Handle the deobfuscation process.

    Steps:
    1. Validate the uploaded obfuscated file and identifier map.
    2. Perform tokenization, parsing, and deobfuscation.
    3. Generate the original code.
    4. Create a ZIP archive containing the deobfuscated code.
    5. Provide a download link to the user.

    Returns:
        Rendered HTML template with original code and download link.
    """
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
            # Read and decode the obfuscated code from the uploaded file
            obf_code = obf_file.read().decode('utf-8')
            logging.debug("Obfuscated Code Received for Deobfuscation.")
        except UnicodeDecodeError:
            logging.error("Failed to decode the obfuscated file.")
            flash('Failed to decode the obfuscated file. Ensure it is a valid UTF-8 encoded `.c` file.')
            return redirect(request.url)
        
        try:
            # Load the identifier_map from the uploaded JSON file
            identifier_map = json.loads(map_file.read().decode('utf-8'))
            logging.debug(f"Identifier Map Received: {identifier_map}")
        except json.JSONDecodeError:
            logging.error("Invalid identifier mapping file.")
            flash('Invalid identifier mapping file. Please provide a valid JSON file.')
            return redirect(request.url)
        
        # **Deobfuscation Process**
        try:
            lexer = Lexer(obf_code)
            obf_tokens = lexer.tokenize()
            logging.debug(f"Tokenization Complete. Tokens: {obf_tokens}")
            
            parser = Parser(obf_tokens)
            obf_ast = parser.parse()
            logging.debug("Parsing Complete. AST Generated.")
            
            deobfuscator = Deobfuscator(identifier_map)
            deobf_ast = deobfuscator.deobfuscate(obf_ast)
            logging.debug("Deobfuscation Complete.")
            
            generator = CodeGenerator()
            original_code = generator.generate(deobf_ast)
            logging.debug("Original Code Generation Complete.")
            
            # **File Handling**
            deobf_filename = 'deobfuscated_code.c'
            zip_filename = 'deobfuscated_code.zip'
            
            # Write deobfuscated code to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.c') as deobf_file:
                deobf_file.write(original_code)
                deobf_filepath = deobf_file.name
            logging.debug(f"Deobfuscated code written to {deobf_filepath}")
            
            # **Create ZIP Archive**
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(deobf_filepath, arcname=deobf_filename)
            logging.debug(f"ZIP Archive Created at {zip_path}")
            
            # **Clean Up Temporary Files**
            os.remove(deobf_filepath)
            logging.debug("Temporary Files Removed.")
            
            # **Render Template with Results**
            return render_template(
                'index.html',
                original_code=original_code,
                download_link=url_for('download_zip', filename=zip_filename)
            )
        
        except Exception as e:
            logging.exception('Deobfuscation failed.')
            flash(f'Deobfuscation failed: {str(e)}')
            return redirect(url_for('home'))
    else:
        flash('Invalid file types. Please ensure you upload a `.c` file and a `.json` mapping file.')
        return redirect(request.url)

@app.route('/download_zip/<filename>')
def download_zip(filename):
    """
    Provide the ZIP file for download.

    Args:
        filename (str): The name of the ZIP file to download.

    Returns:
        send_file response to initiate the download.
    """
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logging.exception('Download failed.')
        flash('Download failed. Please try the operation again.')
        return redirect(url_for('home'))

if __name__ == '__main__':
    # It's recommended to set debug=False in production for security reasons
    app.run(debug=True)