import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

st.title("Pesquisa 'Defesa' no IN.gov.br")

# Configurações do Selenium
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # deixar comentado para ver o navegador
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://www.in.gov.br/leiturajornal")

    wait = WebDriverWait(driver, 30)

    # Espera o campo de pesquisa carregar
    search_input = wait.until(
        EC.presence_of_element_located((By.ID, "search-bar"))
    )

    # Limpa o campo e digita "Defesa"
    search_input.clear()
    search_input.send_keys("Ministério da Defesa")
    search_input.send_keys(Keys.ENTER)

    # Espera até que os resultados apareçam
    resultados = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )

    # Mostra o texto visível da página de resultados
    st.text_area("Resultados da pesquisa 'Defesa'", resultados.text, height=600)

finally:
    driver.quit()