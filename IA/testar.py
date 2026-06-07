import os
import glob
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers

# ==========================================
# 1. CONFIGURAÇÕES E PARÂMETROS
# ==========================================
PASTA_NOVOS_CAPTCHAS = "./novos_captchas"  # Altere para a pasta com as fotos que quer testar
MODELO_PATH = "modelo_captcha.h5"
IMG_WIDTH = 200
IMG_HEIGHT = 50

# ATENÇÃO: Monte exatamente o mesmo alfabeto que a sua rede usou no treino
# Se o seu alfabeto real do treino tinha maiúsculas ou menos letras, ajuste aqui:
characters = sorted(list('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))

# Cria as tabelas de tradução de número para caractere
char_to_num = layers.StringLookup(vocabulary=list(characters), mask_token=None)
num_to_char = layers.StringLookup(vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True)

# ==========================================
# 2. CARREGAR MODELO COM FUNÇÃO CTC EMBUTIDA
# ==========================================
if not os.path.exists(MODELO_PATH):
    print(f"Erro: O arquivo '{MODELO_PATH}' não foi encontrado. Certifique-se de que ele está na mesma pasta deste script.")
    exit()

# Carrega o modelo ignorando a função de perda (já que para testar não precisamos calcular o erro/loss)
model = tf.keras.models.load_model(MODELO_PATH, custom_objects={"ctc_loss": lambda y_true, y_pred: y_pred})
print("[+] Modelo de CAPTCHA carregado com sucesso!\n")

# ==========================================
# 3. FUNÇÕES DE TRATAMENTO E DECODIFICAÇÃO
# ==========================================
def preprocessar_imagem(caminho_imagem):
    """Lê a imagem do disco e adapta para o formato que a rede neural espera"""
    img = tf.io.read_file(caminho_imagem)
    img = tf.io.decode_png(img, channels=1) # Carrega em escala de cinza
    img = tf.image.convert_image_dtype(img, tf.float32) # Normaliza os pixels entre 0 e 1
    img = tf.image.resize(img, [IMG_HEIGHT, IMG_WIDTH]) # Redimensiona
    img = tf.transpose(img, perm=[1, 0, 2]) # Transpõe largura por altura (exigência da RNN)
    img = tf.expand_dims(img, axis=0) # Adiciona a dimensão do lote (Batch size = 1)
    return img

def decodificar_previsao(predicao_bruta):
    """Aplica a regra matemática do CTC para limpar repetições e espaços vazios"""
    # Descobre o tamanho das fatias horizontais geradas pela rede
    input_len = np.ones(predicao_bruta.shape[0]) * predicao_bruta.shape[1]
    
    # Decodificador nativo do TensorFlow para a lógica do CTC (Greedy)
    results = tf.keras.backend.ctc_decode(predicao_bruta, input_length=input_len, greedy=True)[0][0]
    
    # Limpa os índices e traduz os números de volta para letras legíveis
    for res in results:
        res = res[res != -1] # Remove preenchimentos inválidos do TF
        letras = num_to_char(res)
        texto_limpo = tf.strings.reduce_join(letras).numpy().decode("utf-8")
        return texto_limpo

# ==========================================
# 4. VARREDURA DA PASTA E EXECUÇÃO
# ==========================================
# Cria a pasta automaticamente caso ela não exista, para evitar erros
if not os.path.exists(PASTA_NOVOS_CAPTCHAS):
    os.makedirs(PASTA_NOVOS_CAPTCHAS)
    print(f"A pasta '{PASTA_NOVOS_CAPTCHAS}' foi criada. Coloque suas imagens dentro dela para testar.")
    exit()

# Busca por qualquer imagem (PNG, JPG ou JPEG) dentro da pasta externa
extensoes = ["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG"]
arquivos_encontrados = []
for ext in extensoes:
    arquivos_encontrados.extend(glob.glob(os.path.join(PASTA_NOVOS_CAPTCHAS, ext)))

if len(arquivos_encontrados) == 0:
    print(f"Nenhuma imagem encontrada em '{PASTA_NOVOS_CAPTCHAS}'. Jogue algumas fotos lá e rode o script novamente.")
    exit()

print(f"Encontrados {len(arquivos_encontrados)} arquivos para decifrar. Iniciando processamento...\n")
print("-" * 60)
print(f"{'NOME DO ARQUIVO':<35} | {'TEXTO DECIFRADO':<20}")
print("-" * 60)

# Loop principal: passa de arquivo em arquivo decifrando o conteúdo
for caminho_completo in arquivos_encontrados:
    try:
        # 1. Trata os pixels da imagem
        imagem_preparada = preprocessar_imagem(caminho_completo)
        
        # 2. Passa a imagem pela inteligência do modelo (.h5)
        predicao = model.predict(imagem_preparada, verbose=0)
        
        # 3. Limpa a saída confusa usando o algoritmo do CTC
        texto_final = decodificar_previsao(predicao)
        
        # Pega apenas o nome do arquivo limpo (ex: "foto1.png") para exibir na tabela
        nome_arquivo = os.path.basename(caminho_completo)
        
        print(f"{nome_arquivo:<35} | {texto_final:<20}")
        
    except Exception as e:
        nome_arquivo = os.path.basename(caminho_completo)
        print(f"{nome_arquivo:<35} | [ERRO AO PROCESSAR]: {str(e)}")

print("-" * 60)
print("[+] Processamento concluído!")