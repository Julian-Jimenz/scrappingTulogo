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

try:
    # 1️⃣ Abrir la página principal
    driver.get("https://esferos.com/")
    print("✅ Página cargada correctamente.")
    time.sleep(3)

    # 2️⃣ Hacer clic en el icono de inicio de sesión
    login_icon = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "login-icon"))
    )
    login_icon.click()
    print("✅ Se hizo clic en el icono de inicio de sesión.")

    # 3️⃣ Esperar a que aparezca el formulario de login
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "customer_login"))
    )
    print("✅ Formulario de inicio de sesión detectado.")

    # 4️⃣ Ingresar usuario y contraseña
    driver.find_element(By.ID, "CustomerEmail").send_keys("tulogomanizales@gmail.com")
    driver.find_element(By.ID, "CustomerPassword").send_keys("Proveedores2024")
    print("✅ Usuario y contraseña ingresados.")

    # 5️⃣ Hacer clic en el botón de "Iniciar sesión"
    driver.find_element(By.CSS_SELECTOR, "#customer_login button").click()
    print("✅ Se hizo clic en 'Iniciar sesión'.")
    time.sleep(5)

    # 6️⃣ Navegar a la página de productos
    driver.get("https://esferos.com/collections/agendas")
    print("📖 Página de productos cargada.")
    time.sleep(5)

    # Función para hacer scroll fluido
    def scroll_fluido():
        last_height = driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        while current_position < last_height:
            driver.execute_script("window.scrollBy(0, 10);")
            time.sleep(0.05)
            current_position = driver.execute_script("return window.pageYOffset + window.innerHeight")
            last_height = driver.execute_script("return document.body.scrollHeight")

    print("⬇️ Haciendo scroll fluido hasta el final de la página...")
    scroll_fluido()
    print("✅ Scroll completado.")

    # 7️⃣ Esperar hasta que los productos se carguen después del scroll
    try:
        productos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/products/']"))
        )
    except:
        productos = []

    # 8️⃣ Obtener las URLs de los productos
    urls_productos = set()
    for producto in productos:
        href = producto.get_attribute("href")
        if href and "/products/" in href:
            urls_productos.add(href)

    print(f"✅ Se encontraron {len(urls_productos)} productos únicos.")

    # 9️⃣ Extraer información de cada producto
    productos_info = []

    for index, url in enumerate(urls_productos, start=1):
        driver.get(url)
        time.sleep(3)  # Esperar a que cargue la página del producto

        print(f"\n🔍 Procesando producto {index}/{len(urls_productos)}: {url}")

        try:
            # 🔹 Scroll de 500px para cargar inventario
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)

            # 🔹 Extraer el nombre del producto
            nombre_producto = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ap-productmeta__title"))
            ).text

            # 🔹 Extraer el precio
            precio_producto = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "price"))
            ).text

            # 🔹 Intentar abrir el detalle del inventario
            inventario_texto = "No disponible"
            try:
                inventario_section = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//details[summary[contains(text(), 'Inventario Disponible')]]"))
                )
                driver.execute_script("arguments[0].setAttribute('open', 'true');", inventario_section)
                time.sleep(2)

                inventario_parrafos = inventario_section.find_elements(By.TAG_NAME, "p")
                inventario_texto = "\n".join([p.text for p in inventario_parrafos])

            except Exception:
                print("⚠️ No se encontró la sección de inventario.")

            print(f"   - Nombre: {nombre_producto}")
            print(f"   - Precio: {precio_producto}")
            print(f"   - Inventario: {inventario_texto}")

            # Guardar los datos en la lista
            productos_info.append({
                "Producto": nombre_producto,
                "Precio": precio_producto,
                "Inventario": inventario_texto,
                "URL": url
            })

        except Exception as e:
            print(f"❌ Error al extraer datos del producto: {e}")

    # 🔟 Guardar los datos en un archivo Excel
    df = pd.DataFrame(productos_info)
    df.to_excel("productos_inventario.xlsx", index=False)
    print("\n✅ Archivo Excel 'productos_inventario.xlsx' creado con éxito.")

except Exception as e:
    print(f"❌ Ocurrió un error: {e}")

finally:
    driver.quit()
    print("🚪 Navegador cerrado.")
