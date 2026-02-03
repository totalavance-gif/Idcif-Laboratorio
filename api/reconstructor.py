import re
from datetime import datetime

def limpiar_bloque(texto, inicio, fin):
    """Separa los datos pegados del SAT."""
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
    
    # --- LIMPIEZA DE DATOS ---
    nombre = limpiar_bloque(curp_blob, "Nombre:", "Paterno")
    paterno = limpiar_bloque(curp_blob, "Paterno:", "Apellido")
    materno = limpiar_bloque(curp_blob, "Materno:", "Fecha")
    curp_limpia = curp_blob[:18]
    entidad = domicilio_blob.split("Municipio")[0].strip().upper() if "Municipio" in domicilio_blob else domicilio_blob
    
    # QR Oficial Dinámico
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10%26D2=1%26D3={id_cif}_{rfc}"

    return f"""
    <div id="cedula-final" style="
        position: relative; 
        width: 800px; 
        height: 1050px; 
        margin: 20px auto; 
        background-image: url('https://raw.githubusercontent.com/totalavance-gif/Idcif-Laboratorio/main/plantilla.png'); 
        background-size: 100% 100%;
        background-repeat: no-repeat;
        font-family: 'Helvetica', Arial, sans-serif;
        color: #000;
        box-shadow: 0 0 20px rgba(0,0,0,0.2);">

        <img src="{qr_url}" style="position: absolute; top: 155px; left: 638px; width: 125px;">
        
        <div style="position: absolute; top: 232px; left: 630px; font-size: 11px; font-weight: bold;">CIUDAD DE MÉXICO, {datetime.now().strftime('%d/%m/%Y')}</div>

        <div style="position: absolute; top: 185px; left: 245px; font-size: 12px; font-weight: bold;">{rfc}</div>
        <div style="position: absolute; top: 228px; left: 245px; font-size: 9px; width: 230px; line-height: 1.2;">{nombre} {paterno} {materno}</div>
        <div style="position: absolute; top: 275px; left: 285px; font-size: 10px;">{id_cif}</div>

        <div style="position: absolute; top: 367px; left: 385px; font-size: 11px;">{rfc}</div>
        <div style="position: absolute; top: 395px; left: 385px; font-size: 11px;">{curp_limpia}</div>
        <div style="position: absolute; top: 423px; left: 385px; font-size: 11px;">{nombre}</div>
        <div style="position: absolute; top: 451px; left: 385px; font-size: 11px;">{paterno}</div>
        <div style="position: absolute; top: 479px; left: 385px; font-size: 11px;">{materno}</div>
        <div style="position: absolute; top: 563px; left: 385px; font-size: 11px; color: green; font-weight: bold;">ACTIVO</div>

        <div style="position: absolute; top: 685px; left: 35px; font-size: 11px; width: 100px; text-align: center;">02300</div>
        <div style="position: absolute; top: 797px; left: 35px; font-size: 11px; width: 450px;">{entidad}</div>
    </div>
    """
    
