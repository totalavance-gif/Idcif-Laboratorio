import re

def limpiar_dato(texto, etiqueta_corte):
    """Separa el valor real del texto amontonado del SAT."""
    if not texto: return "N/A"
    # Corta el texto antes de la siguiente etiqueta (ej. Nombre, Municipio, etc.)
    partes = re.split(rf'({etiqueta_corte})', texto, flags=re.IGNORECASE)
    return partes[0].replace(':', '').strip().upper()

def generar_html_constancia(datos):
    rfc = datos.get('RFC', 'N/A')
    id_cif = datos.get('id_cif', 'N/A')
    curp_blob = datos.get('CURP', '')
    domicilio_blob = datos.get('Entidad Federativa', '')
    
    # --- PROCESAMIENTO DE DATOS (Mapeo a la Plantilla) ---
    nombre = limpiar_dato(curp_blob.split("Nombre:")[1] if "Nombre:" in curp_blob else "", "Paterno")
    paterno = limpiar_dato(curp_blob.split("Paterno:")[1] if "Paterno:" in curp_blob else "N/A", "Apellido")
    materno = limpiar_dato(curp_blob.split("Materno:")[1] if "Materno:" in curp_blob else "N/A", "Fecha")
    curp_solo = curp_blob[:18] # Extrae los 18 caracteres de la CURP
    
    entidad = limpiar_dato(domicilio_blob, "Municipio")
    cp = "02300" if "CP:02300" in domicilio_blob else "VERIFICAR"

    # URL del QR dinámico que apunta al validador oficial del SAT
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10%26D2=1%26D3={id_cif}_{rfc}"

    return f"""
    <div style="width: 100%; max-width: 800px; margin: 20px auto; background: #fff; padding: 30px; border: 1px solid #000; font-family: Arial, sans-serif; position: relative;">
        
        <div style="display: flex; border: 2px solid #000; margin-bottom: 20px;">
            <div style="width: 45%; border-right: 2px solid #000; padding: 15px; text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/SAT_logo.svg/512px-SAT_logo.svg.png" style="width: 120px; margin-bottom: 10px;">
                <p style="font-size: 10px; font-weight: bold; margin: 5px 0;">CÉDULA DE IDENTIFICACIÓN FISCAL</p>
                <img src="{qr_url}" style="width: 130px; margin: 10px 0;">
                <p style="font-size: 14px; font-weight: bold; letter-spacing: 1px;">{rfc}</p>
                <p style="font-size: 9px; color: #555;">idCIF: {id_cif}</p>
            </div>
            <div style="width: 55%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 10px;">
                <div style="background: #eee; border: 1px solid #000; padding: 15px; width: 90%; font-weight: bold; font-size: 14px;">
                    CONSTANCIA DE SITUACIÓN FISCAL
                </div>
                <div style="margin-top: 20px; font-size: 11px;">
                    Lugar y Fecha de Emisión:<br>
                    <b style="font-size: 13px;">CIUDAD DE MÉXICO A {datos.get('Fecha de Emisión', '03/02/2026')}</b>
                </div>
            </div>
        </div>

        <div style="background: #000; color: #fff; padding: 6px; font-size: 12px; font-weight: bold;">Datos de Identificación del Contribuyente:</div>
        <table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 20px; border: 1px solid #000;">
            <tr><td style="border: 1px solid #000; background: #f2f2f2; width: 35%; padding: 6px; font-weight: bold;">RFC:</td><td style="border: 1px solid #000; padding: 6px;">{rfc}</td></tr>
            <tr><td style="border: 1px solid #000; background: #f2f2f2; padding: 6px; font-weight: bold;">CURP:</td><td style="border: 1px solid #000; padding: 6px;">{curp_solo}</td></tr>
            <tr><td style="border: 1px solid #000; background: #f2f2f2; padding: 6px; font-weight: bold;">Nombre (s):</td><td style="border: 1px solid #000; padding: 6px;">{nombre}</td></tr>
            <tr><td style="border: 1px solid #000; background: #f2f2f2; padding: 6px; font-weight: bold;">Primer Apellido:</td><td style="border: 1px solid #000; padding: 6px;">{paterno}</td></tr>
            <tr><td style="border: 1px solid #000; background: #f2f2f2; padding: 6px; font-weight: bold;">Segundo Apellido:</td><td style="border: 1px solid #000; padding: 6px;">{materno}</td></tr>
            <tr><td style="border: 1px solid #000; background: #f2f2f2; padding: 6px; font-weight: bold;">Estatus en el padrón:</td><td style="border: 1px solid #000; padding: 6px;
    
