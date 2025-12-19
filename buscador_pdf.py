import os
import pdfplumber
import tkinter as tk
from tkinter import filedialog, messagebox

def buscar_em_pdfs(pasta, termo):
    resultados = []
    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(pasta, arquivo)
            with pdfplumber.open(caminho) as pdf:
                for i, pagina in enumerate(pdf.pages):
                    texto = pagina.extract_text()
                    if texto and termo.lower() in texto.lower():
                        resultados.append((arquivo, i+1, texto))
    return resultados

def escolher_pasta():
    pasta = filedialog.askdirectory()
    pasta_var.set(pasta)

def executar_busca():
    pasta = pasta_var.get()
    termo = termo_var.get()
    if not pasta or not termo:
        messagebox.showwarning("Aviso", "Escolha a pasta e digite o termo!")
        return
    
    resultados = buscar_em_pdfs(pasta, termo)
    if resultados:
        with open("resultados.txt", "w", encoding="utf-8") as f:
            for arquivo, pagina, trecho in resultados:
                f.write(f"Arquivo: {arquivo} | Página: {pagina}\n")
                f.write(f"Trecho: {trecho[:200]}...\n\n")
        messagebox.showinfo("Concluído", "Resultados salvos em resultados.txt")
    else:
        messagebox.showinfo("Concluído", "Nenhum resultado encontrado.")

# Interface gráfica
root = tk.Tk()
root.title("Buscador de PDFs")

pasta_var = tk.StringVar()
termo_var = tk.StringVar()

tk.Label(root, text="Pasta dos PDFs:").pack(pady=5)
tk.Entry(root, textvariable=pasta_var, width=50).pack(pady=5)
tk.Button(root, text="Selecionar Pasta", command=escolher_pasta).pack(pady=5)

tk.Label(root, text="Palavra ou número a buscar:").pack(pady=5)
tk.Entry(root, textvariable=termo_var, width=50).pack(pady=5)

tk.Button(root, text="Buscar", command=executar_busca).pack(pady=20)

root.mainloop()
