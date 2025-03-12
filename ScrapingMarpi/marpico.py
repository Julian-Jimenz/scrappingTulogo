from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd  # Para manejar Excel
from bs4 import BeautifulSoup  # Para procesar HTML

# Configurar el driver de Chrome
driver = webdriver.Chrome()

# Lista para almacenar los datos de todos los productos
datos_totales = []

# Rango de páginas a recorrer
for pagina in range(1, 3):  # De la 1 a la 3
    url = f"https://marpicopromocionales.com/#/productos?categoria=30001&subcategoria=3000100001&current_page={pagina}"
    driver.get(url)
    print(f"Página {pagina} abierta correctamente.")
    time.sleep(10)  # Esperar la carga de la página
    driver.refresh()
    time.sleep(10)  # Esperar después de refrescar

    # Encontrar todos los productos en la página
    productos = driver.find_elements(By.CLASS_NAME, "col-sm-6.col-md-6.col-lg-4.col-xl-3.contenedor-producto.ng-star-inserted")
    print(f"Se encontraron {len(productos)} productos en la página {pagina}.")

    for i in range(len(productos)):
        try:
            productos = driver.find_elements(By.CLASS_NAME, "col-sm-6.col-md-6.col-lg-4.col-xl-3.contenedor-producto.ng-star-inserted")
            producto = productos[i]
            producto.click()
            time.sleep(5)

            # Extraer SKU
            contenedor_sku = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "card-body"))
            )
            sku = contenedor_sku.find_element(By.TAG_NAME, "b").text.strip()

            # Extraer el contenedor padre con la tabla
            contenedor_padre = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-md-12.d-none.d-lg-block.ng-star-inserted"))
            )
            contenido_completo = contenedor_padre.get_attribute("innerHTML")
            
            # Extraer la tabla
            soup = BeautifulSoup(contenido_completo, "html.parser")
            tabla = soup.find("table", {"class": "table"})

            if tabla:
                filas = tabla.find_all("tr")
                for fila in filas:
                    celdas = [celda.text.strip() for celda in fila.find_all(["td", "th"])]
                    if celdas:
                        celdas.insert(0, sku)  # Agregar SKU al inicio de cada fila
                        datos_totales.append(celdas)

            driver.back()  # Regresar a la página de productos
            time.sleep(5)

        except Exception as e:
            print(f"Error al procesar un producto: {e}")
            driver.back()
            time.sleep(5)

# Guardar datos en un archivo Excel
df = pd.DataFrame(datos_totales)
df.to_excel("productos_completos.xlsx", index=False, header=False)
print("Archivo Excel creado exitosamente: productos_completos.xlsx")

# Cerrar el navegador
driver.quit()
