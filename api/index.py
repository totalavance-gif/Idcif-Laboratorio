from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import datetime
# Importamos tu reconstructor que armará la plantilla visual
from .reconstructor import generar_html_constancia

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extraer', methods=['POST'])
def extraer():
    try:
        data = request.json
        rfc_usuario = data.get('rfc', '').upper().strip()
        id_cif = data.get('id_cif', '').strip()

        if not rfc_usuario or not id_cif:
            return jsonify({"status": "error", "message": "RFC e ID CIF son obligatorios"}), 400

        # Construcción de URL oficial para validación QR
        # D1=10 (Tipo), D2=1 (Modo), D3=idCIF_RFC
        url = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3={id_cif}_{rfc_usuario}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
        }

        # Petición al SAT con tiempo de espera extendido
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "El SAT no responde. Intenta más tarde."}), 500

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Diccionario base con los datos de entrada
        datos_extraidos = {
            "RFC": rfc_usuario,
            "id_cif": id_cif,
            "Fecha de Emisión": datetime.datetime.now().strftime("%d/%m/%Y")
        }
        
        # Buscador de tablas de información
        tablas = soup.find_all('table')
        if not tablas:
            return jsonify({"status": "error", "message": "Datos no encontrados. Verifica tu ID CIF."}), 404

        # Procesamos cada fila encontrada en las tablas del SAT
        for tabla in tablas:
            for fila in tabla.find_all('tr'):
                cols = fila.find_all('td')
                if len(cols) >= 2:
                    etiqueta = cols[0].get_text(strip=True).replace(':', '')
                    valor = cols[1].get_text(strip=True)
                    if etiqueta and valor:
                        datos_extraidos[etiqueta] = valor

        # --- GENERACIÓN DE LA PLANTILLA RECONSTRUIDA ---
        # Aquí enviamos los datos para que el reconstructor los acomode en la plantilla.png
        html_plantilla = generar_html_constancia(datos_extraidos)

        return jsonify({
            "status": "success",
            "datos": datos_extraidos,
            "html_reconstruido": html_plantilla
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Fallo en conexión: {str(e)}"}), 500

# Requerido para Vercel
app.debug = False
                        
