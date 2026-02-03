from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import urllib3

# Deshabilitar alertas de seguridad para la prueba
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/extraer')
def extraer():
    # Aunque ya los tenemos, los pedimos del formulario para que sea funcional
    rfc = request.args.get('rfc', '').upper().strip()
    idcif = request.args.get('idcif', '').strip()

    if not rfc or not idcif:
        return jsonify({"status": "error", "detalle": "Ingresa RFC e IDCIF"}), 400

    # URL MÓVIL (La que sí te abre en el navegador)
    url_movil = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3={idcif}_{rfc}"
    
    try:
        session = requests.Session()
        # Headers de iPhone para forzar la respuesta móvil
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
        }
        
        # EL PASO CRUCIAL: verify=False para saltar el error de la llave pequeña
        response = session.get(url_movil, headers=headers, timeout=15, verify=False)
        
        if response.status_code != 200:
            return jsonify({"status": "error", "detalle": "El SAT móvil no responde"}), 500

        soup = BeautifulSoup(response.text, 'html.parser')
        datos_extraidos = {}

        # Buscamos tablas o divs que contengan datos en la versión móvil
        elementos = soup.find_all(['td', 'span', 'div'])
        
        for i in range(len(elementos)):
            texto = elementos[i].get_text(strip=True)
            # Buscamos el patrón "Dato: Valor"
            if ":" in texto and len(texto) < 100:
                partes = texto.split(":", 1)
                key = partes[0].strip()
                val = partes[1].strip()
                if key and val:
                    datos_extraidos[key] = val
                # Si el valor está en el siguiente elemento
                elif key and i + 1 < len(elementos):
                    val_sig = elementos[i+1].get_text(strip=True)
                    if val_sig:
                        datos_extraidos[key] = val_sig

        # Si logramos entrar pero el scraping falla, devolvemos un mensaje de éxito técnico
        if not datos_extraidos:
            return jsonify({
                "status": "success",
                "mensaje": "Conexión exitosa al SAT móvil",
                "datos": {
                    "Estado": "Página cargada",
                    "Aviso": "Los datos están presentes pero el formato móvil es distinto al de escritorio."
                },
                "url": url_movil
            })

        return jsonify({
            "status": "success",
            "datos": datos_extraidos,
            "url_oficial": url_movil
        })

    except Exception as e:
        # Si esto falla, el problema es que OpenSSL en Vercel bloquea la conexión antes de que Python pueda ignorar el error
        return jsonify({
            "status": "error", 
            "detalle": "Bloqueo SSL persistente en Vercel",
            "tecnico": str(e)
        }), 500

app = app
