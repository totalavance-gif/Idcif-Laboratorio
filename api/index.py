from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import urllib3

# Silenciamos cualquier advertencia para no generar logs innecesarios
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
        return jsonify({"status": "error"}), 400

    # URL Móvil Efímera
    url_sat = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3={idcif}_{rfc}"
    proxy_url = f"https://api.allorigins.win/get?url={requests.utils.quote(url_sat)}"

    # Iniciamos y matamos la sesión en un solo bloque para no dejar huella
    try:
        with requests.Session() as s:
            # Headers para parecer un visitante fugaz
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)',
                'Connection': 'close' # Le dice al servidor: "En cuanto me des esto, olvídame"
            }
            
            response = s.get(proxy_url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return jsonify({"status": "fail"}), 404

            html = response.json().get('contents', '')
            
            # Si el contenido está vacío o es un error, el proceso muere aquí
            if not html or "Error 404" in html:
                return jsonify({"status": "denied"}), 404

            soup = BeautifulSoup(html, 'html.parser')
            datos = {}

            # Extracción rápida
            for el in soup.find_all(['span', 'td']):
                txt = el.get_text(strip=True)
                if ":" in txt:
                    p = txt.split(":", 1)
                    if len(p) > 1 and p[1].strip():
                        datos[p[0].strip()] = p[1].strip()

            if not datos:
                return jsonify({"status": "empty"}), 404

            # Entregamos y el proceso termina (muere)
            return jsonify({"status": "success", "datos": datos})

    except:
        # Si algo falla, muere en silencio sin dar detalles técnicos
        return jsonify({"status": "terminated"}), 500

app = app
