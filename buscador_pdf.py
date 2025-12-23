import os
import csv
import pdfplumber
import pytesseract
import unicodedata
import re
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
from pdfminer.high_level import extract_text
import PySimpleGUI as sg

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").lower()

def limpar_ocr(texto):
    return re.sub(r'[^a-zA-Z0-9]', '', texto).lower()

def preprocessar(imagem):
    img = imagem.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2)
    img = img.filter(ImageFilter.MedianFilter())
    return img

def destacar_termo(texto, termo):
    # Destaca o termo encontrado no trecho
    return re.sub(f"({re.escape(termo)})", r">>>\1<<<", texto, flags=re.IGNORECASE)

def buscar_em_pdfs(pasta, termo, window):
    resultados = []
    termo_normalizado = limpar_ocr(normalizar(termo))

    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(pasta, arquivo)
            try:
                texto_pdfminer = extract_text(caminho)
                if texto_pdfminer:
                    # DEBUG sempre mostra
                    window["saida"].print(f"[DEBUG] Arquivo: {arquivo} | Origem: Texto embutido")
                    window["saida"].print(texto_pdfminer[:300] + "\n")

                    # Normaliza texto e compara
                    if termo_normalizado in limpar_ocr(normalizar(texto_pdfminer)):
                        trecho = destacar_termo(texto_pdfminer[:200], termo)
                        resultados.append((arquivo, "?", trecho, "Texto embutido"))
                    continue

                with pdfplumber.open(caminho) as pdf:
                    for i, pagina in enumerate(pdf.pages):
                        texto = pagina.extract_text()
                        origem = "Texto embutido"
                        if not texto:
                            imagens = convert_from_path(caminho, dpi=300, first_page=i+1, last_page=i+1)
                            texto = pytesseract.image_to_string(preprocessar(imagens[0]), lang="por")
                            origem = "OCR"
                        texto_limpo = texto.replace("\n", " ").strip()

                        # DEBUG sempre mostra
                        window["saida"].print(f"[DEBUG] Arquivo: {arquivo} | Página: {i+1} | Origem: {origem}")
                        window["saida"].print(texto_limpo[:300] + "\n")

                        # Normaliza texto e compara
                        texto_normalizado = limpar_ocr(normalizar(texto_limpo))
                        if termo_normalizado in texto_normalizado:
                            trecho = destacar_termo(texto_limpo[:200], termo)
                            resultados.append((arquivo, i+1, trecho, origem))
            except Exception as e:
                window["saida"].print(f"[DEBUG] Erro ao abrir {arquivo}: {e}")
    return resultados

def exportar_csv(resultados, filename):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Arquivo", "Página", "Trecho", "Origem"])
        for arquivo, pagina, trecho, origem in resultados:
            writer.writerow([arquivo, pagina, trecho, origem])

layout = [
    [sg.Text("Selecione a pasta dos PDFs:"), sg.Input(key="pasta"), sg.FolderBrowse()],
    [sg.Text("Digite a palavra ou número:"), sg.Input(key="termo")],
    [sg.Button("Buscar"), sg.Button("Exportar CSV"), sg.Button("Sair")],
    [sg.Multiline(size=(100,25), key="saida", disabled=False)]
]

window = sg.Window("Buscador de PDFs com OCR + pdfminer", layout, resizable=True)

resultados = []

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
            resultados = buscar_em_pdfs(pasta, termo, window)
            if resultados:
                for arquivo, pagina, trecho, origem in resultados:
                    window["saida"].print(f"📄 Arquivo: {arquivo} | Página: {pagina} | Origem: {origem}")
                    window["saida"].print(f"Trecho: {trecho}\n")
                window["saida"].print("✅ Busca concluída! Resultados exibidos acima.")
            else:
                window["saida"].print("Nenhum resultado encontrado.")
    if event == "Exportar CSV":
        if resultados:
            filename = sg.popup_get_file("Salvar resultados como...", save_as=True, file_types=(("CSV Files","*.csv"),))
            if filename:
                if not filename.lower().endswith(".csv"):
                    filename += ".csv"
                exportar_csv(resultados, filename)
                window["saida"].print(f"📂 Resultados exportados para '{filename}'.")
        else:
            window["saida"].print("⚠️ Nenhum resultado para exportar.")

window.close()
