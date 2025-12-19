import os
import pdfplumber
import re
import PySimpleGUI as sg
 # Import correto, com maiúsculas

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

# Layout da interface
layout = [
    [sg.Text("Selecione a pasta dos PDFs:"), sg.InputText(key="pasta"), sg.FolderBrowse()],
    [sg.Text("Digite a palavra ou número:"), sg.InputText(key="termo")],
    [sg.Button("Buscar", size=(10,1)), sg.Button("Sair", size=(10,1))],
    [sg.Output(size=(100,25), key="saida")]
]

# Criar janela
window = sg.Window("Buscador de PDFs", layout, resizable=True)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Sair"):
        break
    if event == "Buscar":
        pasta = values["pasta"]
        termo = values["termo"]
        window["saida"].update("")  # limpa saída
        if not pasta or not termo:
            print("⚠️ Escolha a pasta e digite o termo!")
        else:
            resultados = buscar_em_pdfs(pasta, termo)
            if resultados:
                for arquivo, pagina, trecho in resultados:
                    print(f"Arquivo: {arquivo} | Página: {pagina}")
                    print(f"Trecho: {trecho[:200]}...\n")
                print("✅ Busca concluída! Resultados exibidos acima.")
            else:
                print("Nenhum resultado encontrado.")

window.close()
