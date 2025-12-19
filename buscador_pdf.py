import os
import pdfplumber
import re
from PySimpleGUI import Text, Input, Button, Multiline, FolderBrowse, Window

def buscar_em_pdfs(pasta, termo):
    resultados = []
    padrao = re.compile(rf"\b{re.escape(termo)}\b", re.IGNORECASE)
    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(pasta, arquivo)
            try:
                with pdfplumber.open(caminho) as pdf:
                    for i, pagina in enumerate(pdf.pages):
                        texto = pagina.extract_text()
                        if texto and padrao.search(texto):
                            resultados.append((arquivo, i+1, texto))
            except Exception as e:
                resultados.append((arquivo, "ERRO", f"Não foi possível abrir: {e}"))
    return resultados

# Layout adaptado para PySimpleGUI 5.x
layout = [
    [Text("Selecione a pasta dos PDFs:"), Input(key="pasta"), FolderBrowse()],
    [Text("Digite a palavra ou número:"), Input(key="termo")],
    [Button("Buscar", size=(10,1)), Button("Sair", size=(10,1))],
    [Multiline(size=(100,25), key="saida", disabled=True)]
]

# Criar janela
window = Window("Buscador de PDFs", layout, resizable=True)

while True:
    event, values = window.read()
    if event in (None, "Sair"):  # None = janela fechada
        break
    if event == "Buscar":
        pasta = values["pasta"]
        termo = values["termo"]
        window["saida"].update("")  # limpa saída
        if not pasta or not termo:
            window["saida"].update("⚠️ Escolha a pasta e digite o termo!\n")
        else:
            resultados = buscar_em_pdfs(pasta, termo)
            if resultados:
                for arquivo, pagina, trecho in resultados:
                    window["saida"].print(f"Arquivo: {arquivo} | Página: {pagina}")
                    window["saida"].print(f"Trecho: {trecho[:200]}...\n")
                window["saida"].print("✅ Busca concluída! Resultados exibidos acima.")
            else:
                window["saida"].print("Nenhum resultado encontrado.")

window.close()
