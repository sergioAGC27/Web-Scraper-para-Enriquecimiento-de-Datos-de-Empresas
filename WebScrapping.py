import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import urllib.parse

# Tu clave de API de Google Maps
api_key = "TU_API_KEY_AQUI"

# Cargar archivo Excel
archivo = "df_caribe.xlsx"
df = pd.read_excel(archivo)

# Configurar Chrome en modo headless y sin logs
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-logging")
options.add_argument("--log-level=3")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

# Contadores
exitosos = 0
fallidos = 0

# Subconjunto de NITs a procesar, dentro de ese rango, dejar solo donde latitud sea NaN
rango = df.iloc[25000:]
nits_a_procesar = rango[rango["latitud"].isna()].index.tolist()

print(f"NITs a procesar: {len(nits_a_procesar)}")
pbar = tqdm(total=len(nits_a_procesar), desc="Procesando", unit="NIT", ncols=75)



for n, nit in enumerate(nits_a_procesar):

    direccion = df.at[nit, 'direccion']
    ciudad = df.at[nit, 'ciudad']
    departamento = df.at[nit, 'departamento']

    # Unir en un solo string (ignorando NaN)
    partes = [str(x) for x in [direccion, ciudad, departamento] if pd.notna(x)]
    direccion_1 = ", ".join(partes)

    data = {}

    if pd.isna(direccion):
        try:
            driver.get(f"https://edirectorio.net/home/search?q={nit}")

            # Esperar botón "Explora"
            boton = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.custom-btn.btn")) 
            )

            link = boton.get_attribute("href")  # Se toma solo después de localizar

        except Exception as e:
            try:
                driver.get(f"https://edirectorio.net/home/search?q={nit//10}")

                # Esperar botón "Explora"
                boton = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.custom-btn.btn")) 
                )

                link = boton.get_attribute("href")  # Se toma solo después de localizar

            except Exception as e:
                fallidos += 1
                #print(f"❌ Error en NIT {nit}: {e}")
                pbar.update(1)
                continue

        driver.get(link)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        Actividad = driver.find_element(By.CSS_SELECTOR, "p.mb-0 a.badge.badge-level")

        for p in soup.select("p.mb-1"):
            strong = p.find("strong")
            if strong:
                clave = strong.get_text(strip=True).replace(":", "")
                valor = strong.next_sibling.strip() if strong.next_sibling else ""
                data[clave] = valor

        data["Actividad_economica_principal"] = Actividad.text.strip()

        try:
            telefono = driver.execute_script("return document.getElementById('phoneHidden').textContent;")
        except:
            telefono = ""

        direccion_1 = f"{data.get('Dirección')}, {data.get('Ciudad')}, {data.get('Departamento')}"

        df.at[nit, 'razon_social'] = data.get("Razón Social")
        df.at[nit, 'direccion'] = data.get("Dirección")
        df.at[nit, 'ciudad'] = data.get("Ciudad")
        df.at[nit, 'departamento'] = data.get("Departamento")
        df.at[nit, 'telefono'] = telefono.strip()
        df.at[nit, 'sector'] = data.get("Actividad_economica_principal")

    direccion_encoded = urllib.parse.quote(direccion_1)

    # Geocodificación con Google Maps
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={direccion_encoded}&key={api_key}"
    respuesta = requests.get(url).json()

    if respuesta['status'] == 'OK':
        ubicacion = respuesta['results'][0]['geometry']['location']
        data['latitud'] = ubicacion['lat']
        data['longitud'] = ubicacion['lng']
        exitosos += 1
    else:
        fallidos += 1
        #print(f"❌ NIT {nit} - Dirección: {direccion}")
        #print(f"⚠️ No se pudo geocodificar: {respuesta.get('status')}")

    # Guardar en el dataframe
    df.loc[df['nit'] == nit, 'latitud'] = data.get("latitud")
    df.loc[df['nit'] == nit, 'longitud'] = data.get("longitud")

    if n % 1000 == 0 and n != 0:
        df.to_excel("df_caribe.xlsx", index=False)

    pbar.update(1)

pbar.close()
driver.quit()
df.to_excel("df_caribe.xlsx", index=False)

# Resumen final
print("\n" + "="*50)
print("RESUMEN DE PROCESAMIENTO")
print("="*50)
print(f"NITs procesados exitosamente: {exitosos}")
print(f"NITs con errores: {fallidos}")
print(f"Total de NITs procesados: {exitosos + fallidos}")
print("="*50)