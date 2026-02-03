import re

def limpiar_dato(texto, etiqueta):
    """Limpia el texto amontonado buscando la etiqueta de fin."""
    if not texto: return ""
    # Corta el texto antes de la siguiente etiqueta del SAT (ej. Fecha, Municipio, etc.)
    partes = re.split(r'(Fecha|Municipio|Colonia|Tipo|Número|CP|Nombre|Apellido)', texto, flags=re.IGNORECASE)
    return partes[0].replace(':', '').strip().upper()

def generar_html_constancia(datos):
    rfc = datos.get('RFC', '')
    id_cif = datos.get('id_cif', '') # Pasado desde el index
    
    # Mapeo de datos basado en tu captura de 'Datos Encontrados'
    curp_raw = datos.get('CURP', '')
    nombre = limpiar_dato(curp_raw.split("Nombre:")[1] if "Nombre:" in curp_raw else "", "Fecha")
    paterno = limpiar_dato(curp_raw.split("Paterno:")[1] if "Paterno:" in curp_raw else "", "Apellido")
    materno = limpiar_dato(curp_raw.split("Materno:")[1] if "Materno:" in curp_raw else "", "Fecha")
    
    # URL del QR Oficial
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10%26D2=1%26D3={id_cif}_{rfc}"

    return f"""
    <div style="width: 100%; max-width: 750px; margin: auto; background: #fff; border: 1px solid #ccc; font-family: Arial, sans-serif; color: #000; padding: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #000; padding-bottom: 5px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/SAT_logo.svg/512px-SAT_logo.svg.png" style="width: 120px;">
            <div style="text-align: center; font-weight: bold; font-size: 14px;">CONSTANCIA DE SITUACIÓN FISCAL</div>
            <div style="text-align: right; font-size: 10px;">Lugar y Fecha de Emisión:<br><b>MÉXICO, 2026-02-03</b></div>
        </div>

        <div style="display: flex; margin-top: 15px; border: 1px solid #000;">
            <div style="width: 40%; padding: 10px; border-right: 1px solid #000; text-align: center;">
                <div style="font-size: 9px; font-weight: bold;">CÉDULA DE IDENTIFICACIÓN FISCAL</div>
                <img src="{qr_url}" style="width: 130px; margin: 10px 0;">
                <div style="font-size: 11px; font-weight: bold;">{rfc}</div>
                <div style="font-size: 8px;">idCIF: {id_cif}</div>
            </div>
            <div style="width: 60%; padding: 10px; font-size: 11px;">
                <p><b>Datos de Identificación del Contribuyente:</b></p>
                <div style="border: 1px solid #000;">
                    <div style="display: flex; border-bottom: 1px solid #ccc;"><div style="width: 40%; background: #f2f2f2; padding: 3px;">RFC:</div><div style="padding: 3px;">{rfc}</div></div>
                    <div style="display: flex; border-bottom: 1px solid #ccc;"><div style="width: 40%; background: #f2f2f2; padding: 3px;">Nombre (s):</div><div style="padding: 3px;">{nombre}</div></div>
                    <div style="display: flex; border-bottom: 1px solid #ccc;"><div style="width: 40%; background: #f2f2f2; padding: 3px;">Primer Apellido:</div><div style="padding: 3px;">{paterno}</div></div>
                    <div style="display: flex; border-bottom: 1px solid #ccc;"><div style="width: 40%; background: #f2f2f2; padding: 3px;">Segundo Apellido:</div><div style="padding: 3px;">{materno}</div></div>
                    <div style="display: flex;"><div style="width: 40%; background: #f2f2f2; padding: 3px;">Estatus:</div><div style="padding: 3px; color: green; font-weight: bold;">ACTIVO</div></div>
                </div>
            </div>
        </div>

        <div style="margin-top: 15px;">
            <div style="background: #e6e6e6; font-size: 11px; font-weight: bold; padding: 3px; border: 1px solid #000;">Datos del domicilio registrado</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; border: 1px solid #000; border-top: none; font-size: 10px;">
                <div style="padding: 3px; border-right: 1px solid #000; border-bottom: 1px solid #ccc;">Entidad Federativa: <b>{datos.get('Entidad Federativa', 'CDMX')}</b></div>
                <div style="padding: 3px; border-bottom: 1px solid #ccc;">CP: <b>{limpiar_dato(datos.get('Entidad Federativa', ''), 'CP')}</b></div>
            </div>
        </div>
        
        <div style="font-size: 8px; margin-top: 10px; text-align: justify; color: #555;">
            Cualquier alteración a este documento será sancionada conforme a las disposiciones fiscales vigentes.
        </div>
    </div>
    """
    
