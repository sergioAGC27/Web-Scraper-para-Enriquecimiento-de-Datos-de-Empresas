import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import sys

# Tu clave de API de Google Maps
api_key = "TU_CLAVE_DE_API_AQUI"

# Redirigir stdout y stderr para suprimir mensajes no deseados
original_stdout = sys.stdout
original_stderr = sys.stderr
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# Cargar archivo Excel
archivo = "df_añadido.xlsx"
# Leer el archivo Excel
df = pd.read_excel(archivo)
nit = df["nit"][0]

# Restaurar stdout temporalmente para mostrar solo el NIT de prueba
sys.stdout = original_stdout
sys.stderr = original_stderr
print("NIT de prueba:", nit)
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# Configurar Chrome en modo invisible con opciones para suprimir logs
options = Options()
options.add_argument("--headless")  # Navegador sin interfaz
options.add_argument("--disable-logging")
options.add_argument("--log-level=3")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

# Contadores para resultados
exitosos = 0
fallidos = 0

# Crear barra de progreso silenciosa
nits_a_procesar = df["nit"][0:10]

# Restaurar stdout para la barra de progreso
sys.stdout = original_stdout
sys.stderr = original_stderr
pbar = tqdm(total=len(nits_a_procesar), desc="Procesando", unit="NIT", ncols=75)
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

for nit in nits_a_procesar:
    driver.get(f"https://edirectorio.net/home/search?q={nit}")

    try:
        # Esperar a que aparezca el botón
        boton = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.custom-btn.btn"))
        )

        # Obtener el link del botón "Explora"
        link = boton.get_attribute("href")

        # Ir directamente al link de la empresa
        driver.get(link)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        Actividad = driver.find_element(By.CSS_SELECTOR, "p.mb-0 a.badge.badge-level")

        data = {}
        for p in soup.select("p.mb-1"):
            strong = p.find("strong")
            if strong:
                clave = strong.get_text(strip=True).replace(":", "")
                valor = strong.next_sibling.strip() if strong.next_sibling else ""
                data[clave] = valor

        data["Actividad_economica_principal"] = Actividad.text.strip()

        direccion = f"{data.get('Dirección')}, {data.get('Ciudad')}, Colombia"

        # Extraer directamente el texto del span oculto
        telefono = driver.execute_script("return document.getElementById('phoneHidden').textContent;")

        # Geocodificación con Google Maps API

        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={direccion}&key={api_key}"

        respuesta = requests.get(url).json()

        if respuesta['status'] == 'OK':
            ubicacion = respuesta['results'][0]['geometry']['location']
            data['latitud'] = ubicacion['lat']
            data['longitud'] = ubicacion['lng']
            exitosos += 1
        else:
            fallidos += 1

        df.loc[df['nit'] == nit, 'razon_social'] = data.get("Razón Social")
        df.loc[df['nit'] == nit, 'direccion'] = data.get("Dirección")
        df.loc[df['nit'] == nit, 'ciudad'] = data.get("Ciudad")
        df.loc[df['nit'] == nit, 'departamento'] = data.get("Departamento")
        df.loc[df['nit'] == nit, 'telefono'] = telefono.strip()
        df.loc[df['nit'] == nit, 'sector'] = data.get("Actividad_economica_principal")
        df.loc[df['nit'] == nit, 'latitud'] = data.get("latitud")
        df.loc[df['nit'] == nit, 'longitud'] = data.get("longitud")

        
    except Exception as e:
        fallidos += 1
    
    # Actualizar barra de progreso
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    pbar.update(1)
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    #time.sleep(0.1)

# Cerrar barra de progreso y driver
sys.stdout = original_stdout
sys.stderr = original_stderr
pbar.close()
driver.quit()

# Mostrar resumen al final
print("\n" + "="*50)
print("RESUMEN DE PROCESAMIENTO")
print("="*50)
print(f"NITs procesados exitosamente: {exitosos}")
print(f"NITs con errores: {fallidos}")
print(f"Total de NITs procesados: {exitosos + fallidos}")
print("="*50)

df.to_excel("df_enriquecido.xlsx", index=False)

# Restaurar stdout y stderr completamente
sys.stdout = original_stdout
sys.stderr = original_stderr