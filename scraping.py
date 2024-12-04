import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
from selenium.webdriver import Firefox
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error

def executar_scraping():
    url = "https://www.terabyteshop.com.br/hardware/placas-de-video"
    driver = Firefox()

    try:
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        conn = mysql.connector.connect(
            host=host_entry.get(),
            port=3333,  # Porta personalizada
            user=user_entry.get(),
            password=password_entry.get(),
            database=database_entry.get()
        )

        if conn.is_connected():
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255),
                    preco DECIMAL(10,2)
                )
            ''')

            placas = soup.find_all('div', class_="product-item")
            for placa in placas:
                nome_element = placa.find('a', class_='product-item__name')
                preco_element = placa.find('div', class_='product-item__new-price')

                if nome_element and preco_element:
                    nome = nome_element.text.strip()
                    preco = preco_element.find('span').text.strip() if preco_element.find('span') else "Preço não disponível"

                    if preco != "Preço não disponível":
                        preco = preco.replace('R$', '').replace('.', '').replace(',', '.').strip()
                        try:
                            preco = float(preco)
                        except ValueError:
                            continue

                    cursor.execute('INSERT INTO produtos (nome, preco) VALUES (%s, %s)', (nome, preco))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Scraping realizado e dados salvos!")
        else:
            messagebox.showerror("Erro", "Falha na conexão com o banco de dados.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
        driver.close()

def listar_produtos():
    try:
        conn = mysql.connector.connect(
            host=host_entry.get(),
            port=3333,  # Porta personalizada
            user=user_entry.get(),
            password=password_entry.get(),
            database=database_entry.get()
        )

        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT nome, preco FROM produtos")
            produtos = cursor.fetchall()

            # Criar nova janela para exibir os produtos
            listar_window = Toplevel(root)
            listar_window.title("Lista de Produtos")
            listar_window.geometry("600x400")

            # Configurar o layout da nova janela
            listar_window.columnconfigure(0, weight=1)
            listar_window.rowconfigure(1, weight=1)

            # Criar tabela com barras de rolagem
            frame = ttk.Frame(listar_window)
            frame.grid(row=1, column=0, sticky="nsew")

            tree = ttk.Treeview(frame, columns=("Nome", "Preço"), show="headings")
            tree.heading("Nome", text="Nome")
            tree.heading("Preço", text="Preço (R$)")
            tree.pack(side="left", fill="both", expand=True)

            # Adicionar barra de rolagem vertical
            scroll_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            scroll_y.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scroll_y.set)

            for produto in produtos:
                tree.insert("", "end", values=(produto[0], f"R$ {produto[1]:.2f}"))

            # Função para ordenar os produtos
            def ordenar_por_preco():
                produtos_ordenados = sorted(produtos, key=lambda x: x[1], reverse=True)
                # Limpar a tabela atual
                for item in tree.get_children():
                    tree.delete(item)
                # Recarregar os produtos ordenados
                for produto in produtos_ordenados:
                    tree.insert("", "end", values=(produto[0], f"R$ {produto[1]:.2f}"))

            # Botão para ordenar
            ordenar_button = tk.Button(listar_window, text="Ordenar por Preço (Maior para Menor)", command=ordenar_por_preco)
            ordenar_button.grid(row=0, column=0, pady=10)

            conn.close()
        else:
            messagebox.showerror("Erro", "Falha na conexão com o banco de dados.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# Criar janela principal
root = tk.Tk()
root.title("Scraping de Placas de Vídeo")
root.geometry("400x250")
root.minsize(400, 250)

# Configurar pesos para responsividade
root.columnconfigure(1, weight=1)
root.rowconfigure(4, weight=1)

# Campos de entrada para o banco de dados
tk.Label(root, text="Host:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
host_entry = tk.Entry(root)
host_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

tk.Label(root, text="Usuário:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
user_entry = tk.Entry(root)
user_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

tk.Label(root, text="Senha:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

tk.Label(root, text="Banco de Dados:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
database_entry = tk.Entry(root)
database_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

# Botões para executar as ações
executar_button = tk.Button(root, text="Executar Scraping", command=executar_scraping)
executar_button.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

listar_button = tk.Button(root, text="Listar Produtos", command=listar_produtos)
listar_button.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

# Rodar a interface
root.mainloop()
