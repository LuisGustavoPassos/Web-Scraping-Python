from selenium.webdriver import Firefox
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error

# URL e inicialização do Selenium
url = "https://www.terabyteshop.com.br/hardware/placas-de-video"
driver = Firefox()

try:
    driver.get(url)

    # Configurando BeautifulSoup para analisar a página
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Conwcta o MySQL
    conn = mysql.connector.connect(
        host='localhost',
        user='root',  
        password='1234',  
        database='teste'
    )

    if conn.is_connected():
        cursor = conn.cursor()

        # Cria a tabela se ela não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255),
                preco VARCHAR(50)
            )
        ''')

        # Coleta dados das GPU
        placas = soup.find_all('div', class_="product-item")

        if placas:
            for placa in placas:
                nome_element = placa.find('a', class_='product-item__name')
                preco_element = placa.find('div', class_='product-item__new-price')

                # Verifica se nome e preço foram encontrados
                if nome_element and preco_element:
                    nome = nome_element.text.strip()
                    preco = preco_element.find('span').text.strip() if preco_element.find('span') else "Preço não disponível"

                    # Insere os dados no bds
                    cursor.execute('INSERT INTO produtos (nome, preco) VALUES (%s, %s)', (nome, preco))
                    print(f'Placa: {nome} | Preço: {preco}')
                else:
                    print("Informações incompletas para uma placa.")
            
            # Salvando mudanças no banco
            conn.commit()
        else:
            print("Nenhuma placa encontrada.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")

finally:
    # Fecha as conexões
    if conn.is_connected():
        cursor.close()
        conn.close()
    driver.close()
