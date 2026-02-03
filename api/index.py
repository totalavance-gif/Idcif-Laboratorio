from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import urllib3

# Desactivar ruidos de logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/extraer')
def extraer():
    rfc = request.args.get('rfc', '').upper().strip()
    idcif = request.args.get('idcif', '').strip()

    if not rfc or not idcif:
        return jsonify({"status": "error", "detalle": "Faltan datos"}), 400

    # URL Móvil que ya demostró éxito
    url_sat = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3={idcif}_{rfc}"
    
    # El puente AllOrigins que nos dio el pase
    proxy_url = f"https://api.allorigins.win/get?url={requests.utils.quote(url_sat)}"

    try:
        # Iniciamos sesión efímera que muere al terminar
        with requests.Session() as s:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0',
                'Connection': 'close'
            }
            
            response = s.get(proxy_url, headers=headers, timeout=20)
            
            if response.status_code != 200:
                return jsonify({"status": "error", "detalle": "SAT no disponible"}), 500

            contenido = response.json().get('contents', '')
            
            if not contenido or "Error 404" in contenido:
                return jsonify({"status": "error", "detalle": "Datos no encontrados"}), 404

            soup = BeautifulSoup(contenido, 'html.parser')
            datos = {}

            # Limpiamos los datos para que se vean bien en tu tarjeta
            for el in soup.find_all(['span', 'td']):
                txt = el.get_text(strip=True)
                if ":" in txt:
                    p = txt.split(":", 1)
                    if len(p) > 1 and p[1].strip():
                        # Quitamos espacios extras y saltos de línea
                        clave = p[0].strip()
                        valor = " ".join(p[1].split())
                        datos[clave] = valor

            if not datos:
                return jsonify({"status": "error", "detalle": "Formato no reconocido"}), 404

            # Entrega exitosa y fin del proceso
            return jsonify({
                "status": "success", 
                "datos": datos,
                "timestamp": "2026-02-03"
            })

    except Exception:
        return jsonify({"status": "error", "detalle": "Error de conexión ninja"}), 500

app = app
