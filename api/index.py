from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
# Importamos la función que arma la plantilla oficial con el QR
from .reconstructor import generar_html_constancia

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extraer', methods=['POST'])
def extraer():
    try:
        data = request.json
        rfc_usuario = data.get('rfc', '').upper()
        id_cif = data.get('id_cif', '')

        if not rfc_usuario or not id_cif:
            return jsonify({"status": "error", "message": "RFC e ID CIF son requeridos"}), 400

        # URL oficial del validador del SAT usando los parámetros D3 (idCIF_RFC)
        url = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3={id_cif}_{rfc_usuario}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "No se pudo conectar con el servidor del SAT"}), 500

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Diccionario para almacenar los datos extraídos
        datos = {
            "RFC": rfc_usuario,
            "id_cif": id_cif  # Guardamos esto para que el Reconstructor genere el QR
        }
        
        # Buscamos las tablas de datos en la respuesta del SAT
        tablas = soup.find_all('table')
        if not tablas:
            return jsonify({"status": "error", "message": "No se encontró información. Revisa que el ID CIF sea correcto."}), 404

        for tabla in tablas:
            filas = tabla.find_all('tr')
            for fila in filas:
                columnas = fila.find_all('td')
                if len(columnas) >= 2:
                    clave = columnas[0].get_text(strip=True).replace(':', '')
                    valor = columnas[1].get_text(strip=True)
                    if clave and valor:
                        datos[clave] = valor

        # --- LLAMADA AL RECONSTRUCTOR ---
        # Pasamos el diccionario 'datos' para que lo acomode en la plantilla.png que enviaste
        html_oficial = generar_html_constancia(datos)

        return jsonify({
            "status": "success",
            "datos": datos,
            "html_reconstruido": html_oficial
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error en el servidor: {str(e)}"}), 500

# Configuración necesaria para despliegue en Vercel
app.debug = False
