from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import ssl

# --- SOLUCIÓN AL ERROR DE SEGURIDAD DEL SAT (DH_KEY_TOO_SMALL) ---
# Esta clase permite que Python acepte las llaves de cifrado antiguas del SAT
class SATAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # Bajamos el nivel de seguridad a 1 para permitir llaves Diffie-Hellman pequeñas
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(SATAdapter, self).init_poolmanager(*args, **kwargs)

# Configuración de Flask para Vercel
app = Flask(__name__, template_folder='../templates')

@app.route('/')
def home():
    """Muestra la interfaz principal"""
    return render_template('index.html')

@app.route('/api/extraer')
def extraer():
    """Endpoint para obtener los datos del SAT"""
    # Obtener parámetros de la URL
    rfc = request.args.get('rfc', '').upper().strip()
    idcif = request.args.get('idcif', '').strip()

    # Validación básica
    if not rfc or not idcif:
        return jsonify({
            "status": "error", 
            "detalle": "Faltan datos obligatorios: RFC e IDCIF (p1)"
        }), 400

    # Construcción de la URL de validación del código QR
    url_sat = f"https://siat.sat.gob.mx/app/qr/faces/pages/rest/consultarDatosArt79.jsf?p1={idcif}&p2={rfc}"
    
    try:
        # Configurar la sesión con el adaptador de seguridad especial
        session = requests.Session()
        session.mount("https://", SATAdapter())
        
        # Simular un navegador para evitar bloqueos por User-Agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        
        # Realizar la petición al SAT
        response = session.get(url_sat, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return jsonify({
                "status": "error", 
                "detalle": f"El SAT respondió con error {response.status_code}"
            }), 500

        # Analizar el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # El SAT organiza los datos en tablas con etiquetas <td>
        celdas = soup.find_all('td')
        datos_extraidos = {}
        
        # Recorremos la tabla saltando de 2 en 2 (Nombre del campo y Valor)
        for i in range(0, len(celdas) - 1, 2):
            label = celdas[i].get_text(strip=True).replace(":", "")
            valor = celdas[i+1].get_text(strip=True)
            if label and valor:
                datos_extraidos[label] = valor

        # Si no hay datos, probablemente el IDCIF no coincide con el RFC
        if not datos_extraidos:
            return jsonify({
                "status": "error", 
                "detalle": "No se encontraron datos. Verifica que el IDCIF corresponda al RFC."
            }), 404

        # Respuesta exitosa
        return jsonify({
            "status": "success",
            "datos": datos_extraidos,
            "url_oficial": url_sat
        })

    except requests.exceptions.Timeout:
        return jsonify({"status": "error", "detalle": "El SAT tardó demasiado en responder."}), 504
    except Exception as e:
        return jsonify({"status": "error", "detalle": f"Error inesperado: {str(e)}"}), 500

# Exponer la app para Vercel
app = app
