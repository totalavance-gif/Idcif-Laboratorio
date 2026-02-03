import re

def limpiar_dato(texto):
    """Limpia el texto amontonado que envía el SAT."""
    if not texto: return "N/A"
    # Si detecta la palabra 'Fecha', corta el texto ahí para no arruinar el nombre
    limpio = re.split(r'Fecha', texto, flags=re.IGNORECASE)[0]
    return limpio.strip().upper()

def generar_html_constancia(datos):
    """Genera la plantilla visual organizada."""
    rfc = datos.get('RFC', 'N/A')
    # Aplicamos la limpieza ninja a los datos amontonados de tu captura
    nombre = limpiar_dato(datos.get('Nombre o Razón Social', datos.get('CURP', 'N/A')))
    regimen = limpiar_dato(datos.get('Régimen', 'N/A'))
    entidad = datos.get('Entidad Federativa', 'N/A')

    return f"""
    <div id="cedula-template" style="width: 100%; max-width: 500px; margin: auto; font-family: 'Segoe UI', Roboto, sans-serif; border: 1px solid #13322b; border-radius: 8px; overflow: hidden; background: #fff; box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
        
        <div style="background: #13322b; padding: 15px; display: flex; align-items: center; justify-content: space-between;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/SAT_logo.svg/512px-SAT_logo.svg.png" style="height: 35px; filter: brightness(0) invert(1);">
            <div style="text-align: right; color: #fff;">
                <div style="font-size: 10px; font-weight: bold; letter-spacing: 1px;">CÉDULA DE IDENTIFICACIÓN FISCAL</div>
                <div style="font-size: 8px; opacity: 0.8;">VALIDACIÓN OFICIAL 2026</div>
            </div>
        </div>

        <div style="padding: 25px;">
            <div style="margin-bottom: 25px; border-left: 4px solid #bc955c; padding-left: 15px;">
                <label style="display: block; font-size: 9px; color: #bc955c; font-weight: bold; margin-bottom: 2px;">RFC</label>
                <div style="font-size: 20px; font-weight: 900; color: #13322b; letter-spacing: 1px;">{rfc}</div>
            </div>

            <div style="margin-bottom: 20px;">
                <label style="display: block; font-size: 9px; color: #666; font-weight: bold; margin-bottom: 4px;">NOMBRE O RAZÓN SOCIAL</label>
                <div style="font-size: 13px; font-weight: 600; color: #333; line-height: 1.4;">{nombre}</div>
            </div>

            <div style="background: #f8f9fa; padding: 12px; border-radius: 6px; border: 1px solid #eee; margin-bottom: 20px;">
                <label style="display: block; font-size: 9px; color: #13322b; font-weight: bold; margin-bottom: 5px;">RÉGIMEN FISCAL VIGENTE</label>
                <div style="font-size: 11px; color: #444; font-style: italic;">{regimen}</div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding-top: 10px; border-top: 1px solid #f0f0f0;">
                <div>
                    <label style="display: block; font-size: 8px; color: #999; font-weight: bold;">ENTIDAD</label>
                    <div style="font-size: 10px; color: #333;">{entidad}</div>
                </div>
                <div style="text-align: right;">
                    <label style="display: block; font-size: 8px; color: #999; font-weight: bold;">ESTATUS</label>
                    <div style="font-size: 10px; color: #27ae60; font-weight: bold;">● ACTIVO</div>
                </div>
            </div>
        </div>

        <div style="background: #f4f4f4; padding: 8px; text-align: center; font-size: 8px; color: #aaa; border-top: 1px solid #eee;">
            La autenticidad de estos datos puede ser verificada mediante el QR original.
        </div>
    </div>
    """
    
