from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime
import unicodedata

# Inicializar el navegador
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")  # Evita problemas con permisos
options.add_argument("--disable-dev-shm-usage")  # Previene problemas con memoria compartida
options.add_argument("--disable-gpu")  # Deshabilita aceleración por hardware
options.add_argument("--remote-debugging-port=9222")  # Evita problemas con DevTools

# Crear el driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Abrir WhatsApp Web
driver.get("https://web.whatsapp.com")
print("Escanea el código QR en WhatsApp Web para iniciar sesión.")
time.sleep(30)  # Reducido el tiempo de espera inicial

# Función para limpiar caracteres no compatibles y normalizar
def limpiar_mensaje(mensaje):
    mensaje_normalizado = unicodedata.normalize('NFKD', mensaje)
    mensaje_sin_tildes = ''.join(c for c in mensaje_normalizado if not unicodedata.combining(c))
    mensaje_final = ''.join(c for c in mensaje_sin_tildes if ord(c) <= 0xFFFF)
    return mensaje_final

# Función para validar el número de teléfono
def validar_telefono(telefono):
    return len(telefono) == 11 and telefono.isdigit()

# Función para agregar código de país
def agregar_codigo_pais(telefono, codigo_pais="502"):
    return codigo_pais + telefono if len(telefono) == 8 and telefono.isdigit() else telefono

# Cargar datos desde JSON
with open('data2.json', 'r', encoding='utf-8') as file:
    citas = json.load(file)

# Enviar mensaje con optimización
def enviar_mensaje(driver, cita):
    try:
        # Validar y obtener el número de teléfono con código de país
        telefono = agregar_codigo_pais(cita['phone'])
        if not validar_telefono(telefono):
            print(f"Error: Número inválido {telefono}.")
            return
        
        # Crear el mensaje
        nombre = cita["name"]
        datetime_obj = datetime.strptime(cita['date'], "%Y-%m-%d %H:%M:%S")
        fecha = datetime_obj.strftime("%d/%m/%Y")
        hora = datetime_obj.strftime("%H:%M")

        mensaje = (
            f"Estimado/a {nombre}, un gusto saludarle ☺. "
            f"Le recordamos su cita programada para el día {fecha} a las {hora} ⏱. "
            f"Para acceder, por favor, haga clic en el siguiente enlace: medicinavirtualins.com. "
            f"Estamos a su disposición para cualquier pregunta o requerimiento adicional. 😃"
        )
        mensaje_limpio = limpiar_mensaje(mensaje)

        # Abrir chat usando la URL de WhatsApp
        driver.get(f"https://web.whatsapp.com/send?phone={telefono}")
        time.sleep(5)  # Ajustar este tiempo si es necesario

        # Esperar el cuadro de mensaje
        message_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        message_box.send_keys(mensaje_limpio)
        message_box.send_keys(Keys.ENTER)
        print(f"Mensaje enviado a {nombre} ({telefono})")
        
        # Esperar unos segundos antes de enviar el siguiente mensaje
        time.sleep(2)
    
    except Exception as e:
        print(f"Error al enviar mensaje a {cita['name']}: {e}")

# Enviar mensajes a todas las citas de manera optimizada
for cita in citas:
    enviar_mensaje(driver, cita)

# Cerrar el navegador
driver.quit()
