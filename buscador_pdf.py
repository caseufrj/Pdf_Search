import os
import re
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import PySimpleGUI as sg

def buscar_em_pdfs(pasta, termo):
    resultados = []
    padrao = re.compile(re.escape(termo), re.IGNORECASE)

    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(pasta, arquivo)
            try:
                with pdfplumber.open(caminho) as pdf:
                    for i, pagina in enumerate(pdf.pages):
                        texto = pagina.extract_text()
                        if texto:
                            texto_limpo = texto.replace("\n", " ").strip()
                        else:
                            # Se não há texto, usa OCR
                            imagens = convert_from_path(caminho, first_page=i+1, last_page=i+1)
                            texto_limpo = pytesseract.image_to_string(imagens[0], lang="por")  # OCR em português

                        if padrao.search(texto_limpo):
                            resultados.append((arquivo, i+1, texto_limpo))
            except Exception as e:
                resultados.append((arquivo, "ERRO", f"Não foi possível abrir: {e}"))
    return resultados

layout = [
    [sg.Text("Selecione a pasta dos PDFs:"), sg.Input(key="pasta"), sg.FolderBrowse()],
    [sg.Text("Digite a palavra ou número:"), sg.Input(key="termo")],
    [sg.Button("Buscar"), sg.Button("Sair")],
    [sg.Multiline(size=(100,25), key="saida", disabled=True)]
]

window = sg.Window("Buscador de PDFs com OCR", layout, resizable=True)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Sair"):
        break
    if event == "Buscar":
        pasta = values["pasta"]
        termo = values["termo"]
        window["saida"].update("")
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
