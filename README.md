# Web Scraper para Enriquecimiento de Datos de Empresas

Este proyecto es un web scraper desarrollado en Python que extrae información de empresas colombianas a partir de su NIT (Número de Identificación Tributaria) y enriquece un dataset con datos adicionales.

## 🚀 Características

- Extracción automática de información empresarial desde eDirectorio
- Geocodificación de direcciones utilizando la API de Google Maps
- Procesamiento por lotes con barra de progreso
- Modo headless (sin interfaz gráfica) para ejecución en segundo plano
- Manejo robusto de errores y contadores de éxito/fallo

## 📋 Requisitos Previos

- Python 3.7+
- Chrome Browser
- ChromeDriver (compatible con tu versión de Chrome)
- API Key de Google Maps Geocoding API

## 🔧 Instalación

1. Instala las dependencias:
```bash
pip install pandas selenium beautifulsoup4 tqdm requests
```

2. Asegúrate de tener ChromeDriver instalado y en tu PATH.

## 🛠 Configuración

1. Prepara tu archivo Excel (`df_enriquecido.xlsx`) con una columna llamada "nit"

2. Configura tu API Key de Google Maps en el código:
```python
api_key = "TU_API_KEY_AQUÍ"
```

## 📊 Uso

Ejecuta el script y procesará los NITs especificados, actualizando el Excel con:
- Razón social
- Dirección completa
- Ciudad
- Departamento
- Teléfono
- Sector/Actividad económica
- Coordenadas geográficas

## 🔍 Explicación del Funcionamiento

### Flujo del Scraper:

1. **Carga de datos**: Lee un archivo Excel con NITs de empresas
2. **Configuración del navegador**: Chrome en modo headless para operar sin interfaz
3. **Procesamiento por lotes**: Itera a través de los NITs (rango ajustable)
4. **Búsqueda inicial**: Consulta cada NIT en eDirectorio.net
5. **Extracción de enlace**: Localiza y accede al perfil detallado de cada empresa
6. **Scraping de datos**: Extrae información clave usando BeautifulSoup
7. **Geocodificación**: Convierte direcciones a coordenadas con Google Maps API
8. **Actualización del dataset**: Guarda los datos enriquecidos en el Excel original

### Elementos Clave Extraídos:

- Información básica de la empresa (razón social, dirección, ciudad, departamento)
- Teléfono (extraído mediante JavaScript del elemento oculto)
- Actividad económica principal
- Coordenadas geográficas (latitud, longitud)

### Manejo de Errores:

- Contadores para tracking de éxitos/fallos
- Try-catch para continuar procesamiento tras errores
- Timeouts configurados para evitar bloqueos

### Optimizaciones:

- Supresión de logs y mensajes del navegador para mejor performance
- Barra de progreso con tqdm para monitoreo visual
- Esperas inteligentes (WebDriverWait) para carga dinámica de contenido

## ⚠️ Consideraciones

- Respeta los términos de servicio de los sitios web
- Implementa delays apropiados entre requests
- La API de Google Maps tiene límites y posibles costos
- Ajusta el rango de procesamiento según necesidades: `df["nit"][10:100]`
