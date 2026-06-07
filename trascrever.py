import sys
import os
import argparse
import subprocess

def instalar_dependencias():
    print("Instalando dependências (apenas na primeira vez)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper", "-q"])
    print("Pronto!\n")

try:
    import whisper
except ImportError:
    instalar_dependencias()
    import whisper

MODELOS = {
    "tiny":   "Tiny   — muito rápido, menos preciso",
    "base":   "Base   — rápido, boa precisão (recomendado)",
    "small":  "Small  — equilibrado",
    "medium": "Medium — preciso, mais lento",
    "large":  "Large  — máxima precisão, lento e pesado",
}

def alterar_velocidade_audio(caminho_original, velocidade):
    """
    Usa o FFmpeg instalado no sistema para alterar a velocidade do áudio
    mantendo o tom da voz natural (sem distorcer).
    """
    # Cria um nome temporário para o áudio modificado
    diretorio, nome_arquivo = os.path.split(caminho_original)
    nome_sem_ext = os.path.splitext(nome_arquivo)[0]
    caminho_temporario = os.path.join(diretorio, f"temp_{velocidade}x_{nome_sem_ext}.wav")
    
    print(f"Modificando velocidade do áudio para {velocidade}x via FFmpeg...")
    
    comando = [
        'ffmpeg',
        '-y', 
        '-i', caminho_original,
        '-filter:a', f'atempo={velocidade}',
        '-vn',  
        caminho_temporario
    ]
    
    try:
        subprocess.run(comando, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return caminho_temporario
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n[AVISO] Erro ao executar o FFmpeg. O sistema tentará transcrever na velocidade original.")
        print("Certifique-se de que o FFmpeg está instalado e configurado no seu PATH do Windows.\n")
        return caminho_original

def transcrever(caminho_audio: str, modelo: str = "base", idioma: str = None, salvar: bool = True, velocidade: float = 1.0):
    if not os.path.exists(caminho_audio):
        print(f"Erro: arquivo '{caminho_audio}' não encontrado.")
        sys.exit(1)

    audio_para_processar = caminho_audio
    usando_audio_temporario = False

    if velocidade != 1.0:
        audio_para_processar = alterar_velocidade_audio(caminho_audio, velocidade)
        if audio_para_processar != caminho_audio:
            usando_audio_temporario = True

    print(f"Carregando modelo '{modelo}'... (pode demorar na primeira vez)")
    model = whisper.load_model(modelo)

    print(f"Transcrevendo '{os.path.basename(caminho_audio)}'...\n")

    opcoes = {}
    if idioma:
        opcoes["language"] = idioma

    resultado = model.transcribe(audio_para_processar, **opcoes)
    texto = resultado["text"].strip()
    idioma_detectado = resultado.get("language", "desconhecido")

    print("TRANSCRIÇÃO: " + texto)
    print("=" * 60)
    print(f"Idioma detectado: {idioma_detectado}")

    if salvar:
        saida = os.path.splitext(caminho_audio)[0] + "_transcricao.txt"
        with open(saida, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"Arquivo salvo em: {saida}")

    if usando_audio_temporario and os.path.exists(audio_para_processar):
        try:
            os.remove(audio_para_processar)
        except Exception:
            pass

    return texto

def main():
    parser = argparse.ArgumentParser(
        description="Transcreve áudio para texto usando Whisper (100% local e gratuito)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "audio",
        help="Caminho para o arquivo de áudio (mp3, wav, m4a, ogg, flac, ashx...)",
    )
    parser.add_argument(
        "-m", "--modelo",
        default="base",
        choices=MODELOS.keys(),
        help=(
            "Modelo a usar:\n"
            + "\n".join(f"  {k}: {v}" for k, v in MODELOS.items())
            + "\n(padrão: base)"
        ),
    )
    parser.add_argument(
        "-i", "--idioma",
        default=None,
        help="Forçar idioma (ex: pt, en, es). Se omitido, detecta automaticamente.",
    )
    parser.add_argument(
        "-v", "--velocidade",
        type=float,
        default=1.0,
        help="Alterar a velocidade do áudio antes de processar (ex: 0.75 para mais lento, 1.5 para mais rápido. Padrão: 1.0)",
    )
    parser.add_argument(
        "--sem-salvar",
        action="store_true",
        help="Não salvar o resultado em arquivo .txt",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        print("\nExemplo de uso:")
        print("  python transcrever.py Som.ashx")
        print("  python transcrever.py Som.ashx -v 0.75")
        print("  python transcrever.py Som.ashx -m small -i pt -v 0.75")
        sys.exit(0)

    args = parser.parse_args()
    transcrever(
        caminho_audio=args.audio,
        modelo=args.modelo,
        idioma=args.idioma,
        salvar=not args.sem_salvar,
        velocidade=args.velocidade, 
    )

if __name__ == "__main__":
    main()