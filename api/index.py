from flask import Flask, request, jsonify, render_template, send_file
import requests
from bs4 import BeautifulSoup
import urllib3
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Silencio para evitar logs innecesarios en Vercel
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

def generar_pdf_llenado(datos, idcif):
    """Crea una capa de texto sobre plantilla.pdf"""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 8)
    
    # --- COORDENADAS ESTIMADAS PARA plantilla.pdf ---
    # Ajustar X (derecha) y Y (arriba) según sea necesario
    # Bloque Identificación
    can.drawString(205, 672, datos.get("RFC", ""))
    can.drawString(205, 658, datos.get("CURP", ""))
    can.drawString(205, 644, datos.get("Nombre (s)", ""))
    can.drawString(205, 630, datos.get("Primer Apellido", ""))
    can.drawString(205, 616, datos.get("Segundo Apellido", ""))
    can.drawString(205, 602, datos.get("Estatus en el padrón", ""))
    
    # Bloque Domicilio
    can.drawString(145, 528, datos.get("Código Postal", ""))
    can.drawString(145, 514, datos.get("Tipo de Vialidad", ""))
    can.drawString(380, 514, datos.get("Nombre de Vialidad", ""))
    can.drawString(145, 500, datos.get("Número Exterior.", ""))
    can.drawString(145, 486, datos.get("Nombre de la Colonia", ""))
    
    can.save()
    packet.seek(0)
    
    try:
        # Fusionar con la plantilla física en el repo
        plantilla = PdfReader("plantilla.pdf")
        marcador = PdfReader(packet)
        writer = PdfWriter()
        
        page = plantilla.pages[0]
        page.merge_page(marcador.pages[0])
        writer.add_page(page)
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output
    except Exception as e:
        print(f"Error en fusión: {e}")
        return None

@app.route('/')
def home():
    return "Laboratorio IDCIF: Operativo y listo para extracción."

@app.route('/api/extraer')
def extraer():
    rfc = request.args.get('rfc', '').upper().strip()
    idcif = request.args.get('idcif', '').strip()
    download = request.args.get('download', 'false').lower() == 'true'

    if not rfc or not idcif:
        return jsonify({"status": "error", "msg": "Datos incompletos"}), 400

    # Tu lógica Ninja que ya funciona
    url_sat = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3={idcif}_{rfc}"
    puente_ninja = f"https://api.allorigins.win/get?url={requests.utils.quote(url_sat)}"

    try:
        with requests.Session() as s:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0'}
            response = s.get(puente_ninja, headers=headers, timeout=10)
            contenido = response.json().get('contents', '')
            
            if not contenido or "Error 404" in contenido:
                return jsonify({"status": "not_found"}), 404

            soup = BeautifulSoup(contenido, 'html.parser')
            datos = {}

            # Extracción de spans y celdas
            for span in soup.find_all(['span', 'td']):
                texto = span.get_text(strip=True)
                if ":" in texto:
                    partes = texto.split(":", 1)
                    if len(partes) > 1 and partes[1].strip():
                        datos[partes[0].strip()] = partes[1].strip()

            if not datos:
                return jsonify({"status": "ghost_mode"}), 404

            # SI EL USUARIO CLIQUEÓ "IMPRIMIR" (DOWNLOAD)
            if download:
                pdf_listo = generar_pdf_llenado(datos, idcif)
                if pdf_listo:
                    return send_file(
                        pdf_listo,
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name=f"Constancia_{rfc}.pdf"
                    )

            return jsonify({"status": "success", "datos": datos})

    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

app = app
