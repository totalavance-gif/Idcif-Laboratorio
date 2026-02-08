from flask import Flask, request, send_file, render_template
import io
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

def extraer_desde_sat(idcif):
    url = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/consultas/cmf/consultaDatosTax.jsf?idCIF={idcif}"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        datos = {}
        for li in soup.find_all('li'):
            texto = li.get_text(strip=True)
            if ":" in texto:
                k, v = texto.split(":", 1)
                datos[k.strip().upper()] = v.strip().upper()
        return datos
    except:
        return None

@app.route('/')
def home():
    return "Laboratorio IDCIF Activo. Usa /generar?idcif=TU_ID"

@app.route('/generar')
def generar():
    idcif = request.args.get('idcif')
    if not idcif:
        return "Falta el idCIF", 400

    datos = extraer_desde_sat(idcif)
    if not datos:
        return "No se pudo obtener información del SAT", 500

    # 1. Crear el PDF en memoria (BytesIO)
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 9)
    
    # --- Coordenadas basadas en tu plantilla.pdf ---
    can.drawString(200, 672, datos.get("RFC", ""))
    can.drawString(200, 658, datos.get("CURP", ""))
    can.drawString(200, 644, datos.get("NOMBRE", ""))
    # ... agregar más campos según sea necesario
    
    can.save()
    packet.seek(0)

    # 2. Leer la plantilla (Asegúrate de que plantilla.pdf esté en tu repo de GitHub)
    try:
        plantilla_pdf = PdfReader("plantilla.pdf")
        capa_datos = PdfReader(packet)
        escritor = PdfWriter()

        pagina = plantilla_pdf.pages[0]
        pagina.merge_page(capa_datos.pages[0])
        escritor.add_page(pagina)

        output = io.BytesIO()
        escritor.write(output)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Constancia_{idcif}.pdf"
        )
    except Exception as e:
        return f"Error procesando el PDF: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
        
