import os
import time
import datetime
import requests
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


Options = webdriver.ChromeOptions()
Options.add_argument("--headless")
driver = webdriver.Chrome(options=Options)

_url = "https://www.nfe.fazenda.sp.gov.br/ConsultaNFe/consulta/publica/consultarnfe.aspx"
_urlAudio = "https://www.nfe.fazenda.sp.gov.br/ConsultaNFe/controls/Som.ashx"

image_files = len([f for f in os.listdir('C://Users/asafe/Downloads/AD/Images/') if f.endswith('.png')])
print(f"Imagens já capturadas: {image_files}")

driver.get(_url)
cookies = driver.get_cookies()

request_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
response = requests.get(_urlAudio, cookies=request_cookies)

with open(f"C://Users/asafe/Downloads/AD/Audio/Som_{image_files + 1}.mp3", "wb") as f:
    f.write(response.content)

index = image_files + 1

while True:

    element = driver.find_element(By.XPATH, '//*[@id="ContentMain_CaptchaSefazAutor_captchaNFe"]')
    image = element.screenshot(f"C://Users/asafe/Downloads/AD/Images/captcha_{index}.png")   
    time.sleep(3)
    index += 1
    driver.refresh()

    cookies = driver.get_cookies()
    request_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    response = requests.get(_urlAudio, cookies=request_cookies)
    print(f"Áudio {response.content} baixado.")

    with open(f"C://Users/asafe/Downloads/AD/Audio/Som_{index}.mp3", "wb") as f:
        f.write(response.content)
    
