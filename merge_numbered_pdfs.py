#!/usr/bin/env python3
# merge_numbered_pdfs.py
# Junta todos os PDFs de uma pasta em um único PDF e adiciona numeração de páginas.
# Requisitos: python 3.7+ e pacotes: pypdf, reportlab
#
# Uso:
#   python merge_numbered_pdfs.py "C:\caminho\para\pasta"
# Ou deixe sem argumento e o script usará a pasta definida na variável DEFAULT_FOLDER.

import sys
import os
from pathlib import Path
import io

try:
    from pypdf import PdfReader, PdfWriter
except Exception as e:
    print("Erro: biblioteca 'pypdf' não encontrada. Instale com: python -m pip install pypdf")
    raise

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
except Exception as e:
    print("Erro: biblioteca 'reportlab' não encontrada. Instale com: python -m pip install reportlab")
    raise

# ======= CONFIGURAÇÃO PADRÃO (edite apenas se quiser) =======
# Se for executar via .bat, não precisa mexer aqui — passe a pasta como argumento no .bat.
DEFAULT_FOLDER = r"C:\juntaPdf"   # <-- troque este caminho só se desejar usar sem argumento
OUTPUT_FILENAME = "merged_numbered.pdf"
PAGE_NUMBER_FORMAT = "Página {num}"   # texto do número (pode personalizar)
PAGE_NUMBER_FONT_SIZE = 9
MARGIN_RIGHT = 40  # distância da margem direita para o número (em pontos)
MARGIN_BOTTOM = 20  # distância do rodapé (em pontos)
# ===========================================================

def make_page_number_overlay(width_pt, height_pt, page_num_text):
    """Cria um PDF em memória contendo somente o número de página (overlay)."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(width_pt, height_pt))
    # ajustar fonte (padrão)
    c.setFont("Helvetica", PAGE_NUMBER_FONT_SIZE)
    text_width = c.stringWidth(page_num_text, "Helvetica", PAGE_NUMBER_FONT_SIZE)
    x = width_pt - MARGIN_RIGHT - text_width
    y = MARGIN_BOTTOM
    c.drawString(x, y, page_num_text)
    c.save()
    packet.seek(0)
    return packet

def main(folder_path):
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        print(f"Pasta não encontrada: {folder_path}")
        return

    # lista de arquivos PDF na pasta (ordenada por nome)
    pdf_paths = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"])
    if not pdf_paths:
        print("Nenhum arquivo PDF encontrado na pasta.")
        return

    writer = PdfWriter()
    total_pages = 0

    print(f"Arquivos encontrados: {len(pdf_paths)}")
    # primeiro pass: contar páginas totais (opcional — podemos usar para exibir)
    for pdf_path in pdf_paths:
        reader = PdfReader(str(pdf_path))
        total_pages += len(reader.pages)

    print(f"Total de páginas que serão processadas: {total_pages}")

    current_page_number = 1
    for pdf_path in pdf_paths:
        print(f"Processando: {pdf_path.name}")
        reader = PdfReader(str(pdf_path))
        for p in reader.pages:
            # copiar a página (pypdf trabalha por referência; vamos usar o objeto diretamente)
            page = p

            # dimensões da página em pontos
            try:
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
            except Exception:
                # fallback padrão (letter)
                width, height = letter

            # criar overlay com o número de página
            page_number_text = PAGE_NUMBER_FORMAT.format(num=current_page_number)
            overlay_stream = make_page_number_overlay(width, height, page_number_text)
            overlay_reader = PdfReader(overlay_stream)
            overlay_page = overlay_reader.pages[0]

            # mesclar overlay na página (a overlay é desenhada "sobre" a página)
            page.merge_page(overlay_page)

            # adicionar a página numerada ao writer
            writer.add_page(page)
            current_page_number += 1

    output_path = folder / OUTPUT_FILENAME
    # gravar arquivo final
    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    print(f"Arquivo criado com sucesso: {output_path}")
    print("Pronto!")

if __name__ == "__main__":
    # aceitar argumento de linha de comando: pasta
    if len(sys.argv) >= 2 and sys.argv[1].strip():
        folder_arg = sys.argv[1]
    else:
        folder_arg = DEFAULT_FOLDER

    if not folder_arg or folder_arg == r"C:\juntaPdf":
        print("ATENÇÃO: Você não alterou o caminho padrão. Passe a pasta como argumento ou edite DEFAULT_FOLDER no script.")
        print("Exemplo de uso no prompt: python merge_numbered_pdfs.py \"C:\\MeusPDFs\"")
        # vamos permitir continuar só se usuário confirmar via prompt (apenas para evitar sobrescrever pasta errada)
        resp = input("Deseja continuar com a pasta DEFAULT configurada? (s/N): ").strip().lower()
        if resp != "s":
            print("Cancelado.")
            sys.exit(1)

    main(folder_arg)
