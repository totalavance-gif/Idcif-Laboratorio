from flask import Flask, request, jsonify, render_template, send_file
import requests
from bs4 import BeautifulSoup
import urllib3
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Silencio total
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

def generar_pdf_en_memoria(datos, idcif):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 8)
    
    # --- COORDENADAS CALIBRADAS PARA TU PLANTILLA ---
    # Ajusta estos valores (X, Y) según necesites mover el texto
    can.drawString(225, 672, datos.get("RFC", ""))
    can.drawString(225, 658, datos.get("CURP", ""))
    can.drawString(225, 644, datos.get("Nombre", ""))
    can.drawString(225, 630, datos.get("Primer Apellido", ""))
    can.drawString(225, 616, datos.get("Segundo Apellido", ""))
    
    # Domicilio (Ejemplo)
    can.drawString(110, 520, datos.get("Código Postal", ""))
    can.drawString(220, 520, datos.get("Nombre de Vialidad", ""))
    
    can.save()
    packet.seek(0)
    
    # Leer plantilla y fusionar
    plantilla_path = "plantilla.pdf"
    try:
        reader = PdfReader(plantilla_path)
        overlay = PdfReader(packet)
        writer = PdfWriter()
        
        page = reader.pages[0]
        page.merge_page(overlay.pages[0])
        writer.add_page(page)
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output
    except Exception as e:
        print(f"Error PDF: {e}")
        return None

@app.route('/')
def home():
    return "Laboratorio IDCIF: Motor de Extracción Activo."

@app.route('/api/extraer')
def extraer():
    rfc = request.args.get('rfc', '').upper().strip()
    idcif = request.args.get('idcif', '').strip()
    download = request.args.get('download', 'false').lower() == 'true'

    if not rfc or not idcif:
        return jsonify({"status": "error", "message": "Faltan credenciales"}), 400

    url_sat = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3={idcif}_{rfc}"
    puente_ninja = f"https://api.allorigins.win/get?url={requests.utils.quote(url_sat)}"

    try:
        with requests.Session() as s:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'}
            response = s.get(puente_ninja, headers=headers, timeout=10)
            
            contenido = response.json().get('contents', '')
            if not contenido or "Error 404" in contenido:
                return jsonify({"status": "not_found"}), 404

            soup = BeautifulSoup(contenido, 'html.parser')
            datos = {}

            for span in soup.find_all(['span', 'td']):
                texto = span.get_text(strip=True)
                if ":" in texto:
                    partes = texto.split(":", 1)
                    if len(partes) > 1:
                        datos[partes[0].strip()] = partes[1].strip()

            if not datos:
                return jsonify({"status": "ghost_mode"}), 404

            # SI EL USUARIO PIDE EL PDF
            if download:
                pdf_resultado = generar_pdf_en_memoria(datos, idcif)
                if pdf_resultado:
                    return send_file(
                        pdf_resultado,
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name=f"Constancia_{rfc}.pdf"
                    )

            return jsonify({"status": "success", "datos": datos})

    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

# Para Vercel
app = app
    
