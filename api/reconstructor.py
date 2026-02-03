import re

def limpiar_seccion(texto, etiqueta_inicio, etiqueta_fin):
    """Extrae el texto entre dos etiquetas del SAT."""
    try:
        if etiqueta_inicio not in texto: return ""
        resultado = texto.split(etiqueta_inicio)[1]
        if etiqueta_fin and etiqueta_fin in resultado:
            resultado = resultado.split(etiqueta_fin)[0]
        return resultado.replace(':', '').strip().upper()
    except:
        return ""

def generar_html_constancia(datos):
    rfc = datos.get('RFC', '')
    id_cif = datos.get('id_cif', '')
    curp_blob = datos.get('CURP', '')
    domicilio_blob = datos.get('Entidad Federativa', '')
    
    # --- PROCESAMIENTO DE LA PLANTILLA SUBIDA ---
    # Limpiamos los nombres amontonados de tu captura
    nombre = limpiar_seccion(curp_blob, "Nombre:", "Paterno")
    paterno = limpiar_seccion(curp_blob, "Paterno:", "Apellido")
    materno = limpiar_seccion(curp_blob, "Materno:", "Fecha")
    curp_limpia = curp_blob[:18] # Los primeros 18 caracteres son la CURP
    
    # Limpiamos domicilio
    entidad = domicilio_blob.split("Municipio")[0].strip().upper() if "Municipio" in domicilio_blob else domicilio_blob
    cp = "02300" if "CP:02300" in domicilio_blob else ""

    # Generación de QR dinámico (Apunta a la validación oficial del SAT)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10%26D2=1%26D3={id_cif}_{rfc}"

    return f"""
    <div style="width: 100%; max-width: 800px; margin: auto; font-family: Arial, sans-serif; background: #fff; padding: 20px; border: 1px solid #000;">
        
        <div style="display: flex; border-bottom: 2px solid #333; padding-bottom: 10px;">
            <div style="width: 50%; border: 1px solid #000; padding: 10px; text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/SAT_logo.svg/512px-SAT_logo.svg.png" style="width: 100px;">
                <p style="font-size: 9px; font-weight: bold; margin: 5px 0;">CÉDULA DE IDENTIFICACIÓN FISCAL</p>
                <img src="{qr_url}" style="width: 120px;">
                <p style="font-size: 11px; font-weight: bold; margin: 5px 0;">{rfc}</p>
                <p style="font-size: 8px;">idCIF: {id_cif}</p>
            </div>
            <div style="width: 50%; padding-left: 20px; text-align: center; display: flex; flex-direction: column; justify-content: center;">
                <div style="border: 1px solid #000; padding: 10px; font-weight: bold; background: #eee;">CONSTANCIA DE SITUACIÓN FISCAL</div>
                <div style="margin-top: 10px; font-size: 10px;">Lugar y Fecha de Emisión:<br><b>MÉXICO, CDMX A {datos.get('Fecha de Emisión', '2026-02-03')}</b></div>
            </div>
        </div>

        <div style="margin-top: 20px;">
            <div style="background: #000; color: #fff; padding: 5px; font-size: 11px; font-weight: bold;">Datos de Identificación del Contribuyente:</div>
            <table style="width: 100%; border-collapse: collapse; font-size: 10px;">
                <tr><td style="border: 1px solid #000; width: 30%; background: #f2f2f2; padding: 5px;">RFC:</td><td style="border: 1px solid #000; padding: 5px;">{rfc}</td></tr>
                <tr><td style="border: 1px solid #000; background: #f2f2f2; padding: 5px;">CURP:</td><td style="border: 1px solid #000; padding: 5px;">{curp_limpia}</td></tr>
                <tr><td style="border: 1px solid #000; background: #f2f2f2; padding: 5px;">Nombre (s):</td><td style="border: 1px solid #000; padding: 5px;">{nombre}</td></tr>
                <tr><td style="border: 1px solid #000; background: #f2f2f2; padding: 5px;">Primer Apellido:</td><td style="border: 1px solid #000; padding: 5px;">{paterno}</td></tr>
                <tr><td style="border: 1px solid #000; background: #f2f2f2; padding: 5px;">Segundo Apellido:</td><td style="border: 1px solid #000; padding: 5px;">{materno}</td></tr>
                <tr><td style="border: 1px solid #000; background: #f2f2f2; padding: 5px;">Estatus en el padrón:</td><td style="border: 1px solid #000; padding: 5px; color: green; font-weight: bold;">ACTIVO</td></tr>
            </table>
        </div>

        <div style="margin-top: 20px;">
            <div style="background: #000; color: #fff; padding: 5px; font-size: 11px; font-weight: bold;">Datos del domicilio registrado:</div>
            <table style="width: 100%; border-collapse: collapse; font-size: 10px;">
                <tr>
                    <td style="border: 1px solid #000; background: #f2f2f2; padding: 5px; width: 20%;">Código Postal:</td><td style="border: 1px solid #000; padding: 5px; width: 30%;">{cp}</td>
                    <td style="border: 1px solid #000; background: #f2f2f2; padding: 5px; width: 20%;">Entidad Federativa:</td><td style="border: 1px solid #000; padding: 5px; width: 30%;">{entidad}</td>
                </tr>
            </table>
        </div>

        <div style="margin-top: 30px; border-top: 3px solid #13322b; display: flex; justify-content: space-between; align-items: center; padding-top: 10px;">
             <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/SAT_logo.svg/512px-SAT_logo.svg.png" style="width: 80px;">
             <div style="font-size: 8px; color: #666; text-align: right;">Página [1] de [2]</div>
        </div>
    </div>
    """
    
