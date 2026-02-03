def generar_html_constancia(datos):
    """
    Crea una versión visual de la constancia.
    """
    # Limpieza de datos para que no se vea amontonado
    regimen = datos.get('Régimen', 'No detectado')
    rfc = datos.get('RFC', 'No detectado')
    nombre = datos.get('Nombre o Razón Social', 'No detectado')

    return f"""
    <div style="background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #ddd; font-family: sans-serif;">
        <div style="text-align: center; border-bottom: 2px solid #13322b; margin-bottom: 15px; padding-bottom: 10px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/SAT_logo.svg/512px-SAT_logo.svg.png" style="width: 70px;">
            <h2 style="font-size: 14px; color: #13322b; margin: 5px 0;">CÉDULA DE IDENTIFICACIÓN FISCAL</h2>
        </div>
        <div style="margin-bottom: 10px;">
            <p style="font-size: 10px; color: #666; margin: 0;">RFC:</p>
            <p style="font-size: 14px; font-weight: bold; margin: 0;">{rfc}</p>
        </div>
        <div style="margin-bottom: 10px;">
            <p style="font-size: 10px; color: #666; margin: 0;">NOMBRE:</p>
            <p style="font-size: 12px; margin: 0;">{nombre}</p>
        </div>
        <div style="background: #f9f9f9; padding: 10px; border-radius: 4px;">
            <p style="font-size: 10px; color: #666; margin: 0;">RÉGIMEN FISCAL:</p>
            <p style="font-size: 11px; margin: 0;">{regimen}</p>
        </div>
    </div>
    """
    
