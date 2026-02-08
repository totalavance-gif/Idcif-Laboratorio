import io
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# --- CONFIGURACIÓN DEL LABORATORIO ---
IDCIF_A_PROBAR = "76996792661"
PLANTILLA_FILE = "plantilla.pdf"

def extraer_desde_sat(idcif):
    """Consulta la URL móvil y devuelve un diccionario con los datos."""
    url = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/consultas/cmf/consultaDatosTax.jsf?idCIF={idcif}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        datos = {}
        
        # Mapeo básico de etiquetas (esto varía según la respuesta del SAT)
        # Aquí simulamos la extracción de los campos clave
        for li in soup.find_all('li'):
            texto = li.get_text(strip=True)
            if ":" in texto:
                k, v = texto.split(":", 1)
                datos[k.strip().upper()] = v.strip().upper()
        
        return datos
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def generar_pdf(datos, idcif):
    """Estampa los datos sobre la plantilla.pdf"""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 9)
    
    # --- MAPEADO DE COORDENADAS ---
    # Nota: Los valores X, Y requieren calibración manual según tu plantilla
    can.drawString(245, 665, datos.get("RFC", ""))
    can.drawString(245, 650, datos.get("CURP", ""))
    
    # Ejemplo de cómo separar nombre completo si viene junto
    nombre_completo = datos.get("NOMBRE", "JACQUELINE NERI ESCOBAR")
    partes = nombre_completo.split(" ")
    can.drawString(245, 635, partes[0]) # Nombre
    can.drawString(245, 620, partes[1] if len(partes)>1 else "") # Apellido P
    can.drawString(245, 605, partes[2] if len(partes)>2 else "") # Apellido M

    can.save()
    packet.seek(0)

    # Fusión
    lector_plantilla = PdfReader(open(PLANTILLA_FILE, "rb"))
    lector_datos = PdfReader(packet)
    escritor = PdfWriter()

    pagina = lector_plantilla.pages[0]
    pagina.merge_page(lector_datos.pages[0])
    escritor.add_page(pagina)

    output_name = f"Resultado_{idcif}.pdf"
    with open(output_name, "wb") as f:
        escritor.write(f)
    return output_name

if __name__ == "__main__":
    print(f"🚀 Iniciando extracción para idCIF: {IDCIF_A_PROBAR}...")
    datos_sat = extraer_desde_sat(IDCIF_A_PROBAR)
    
    if datos_sat:
        archivo = generar_pdf(datos_sat, IDCIF_A_PROBAR)
        print(f"✨ Proceso terminado. Archivo creado: {archivo}")
    else:
        print("🛑 No se pudieron obtener datos.")
        
