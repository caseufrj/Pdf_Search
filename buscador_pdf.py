import os
import pdfplumber

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

def main():
    pasta = input("Digite o caminho da pasta com os PDFs: ")
    termo = input("Digite a palavra ou número a buscar: ")
    resultados = buscar_em_pdfs(pasta, termo)

    if resultados:
        with open("resultados.txt", "w", encoding="utf-8") as f:
            for arquivo, pagina, trecho in resultados:
                f.write(f"Arquivo: {arquivo} | Página: {pagina}\n")
                f.write(f"Trecho: {trecho[:200]}...\n\n")
        print("Busca concluída! Resultados salvos em resultados.txt")
    else:
        print("Nenhum resultado encontrado.")

if __name__ == "__main__":
    main()
