import re

def limpiar_valor(texto, inicio, fin):
    """Extrae el valor real del bloque amontonado del SAT."""
    try:
        if inicio not in texto: return ""
        res = texto.split(inicio)[1]
        if fin and fin in res: res = res.split(fin)[0]
        return res.replace(':', '').strip().upper()
    except: return ""

def generar_html_constancia(datos):
    rfc = datos.get('RFC', '')
    id_cif = datos.get('id_cif', '')
    curp_blob = datos.get('CURP', '')
    domicilio_blob = datos.get('Entidad Federativa', '')
    
    # --- PROCESAMIENTO DE DATOS ---
    nombre = limpiar_valor(curp_blob, "Nombre:", "Paterno")
    paterno = limpiar_valor(curp_blob, "Paterno:", "Apellido")
    materno = limpiar_valor(curp_blob, "Materno:", "Fecha")
    curp_limpia = curp_blob[:18]
    entidad = domicilio_blob.split("Municipio")[0].strip().upper() if "Municipio" in domicilio_blob else domicilio_blob
    cp = "02300" if "CP:02300" in domicilio_blob else ""

    # QR Dinámico
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10%26D2=1%26D3={id_cif}_{rfc}"

    return f"""
    <div id="constancia-imprimible" style="
        position: relative; 
        width: 800px; 
        height: 1035px; 
        margin: auto; 
        background-image: url('https://raw.githubusercontent.com/totalavance-gif/Idcif-Laboratorio/main/plantilla.png'); 
        background-size: contain; 
        background-repeat: no-repeat;
        font-family: Arial, sans-serif;
        color: #000;
        text-transform: uppercase;">

        <img src="{qr_url}" style="position: absolute; top: 145px; left: 85px; width: 125px;">
        
        <div style="position: absolute; top: 180px; left: 245px; font-size: 12px; font-weight: bold;">{rfc}</div>
        <div style="position: absolute; top: 225px; left: 245px; font-size: 10px; width: 230px;">{nombre} {paterno} {materno}</div>
        <div style="position: absolute; top: 270px; left: 280px; font-size: 10px;">{id_cif}</div>
        <div style="position: absolute; top: 230px; left: 630px; font-size: 11px; font-weight: bold;">03/02/2026</div>

        <div style="position: absolute; top: 367px; left: 300px; font-size: 11px;">{rfc}</div>
        <div style="position: absolute; top: 395px; left: 300px; font-size: 11px;">{curp_limpia}</div>
        <div style="position: absolute; top: 423px; left: 300px; font-size: 11px;">{nombre}</div>
        <div style="position: absolute; top: 451px; left: 300px; font-size: 11px;">{paterno}</div>
        <div style="position: absolute; top: 479px; left: 300px; font-size: 11px;">{materno}</div>
        <div style="position: absolute; top: 563px; left: 300px; font-size: 11px; color: green; font-weight: bold;">ACTIVO</div>

        <div style="position: absolute; top: 685px; left: 300px; font-size: 11px;">{cp}</div>
        <div style="position: absolute; top: 795px; left: 300px; font-size: 11px;">{entidad}</div>
    </div>
    """
    
