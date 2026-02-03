from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup

# Importante: template_folder le dice a Flask dónde buscar el HTML en Vercel
app = Flask(__name__, template_folder='../templates')

@app.route('/')
def home():
    # Renderiza el archivo que tienes en /templates/index.html
    return render_template('index.html')

@app.route('/api/extraer')
def extraer():
    # Obtenemos los datos de la URL (ej: /api/extraer?rfc=XXX&idcif=123)
    rfc = request.args.get('rfc', '').upper().strip()
    idcif = request.args.get('idcif', '').strip()

    if not rfc or not idcif:
        return jsonify({
            "status": "error", 
            "detalle": "Debes proporcionar RFC e IDCIF"
        }), 400

    # 1. Construir la URL de validación del código QR del SAT
    url_sat = f"https://siat.sat.gob.mx/app/qr/faces/pages/rest/consultarDatosArt79.jsf?p1={idcif}&p2={rfc}"
    
    try:
        # 2. Simular un navegador real para evitar bloqueos básicos
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        
        # Hacemos la petición con un timeout de 10 segundos
        response = requests.get(url_sat, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return jsonify({
                "status": "error", 
                "detalle": "El servidor del SAT no respondió (Status: " + str(response.status_code) + ")"
            }), 500

        # 3. Analizar el HTML recibido
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # El SAT usa tablas para mostrar los datos de la CIF
        celdas = soup.find_all('td')
        datos_extraidos = {}
        
        # Recorremos la tabla: el SAT suele poner una celda con el nombre del dato 
        # y la siguiente con el valor real.
        for i in range(0, len(celdas) - 1, 2):
            label = celdas[i].get_text(strip=True).replace(":", "")
            valor = celdas[i+1].get_text(strip=True)
            
            if label and valor:
                # Guardamos en el diccionario (ej: {"RFC": "XAXX010101000", "Nombre": "JUAN..."})
                datos_extraidos[label] = valor

        # Si el diccionario está vacío, el IDCIF o el RFC están mal vinculados
        if not datos_extraidos:
            return jsonify({
                "status": "error", 
                "detalle": "No se encontraron datos. Verifica que el IDCIF corresponda al RFC."
            }), 404

        # 4. Éxito: Devolvemos el JSON con la info
        return jsonify({
            "status": "success",
            "datos": datos_extraidos,
            "url_oficial": url_sat
        })

    except requests.exceptions.Timeout:
        return jsonify({"status": "error", "detalle": "El SAT tardó demasiado en responder"}), 504
    except Exception as e:
        return jsonify({"status": "error", "detalle": str(e)}), 500

# Esta línea es necesaria para que Vercel detecte la app de Flask
app = app
      
