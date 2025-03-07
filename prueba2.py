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
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://web.whatsapp.com")
print("Escanea el código QR en WhatsApp Web para iniciar sesión.")
time.sleep(30)  # Esperar para escanear el código QR

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
with open('data3.json', 'r', encoding='utf-8') as file:
    citas = json.load(file)

# Enviar mensaje
def enviar_mensaje(driver, cita):
    try:
        telefono = agregar_codigo_pais(cita['phone'])
        if not validar_telefono(telefono):
            print(f"Error: Número inválido {telefono}.")
            return
        
        nombre = cita["name"]
        doctor = cita["doctor"]
        datetime_obj = datetime.strptime(cita['date'], "%Y-%m-%d %H:%M:%S")
        fecha = datetime_obj.strftime("%d/%m/%Y")
        hora = datetime_obj.strftime("%H:%M")

        mensaje = (
            f"Estimado/a {nombre},\n\n"
            f"Hemos confirmado su cita con el Dr. {doctor}, programada para el {fecha} a las {hora} (hora local de Costa Rica).\n\n"
            f"📌 *Lineamientos para una Consulta Médica Virtual Efectiva:*\n\n"
            f"✅ *Normativa:* Se le informa que este mensaje incluye las regulaciones necesarias para recibir el servicio de Medicina Virtual.\n\n"
            f"✅ *Reglamento de telesalud:* Reglamento para el control y regulación de la teleconsulta sanitaria en Costa Rica Nº44363-S.\n\n"
            f"✅ *Conexión Anticipada:* Conéctese al menos 15 minutos antes de la hora programada. Si no se conecta dentro de los primeros 5 minutos posteriores al inicio de la cita, ésta será cancelada y deberá reprogramarse según disponibilidad.\n\n"
            f"✅ *Conexión a Internet:* Si tiene problemas técnicos 15 minutos antes de la cita, contáctenos vía WhatsApp Soporte de Medicina Virtual al *#7236-5512*.\n\n"
            f"✅ *Permisos del Navegador:* Autorice el acceso a video y audio en su dispositivo para garantizar una correcta comunicación.\n\n"
            f"✅ *Calidad de Imagen:* Si la imagen del médico no se visualiza claramente, revise su conexión a internet y la calidad de su dispositivo.\n\n"
            f"✅ *Preparación de Síntomas:* Tenga listos sus síntomas y preguntas para optimizar el tiempo de la consulta.\n\n"
            f"✅ *Ambiente Tranquilo:* Escoja un lugar sin ruidos ni interrupciones para la consulta.\n\n"
            f"✅ *Atención a Menores:* Si la consulta es para un menor, active el video y comparta el enlace con el adulto responsable.\n\n"
            f"✅ *Emergencias:* En caso de que su situación requiera atención presencial, considere acudir a un centro médico.\n\n"
            f"✅ *Patologías de atención:* La Medicina Virtual está destinada a casos en los que no se requiera un examen físico presencial y se enfocará en patologías agudas de resolución rápida.\n\n"
            f"✅ *Atención Durante la Consulta:* Manténgase enfocado y evite actividades como comer, beber, conducir o hacer compras.\n\n"
            f"✅ *Respeto y Profesionalismo:* Mantenga una actitud respetuosa con el médico.\n\n"
            f"✅ *Consulta Adicional:* Para dudas sobre entrega de medicamentos y cobertura de su póliza, comuníquese al *800-MEDICAL (800-633-4225)*.\n\n"
            f"✅ *Documentación Previa:* Si necesita compartir resultados de laboratorio o imágenes, envíelos a *medicinavirtualresultados@grupoins.com* e incluya su nombre completo en el asunto.\n\n"
            f"Atentamente,\n"
            f"*Equipo de Medicina Virtual*"
        )

        mensaje_limpio = limpiar_mensaje(mensaje)

        driver.get(f"https://web.whatsapp.com/send?phone={telefono}")
        time.sleep(5)

        message_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )

        for line in mensaje_limpio.split("\n"):
            message_box.send_keys(line)
            message_box.send_keys(Keys.SHIFT, Keys.ENTER)  # Agregar salto de línea sin enviar el mensaje

        message_box.send_keys(Keys.ENTER)  # Ahora sí, enviar todo el mensaje junto
        print(f"Mensaje enviado a {nombre} ({telefono})")
        
        time.sleep(2)
    
    except Exception as e:
        print(f"Error al enviar mensaje a {cita['name']}: {e}")

for cita in citas:
    enviar_mensaje(driver, cita)

driver.quit()