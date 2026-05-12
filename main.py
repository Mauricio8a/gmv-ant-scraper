from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="ANT Scraper API - GMV")

# Configuración CORS (permite llamadas desde Google Apps Script)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Luego puedes restringirlo a tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/buscar/{identificacion}")
async def buscar_ant(identificacion: str):
    try:
        cedula = identificacion.strip()
        
        if len(cedula) < 5:
            return {"success": False, "message": "Identificación demasiado corta"}

        if len(cedula) == 10:
            tipo = "CED"
        elif len(cedula) == 13:
            tipo = "RUC"
        else:
            tipo = "PAS"

        url = f"https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_grid_citaciones.jsp?ps_tipo_identificacion={tipo}&ps_identificacion={cedula}&ps_placa="

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        elemento = soup.find('td', class_='titulo1')
        
        if not elemento or not elemento.text.strip():
            return {"success": False, "message": "No se encontraron datos en ANT"}

        nombre_completo = elemento.text.strip().upper()
        partes = nombre_completo.split()
        
        # Lógica mejorada para nombres ecuatorianos
        if len(partes) >= 3:
            apellidos = " ".join(partes[:2])      # Primeros dos = Apellidos
            nombres = " ".join(partes[2:])        # Resto = Nombres
        elif len(partes) == 2:
            apellidos = partes[0]
            nombres = partes[1]
        else:
            apellidos = ""
            nombres = nombre_completo

        return {
            "success": True,
            "cedula": cedula,
            "nombre_completo": nombre_completo,
            "nombres": nombres,
            "apellidos": apellidos
        }

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


# Para pruebas locales
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
