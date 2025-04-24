# Importa as bibliotecas necessárias
from flask import Flask, render_template, request, send_file  # Flask e funções para lidar com rotas, formulários e download
from PIL import Image, ImageOps  # Biblioteca Pillow para manipulação de imagens
import os  # Para trabalhar com arquivos e diretórios
import zipfile  # Para criar arquivos ZIP
from io import BytesIO  # Para manipular arquivos em memória
import requests  # Para baixar imagens de URLs
import time  # Para trabalhar com tempo (timestamp)
import shutil  # Para remover diretórios e arquivos
from datetime import datetime  # Para gerar nomes únicos com hora/data

# Cria o app Flask
app = Flask(__name__)

# Define os diretórios de upload e cortes
UPLOAD_FOLDER = 'static/uploads'
CORTES_FOLDER = 'static/cortes'

# Garante que os diretórios existem (senão, cria)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CORTES_FOLDER, exist_ok=True)

# Função que limpa cortes antigos (mais de 30 min)
def limpar_cortes_antigos(diretorio, tempo_limite_minutos=30):
    agora = time.time()
    for pasta in os.listdir(diretorio):
        caminho_completo = os.path.join(diretorio, pasta)
        if os.path.isdir(caminho_completo):
            tempo_modificacao = os.path.getmtime(caminho_completo)
            if agora - tempo_modificacao > tempo_limite_minutos * 60:
                shutil.rmtree(caminho_completo, ignore_errors=True)

# Rota principal do site (/, aceita GET e POST)
@app.route('/', methods=['GET', 'POST'])
def index():
    # Tamanhos de papel disponíveis
    tamanhos_papel = {
        'A4': (21.0, 29.7),
        'A3': (29.7, 42.0),
        'A5': (14.8, 21.0),
        'Letter': (21.6, 27.9)
    }

    # Se for um envio de formulário (POST)
    if request.method == 'POST':
        try:
            limpar_cortes_antigos(CORTES_FOLDER)  # Limpa cortes antigos

            # Lê os valores do formulário (com valores padrão)
            cols = int(request.form.get('cols', 2))
            rows = int(request.form.get('rows', 2))
            tamanho_folha = request.form.get('paper_size', 'A4')

            # Pega o arquivo de imagem enviado ou o link da imagem
            file = request.files.get('image')
            image_url = request.form.get('image_url', '').strip()

            # Carrega a imagem do arquivo ou do link
            if file and file.filename != '':
                image = Image.open(file.stream).convert("RGB")
            elif image_url:
                try:
                    response = requests.get(image_url)
                    image = Image.open(BytesIO(response.content)).convert("RGB")
                except Exception:
                    return render_template('index.html', tamanhos_papel=tamanhos_papel,
                                           erro="Erro ao carregar imagem do link.")
            else:
                return render_template('index.html', tamanhos_papel=tamanhos_papel,
                                       erro="Nenhuma imagem enviada.")

            # Salva a imagem original no servidor
            filename = 'imagem_original.jpg'
            path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(path)

            # Converte o tamanho da folha para centímetros
            largura_folha, altura_folha = tamanhos_papel.get(tamanho_folha, (21.0, 29.7))
            largura_total = cols * largura_folha
            altura_total = rows * altura_folha
            tamanho_final = f"{largura_total:.1f} x {altura_total:.1f} cm"

            # Converte centímetros para pixels (300 DPI)
            dpi = 300
            largura_folha_px = int((largura_folha / 2.54) * dpi)
            altura_folha_px = int((altura_folha / 2.54) * dpi)
            largura_total_px = cols * largura_folha_px
            altura_total_px = rows * altura_folha_px

            # Redimensiona a imagem para o tamanho final em pixels
            image = image.resize((largura_total_px, altura_total_px), Image.LANCZOS)

            # Calcula o tamanho de cada parte
            part_width = largura_total_px // cols
            part_height = altura_total_px // rows

            # Cria uma pasta única para os cortes (timestamp)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            pasta_cortes = os.path.join(CORTES_FOLDER, timestamp)

            try:
                os.makedirs(pasta_cortes, exist_ok=True)
            except PermissionError:
                return render_template('index.html', tamanhos_papel=tamanhos_papel,
                                       erro="Erro de permissão ao criar a pasta de cortes.")

            cortes_paths = []  # Lista de caminhos dos cortes
            margem = 20  # Adiciona borda branca de 20px

            # Loop para cortar a imagem em linhas e colunas
            for row in range(rows):
                for col in range(cols):
                    # Define as coordenadas do corte
                    left = col * part_width
                    upper = row * part_height
                    right = (col + 1) * part_width if col < cols - 1 else largura_total_px
                    lower = (row + 1) * part_height if row < rows - 1 else altura_total_px

                    # Faz o corte e adiciona margem branca
                    corte = image.crop((left, upper, right, lower))
                    corte_com_margem = ImageOps.expand(corte, border=margem, fill='white')
                    corte_filename = f"corte_{row}_{col}.jpg"
                    corte_path = os.path.join(pasta_cortes, corte_filename)
                    corte_com_margem.save(corte_path)
                    cortes_paths.append(corte_path)

            # Cria um arquivo ZIP com os cortes
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for path in cortes_paths:
                    zip_file.write(path, os.path.basename(path))
            zip_buffer.seek(0)

            # Salva o ZIP no servidor
            zip_filename = 'cortes.zip'
            zip_path = os.path.join(pasta_cortes, zip_filename)
            with open(zip_path, 'wb') as f:
                f.write(zip_buffer.read())

            # Retorna para o HTML com os dados de prévia e download
            return render_template('index.html',
                       imagem_cortada=True,
                       tamanho=tamanho_final,
                       zip_file=f"{timestamp}/cortes.zip",
                       preview_image=filename,
                       rows=rows,
                       cols=cols,
                       folha=tamanho_folha,
                       tamanhos_papel=tamanhos_papel,
                       timestamp=timestamp)

        # Caso ocorra erro, mostra mensagem
        except Exception as e:
            return render_template('index.html', tamanhos_papel=tamanhos_papel,
                                   erro=f"Ocorreu um erro inesperado: {str(e)}")

    # Caso seja GET, só renderiza a página inicial
    return render_template('index.html', tamanhos_papel=tamanhos_papel)

# Rota para baixar o arquivo ZIP
@app.route('/download/<path:zip_file>')
def download_zip(zip_file):
    path = os.path.join(CORTES_FOLDER, zip_file)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Arquivo não encontrado", 404

# Rota para página de impressão
@app.route('/imprimir/<folder>')
def imprimir(folder):
    folder_path = os.path.join(app.static_folder, 'cortes', folder)
    imagens = sorted([
        f'cortes/{folder}/{nome}' for nome in os.listdir(folder_path)
        if nome.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])
    return render_template('print.html', cortes=imagens)

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)