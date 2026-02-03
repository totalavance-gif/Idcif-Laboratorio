from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import urllib3

# Silenciamos advertencias para un proceso limpio
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

    # URL Móvil Efímera (La que ya validamos que entra)
    url_sat = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3={idcif}_{rfc}"
    
    # Puente para saltar la muralla SSL de Vercel
    proxy_url = f"https://api.allorigins.win/get?url={requests.utils.quote(url_sat)}"

    # El proceso nace y muere dentro de este bloque
    try:
        with requests.Session() as s:
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)',
                'Connection': 'close' # Terminación inmediata
            }
            
            # Petición fugaz
            response = s.get(proxy_url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return jsonify({"status": "fail"}), 404

            # Extraemos el contenido del puente
            json_res = response.json()
            html = json_res.get('contents', '')
            
            # Si el SAT nos da el 404 que viste antes, el proceso muere aquí
            if not html or "Error 404" in html:
                return jsonify({"status": "denied"}), 404

            soup = BeautifulSoup(html, 'html.parser')
            datos = {}

            # Extracción quirúrgica de datos en versión móvil
            for el in soup.find_all(['span', 'td', 'div']):
                txt = el.get_text(strip=True)
                if ":" in txt and len(txt) < 100:
                    partes = txt.split(":", 1)
                    if len(partes) > 1 and partes[1].strip():
                        datos[partes[0].strip()] = partes[1].strip()

            if not datos:
                return jsonify({"status": "empty"}), 404

            # Entregamos resultados y el proceso se auto-destruye
            return jsonify({"status": "success", "datos": datos})

    except:
        # Cualquier fallo mata el proceso en silencio
        return jsonify({"status": "terminated"}), 500

app = app
            
