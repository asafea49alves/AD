import os
import glob
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

# ==========================================
# 1. CONFIGURAÇÕES E PARÂMETROS
# ==========================================
DATA_DIR = "./Images"
BATCH_SIZE = 16
IMG_WIDTH = 200
IMG_HEIGHT = 50

# Descobre quais caracteres existem no seu dataset (ex: números e letras minúsculas)
search_path = os.path.join(DATA_DIR, "*.png")
img_files = glob.glob(search_path)
all_labels = [os.path.splitext(os.path.basename(f))[0] for f in img_files]

# Cria o vocabulário único de caracteres ordenados
characters = sorted(list(set("".join(all_labels))))
print(f"Caracteres encontrados ({len(characters)}): {characters}")

# Tabelas de mapeamento: Caractere <-> Número
char_to_num = layers.StringLookup(vocabulary=list(characters), mask_token=None)
num_to_char = layers.StringLookup(vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True)

# Define o tamanho máximo de um CAPTCHA (ex: 4 ou 5 caracteres)
max_length = max([len(label) for label in all_labels])

# ==========================================
# 2. PIPELINE DE PROCESSAMENTO DE DADOS
# ==========================================
def process_image_labels(img_path):
    # 1. Lê e decodifica a imagem como escala de cinza (1 canal)
    img = tf.io.read_file(img_path)
    img = tf.io.decode_png(img, channels=1)
    # 2. Converte para float32 e normaliza para o intervalo [0, 1]
    img = tf.image.convert_image_dtype(img, tf.float32)
    # 3. Redimensiona para o tamanho padrão
    img = tf.image.resize(img, [IMG_HEIGHT, IMG_WIDTH])
    # 4. Transpõe a imagem pois queremos que a largura seja a dimensão do tempo (sequência)
    img = tf.transpose(img, perm=[1, 0, 2])
    
    # Extrai o texto do caminho do arquivo
    label_str = tf.strings.split(img_path, os.path.sep)[-1]
    label_str = tf.strings.split(label_str, ".")[0]
    # Converte as letras em números usando o StringLookup
    label = char_to_num(tf.strings.unicode_split(label_str, input_encoding="UTF-8"))
    
    return img, label

# Criando o Dataset do TensorFlow
dataset = tf.data.Dataset.from_tensor_slices(img_files)
dataset = (
    dataset.map(process_image_labels, num_parallel_calls=tf.data.AUTOTUNE)
    .batch(BATCH_SIZE)
    .prefetch(buffer_size=tf.data.AUTOTUNE)
)

# ==========================================
# 3. CONSTRUÇÃO DA ARQUITETURA CRNN
# ==========================================
def build_model():
    # Entrada da Imagem (Transposta: Largura, Altura, Canal)
    input_img = layers.Input(shape=(IMG_WIDTH, IMG_HEIGHT, 1), name="image", dtype="float32")

    # Bloco CNN (Extração de Características Visuais)
    x = layers.Conv2D(32, (3, 3), activation="relu", padding="same", name="Conv1")(input_img)
    x = layers.MaxPooling2D((2, 2), name="pool1")(x)
    
    x = layers.Conv2D(64, (3, 3), activation="relu", padding="same", name="Conv2")(x)
    x = layers.MaxPooling2D((2, 2), name="pool2")(x)

    # Ajuste de Formato (Reshape) para conectar a CNN à RNN
    # Reduzimos as dimensões da Altura e Canais em um vetor contínuo por fatia de Largura
    new_shape = ((IMG_WIDTH // 4), (IMG_HEIGHT // 4) * 64)
    x = layers.Reshape(target_shape=new_shape, name="reshape")(x)
    x = layers.Dense(64, activation="relu", name="dense1")(x)

    # Bloco RNN (Análise Sequencial Bidirecional)
    x = layers.Bidirectional(layers.LSTM(128, return_sequences=True, dropout=0.25), name="LSTM1")(x)
    x = layers.Bidirectional(layers.LSTM(64, return_sequences=True, dropout=0.25), name="LSTM2")(x)

    # Camada de Saída (+1 para o token em branco/blank exigido pelo CTC)
    output = layers.Dense(len(char_to_num.get_vocabulary()) + 1, activation="softmax", name="dense2")(x)

    return models.Model(inputs=input_img, outputs=output, name="ocr_model")

model = build_model()
model.summary()

# ==========================================
# 4. FUNÇÃO DE PERDA CTC E COMPILAÇÃO
# ==========================================
def ctc_loss(y_true, y_pred):
    # Calcula o tamanho do lote dinamicamente
    batch_len = tf.cast(tf.shape(y_true)[0], dtype="int64")
    
    # Input length: tamanho da sequência gerada pela nossa rede (IMG_WIDTH // 4)
    input_length = tf.cast(tf.shape(y_pred)[1], dtype="int64")
    input_length = input_length * tf.ones(shape=(batch_len, 1), dtype="int64")
    
    # Label length: tamanho real do texto do CAPTCHA
    label_length = tf.cast(tf.shape(y_true)[1], dtype="int64")
    label_length = label_length * tf.ones(shape=(batch_len, 1), dtype="int64")

    return tf.keras.backend.ctc_batch_cost(y_true, y_pred, input_length, label_length)

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss=ctc_loss)

# ==========================================
# 5. TREINAMENTO
# ==========================================
EPOCHS = 50 # Ajuste dependendo do tamanho do seu dataset
print("\nIniciando o treinamento...")
history = model.fit(dataset, epochs=EPOCHS)

# Salva o modelo treinado
model.save("modelo_captcha.h5")
print("\nModelo treinado e salvo com sucesso como 'modelo_captcha.h5'!")