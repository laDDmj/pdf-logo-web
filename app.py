from flask import Flask, render_template, request, send_file
import fitz  
from PIL import Image
import os
import io

app = Flask(__name__)


UPLOAD_FOLDER = 'static/uploads'
LOGO_PATH = os.path.join(app.root_path, 'static', 'images', 'logo.png')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        
        pdf_file = request.files["pdf"]

        
        pdf_filename = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
        pdf_file.save(pdf_filename)

        
        output_pdf = insert_logo_into_pdf(pdf_filename, LOGO_PATH)

        
        return send_file(output_pdf, as_attachment=True)

    return render_template("index.html")

def insert_logo_into_pdf(pdf_filename, logo_filename):
    
    doc = fitz.open(pdf_filename)
    page = doc[0]

    
    zoom = 4  # 288 DPI
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    
    logo = Image.open(logo_filename).convert("RGBA")

    # Logo size
    logo_width_pt = 275
    x_offset_pt = 169
    y_offset_pt = 60


    logo_width_px = int(logo_width_pt * zoom)
    aspect_ratio = logo.width / logo.height
    logo_height_px = int(logo_width_px / aspect_ratio)
    logo = logo.resize((logo_width_px, logo_height_px), resample=Image.LANCZOS)

    x_offset_px = int(x_offset_pt * zoom)
    y_offset_px = int(y_offset_pt * zoom) - logo_height_px

    
    img.paste(logo, (x_offset_px, y_offset_px), logo)

    
    output_pdf = fitz.open()
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG", compress_level=0)
    img_bytes.seek(0)
    img_page = output_pdf.new_page(width=page.rect.width, height=page.rect.height)
    img_page.insert_image(page.rect, stream=img_bytes.read())

    
    for i in range(1, len(doc)):
        output_pdf.insert_pdf(doc, from_page=i, to_page=i)

    output_filename = "output_logo_pdf.pdf"
    output_pdf.save(output_filename, deflate=False)
    output_pdf.close()
    doc.close()

    return output_filename

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)