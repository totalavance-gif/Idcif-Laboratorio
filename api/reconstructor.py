def generar_html_constancia(datos):
    """
    Crea la estructura visual de la constancia.
    """
    filas = ""
    # Mapeo para que los nombres se vean limpios
    for clave, valor in datos.items():
        filas += f"""
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #eee; font-size: 13px;">
            <span style="font-weight: bold; color: #666; text-transform: uppercase;">{clave}:</span>
            <span style="text-align: right; color: #111;">{valor}</span>
        </div>
        """

    return f"""
    <div style="background: #fff; padding: 20px; border-top: 5px solid #13322b; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); font-family: sans-serif;">
        <div style="text-align: center; margin-bottom: 15px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/SAT_logo.svg/512px-SAT_logo.svg.png" style="width: 60px;">
            <h4 style="margin: 5px 0; color: #13322b; font-size: 12px;">CÉDULA DE IDENTIFICACIÓN FISCAL</h4>
        </div>
        {filas}
    </div>
    """
  
