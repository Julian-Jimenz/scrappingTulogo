from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Configurar Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Datos de inicio de sesión
usuario = "tulogomanizales@gmail.com"
contrasena = "Proveedores2024"

try:
    # 🔹 PASO 1: INICIAR SESIÓN
    driver.get("https://esferos.com/")
    print("✅ Página principal cargada.")
    time.sleep(3)

    # Hacer clic en el icono de inicio de sesión
    login_icon = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "login-icon"))
    )
    login_icon.click()
    print("✅ Se hizo clic en el icono de inicio de sesión.")

    # Esperar a que aparezca el formulario de login
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "customer_login"))
    )
    print("✅ Formulario de inicio de sesión detectado.")

    # Ingresar usuario y contraseña
    driver.find_element(By.ID, "CustomerEmail").send_keys(usuario)
    driver.find_element(By.ID, "CustomerPassword").send_keys(contrasena)
    print("✅ Usuario y contraseña ingresados.")

    # Hacer clic en "Iniciar sesión"
    driver.find_element(By.CSS_SELECTOR, "#customer_login button").click()
    print("✅ Se hizo clic en 'Iniciar sesión'.")
    time.sleep(5)  # Esperar a que se inicie sesión correctamente

    # 🔹 PASO 2: PROCESAR CATEGORÍAS
    categorias = [
        "https://esferos.com/collections/alcancias",
        "https://esferos.com/collections/bolsas",
        "https://esferos.com/collections/cuidado-personal"
    ]

    datos_productos = []

    for categoria in categorias:
        print(f"📂 Accediendo a la categoría: {categoria}")
        driver.get(categoria)
        time.sleep(5)

        # Función para hacer scroll fluido en la página de categoría
        def scroll_fluido():
            last_height = driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            while current_position < last_height:
                driver.execute_script("window.scrollBy(0, 10);")
                time.sleep(0.05)
                current_position = driver.execute_script("return window.pageYOffset + window.innerHeight")
                last_height = driver.execute_script("return document.body.scrollHeight")

        print("⬇️ Haciendo scroll fluido...")
        scroll_fluido()
        print("✅ Scroll completado.")

        # Esperar hasta que los productos se carguen después del scroll
        try:
            productos = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/products/']"))
            )
        except:
            productos = []

        # Obtener URLs únicas de los productos
        urls_productos = set()
        for producto in productos:
            href = producto.get_attribute("href")
            if href and "/products/" in href:
                urls_productos.add(href)

        print(f"✅ Se encontraron {len(urls_productos)} productos.")

        # Recorrer cada producto y extraer información
        for url in urls_productos:
            print(f"🔍 Extrayendo datos de: {url}")
            driver.get(url)
            time.sleep(3)

            # Extraer nombre del producto
            try:
                nombre = driver.find_element(By.CLASS_NAME, "ap-productmeta__title").text.strip()
            except:
                nombre = "No encontrado"

            # Extraer precio del producto
            try:
                precio = driver.find_element(By.CSS_SELECTOR, "span.price").text.strip()
            except:
                precio = "No encontrado"

            # Hacer scroll de 500px para cargar inventario
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)

            # Extraer inventario
            try:
                inventario_section = driver.find_element(By.TAG_NAME, "details")
                inventario_section.click()  # Expandir la sección
                time.sleep(1)
                inventario_texto = inventario_section.find_element(By.CLASS_NAME, "divDetails").text.strip()
            except:
                inventario_texto = "No encontrado"

            # Guardar datos
            datos_productos.append([nombre, precio, inventario_texto, url])
            print(f"✅ Datos extraídos: {nombre} | {precio} | {inventario_texto}")

    # 🔹 PASO 3: GUARDAR EN EXCEL
    df = pd.DataFrame(datos_productos, columns=["Nombre", "Precio", "Inventario", "URL"])
    df.to_excel("productos_esferos.xlsx", index=False)
    print("📁 Archivo Excel generado: productos_esferos.xlsx")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    driver.quit()
    print("🚪 Navegador cerrado.")
