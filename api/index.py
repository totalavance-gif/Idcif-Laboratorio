import requests
from bs4 import BeautifulSoup

def extraer_datos_sat(idcif):
    # La URL que el QR apunta en dispositivos móviles
    url = f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/consultas/cmf/consultaDatosTax.jsf?idCIF={idcif}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscamos todos los elementos de datos (usualmente en spans o tablas con IDs específicos)
            datos = {}
            # En el sitio móvil, los datos suelen venir en una estructura de lista o tabla
            items = soup.find_all('li') # Opcional: ajustar según la estructura actual del DOM
            
            print(f"--- Datos extraídos del idCIF: {idcif} ---")
            for item in items:
                texto = item.get_text(strip=True)
                if ":" in texto:
                    clave, valor = texto.split(":", 1)
                    datos[clave.strip()] = valor.strip()
                    print(f"✅ {clave.strip()}: {valor.strip()}")
            
            if not datos:
                # Si no hay <li>, intentamos por etiquetas generales de texto
                print("⚠️ No se detectó estructura de lista, imprimiendo texto plano...")
                print(soup.get_text(separator='\n', strip=True))
                
            return datos
        else:
            print(f"❌ Error al conectar: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en la ejecución: {e}")

# --- PRUEBA DEL LABORATORIO ---
# Usando el idCIF del expediente anterior
mi_idcif = "76996792661"
extraer_datos_sat(mi_idcif)
