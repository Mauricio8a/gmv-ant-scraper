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

        # Determinar tipo de documento
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
        
        # Buscar el nombre completo
        elemento = soup.find('td', class_='titulo1')
        
        if not elemento or not elemento.text.strip():
            return {
                "success": False, 
                "message": "No se encontraron datos para esta identificación en ANT"
            }

        nombre_completo = elemento.text.strip()
        
        # Separar Nombres y Apellidos de forma inteligente
        partes = nombre_completo.split()
        
        if len(partes) >= 3:
            nombres = " ".join(partes[:2])      # Generalmente los dos primeros son nombres
            apellidos = " ".join(partes[2:])    # El resto son apellidos
        elif len(partes) == 2:
            nombres = partes[0]
            apellidos = partes[1]
        else:
            nombres = nombre_completo
            apellidos = ""

        return {
            "success": True,
            "cedula": cedula,
            "nombres": nombres,
            "apellidos": apellidos,
            "nombre_completo": nombre_completo  # Lo mantenemos por si acaso en el futuro
        }

    except requests.exceptions.Timeout:
        return {"success": False, "message": "Timeout al consultar el sitio de ANT"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Error de conexión: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Error inesperado: {str(e)}"}


# Para pruebas locales
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)