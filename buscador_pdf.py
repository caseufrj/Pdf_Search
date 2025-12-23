import os
import pdfplumber
import pytesseract
import unicodedata
import re
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import PySimpleGUI as sg

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").lower()

def limpar_ocr(texto):
    return re.sub(r'[^a-zA-Z0-9]', '', texto).lower()

def preprocessar(imagem):
    img = imagem.convert("L")  # escala de cinza
    img = ImageEnhance.Contrast(img).enhance(2)  # aumenta contraste
    img = img.filter(ImageFilter.MedianFilter())  # reduz ruído
    return img

def buscar_em_pdfs(pasta, termo, window):
    resultados = []
    termo_normalizado = limpar_ocr(normalizar(termo))

    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(pasta, arquivo)
            try:
                with pdfplumber.open(caminho) as pdf:
                    for i, pagina in enumerate(pdf.pages):
                        texto = pagina.extract_text()
                        if not texto:
                            imagens = convert_from_path(caminho, dpi=300, first_page=i+1, last_page=i+1)
                            texto = pytesseract.image_to_string(preprocessar(imagens[0]), lang="por")
                        texto_limpo = texto.replace("\n", " ").strip()

                        # DEBUG
                        window["saida"].print(f"[DEBUG] Arquivo: {arquivo} | Página: {i+1}")
                        window["saida"].print(texto_limpo[:300] + "\n")

                        texto_normalizado = limpar_ocr(normalizar(texto_limpo))
                        if termo_normalizado in texto_normalizado:
                            resultados.append((arquivo, i+1, texto_limpo))
            except Exception as e:
                resultados.append((arquivo, "ERRO", f"Não foi possível abrir: {e}"))
    return resultados

layout = [
    [sg.Text("Selecione a pasta dos PDFs:"), sg.Input(key="pasta"), sg.FolderBrowse()],
    [sg.Text("Digite a palavra ou número:"), sg.Input(key="termo")],
    [sg.Button("Buscar"), sg.Button("Sair")],
    [sg.Multiline(size=(100,25), key="saida", disabled=False)]
]

window = sg.Window("Buscador de PDFs com OCR (Pré-processamento)", layout, resizable=True)

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
                for arquivo, pagina, trecho in resultados:
                    window["saida"].print(f"📄 Arquivo: {arquivo} | Página: {pagina}")
                    window["saida"].print(f"Trecho: {trecho[:200]}...\n")
                window["saida"].print("✅ Busca concluída! Resultados exibidos acima.")
            else:
                window["saida"].print("Nenhum resultado encontrado.")

window.close()
