import os
import io
import zipfile
import pandas as pd
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    # 1. Get files from the user
    csv_file = request.files.get('csv_file')
    html_template = request.files.get('html_file')

    if not csv_file or not html_template:
        return "Please upload both files.", 400

    # 2. Read the files
    df = pd.read_csv(csv_file)
    template_content = html_template.read().decode('utf-8')
    
    # Use the HTML filename (minus extension) for the zip name
    base_name = html_template.filename.replace('.html', '')
    
    # 3. Create Zip file in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for _, row in df.iterrows():
            vendor = str(row['vendor'])
            link = str(row['link'])
            
            # Replace placeholder and create new filename
            final_html = template_content.replace('#####', link)
            new_filename = f"{base_name}_{vendor}.html"
            
            # Add to zip
            zf.writestr(new_filename, final_html)
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{base_name}_files.zip"
    )

if __name__ == '__main__':
    app.run(debug=True)
