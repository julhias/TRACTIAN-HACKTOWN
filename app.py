import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from deep_translator import GoogleTranslator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfMerger
import streamlit as st

# Função para extrair texto e imagens por página e fazer OCR
def extrair_texto_e_imagem_por_pagina(caminho_pdf):
    paginas_texto = []
    imagens_por_pagina = []
    with fitz.open(caminho_pdf) as pdf_file:
        for page_num in range(pdf_file.page_count):
            page = pdf_file[page_num]
            img = page.get_pixmap()
            img_path = f"temp_page_{page_num}.png"
            img.save(img_path)
            texto_ocr = pytesseract.image_to_string(Image.open(img_path))
            paginas_texto.append(texto_ocr)
            imagens_por_pagina.append(img_path)
    return paginas_texto, imagens_por_pagina

# Função para criar um PDF temporário para cada página traduzida
def criar_pdf_pagina(texto_traduzido, imagem_pagina, nome_pdf_temp):
    c = canvas.Canvas(nome_pdf_temp, pagesize=letter)
    largura_pagina, altura_pagina = letter
    c.drawImage(imagem_pagina, 0, 0, width=largura_pagina, height=altura_pagina)

    y_position = altura_pagina - 100  # posição inicial para o texto
    for line in texto_traduzido.split('\n'):
        c.drawString(72, y_position, line.strip())
        y_position -= 12
        if y_position < 50:  # nova página se ultrapassar o limite
            c.showPage()
            y_position = altura_pagina - 100

    c.save()

# Função principal para traduzir o PDF
def traduzir_pdf(caminho_pdf):
    # Extrair texto e imagens por página
    paginas_texto, imagens_por_pagina = extrair_texto_e_imagem_por_pagina(caminho_pdf)

    # Traduzir cada página e criar PDFs temporários
    translator = GoogleTranslator(source='en', target='pt')
    pdf_temp_paths = []

    for i, texto in enumerate(paginas_texto):
        texto_traduzido = translator.translate(texto)
        nome_pdf_temp = f"temp_translated_page_{i}.pdf"
        criar_pdf_pagina(texto_traduzido, imagens_por_pagina[i], nome_pdf_temp)
        pdf_temp_paths.append(nome_pdf_temp)

    # Combinar PDFs temporários em um PDF final
    output_pdf = "manual_traduzido_completo.pdf"
    merger = PdfMerger()

    for pdf_path in pdf_temp_paths:
        merger.append(pdf_path)

    merger.write(output_pdf)
    merger.close()

    # Limpeza dos arquivos temporários
    for img_path in imagens_por_pagina + pdf_temp_paths:
        if os.path.exists(img_path):
            os.remove(img_path)

    return output_pdf

# Streamlit Interface
st.title("Tradutor de PDF")
uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

if uploaded_file is not None:
    with open("uploaded.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Arquivo carregado com sucesso!")

    if st.button("Traduzir PDF"):
        output_pdf = traduzir_pdf("uploaded.pdf")
        st.success("Tradução concluída!")
        st.download_button("Baixar PDF traduzido", output_pdf)



