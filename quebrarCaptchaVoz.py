import os
import subprocess
dirImages = os.listdir('C://Users/asafe/Downloads/AD/Images/')
dirAudio = os.listdir('C://Users/asafe/Downloads/AD/Audio/')
dirBase = 'C://Users/asafe/Downloads/'
list = []
index = 0

def main():
    TranscriptList()
    if list.__len__() > 0:
        RenomearArchivePhoto(list)
        ExportarTranscricao()
    

def TranscriptList():
    global index
    
    while index < len(dirAudio):

        result = subprocess.run([f"python3", "trascrever.py", f"{dirBase}/AD/Audio/{dirAudio[index]}", "-v", "0.9"], capture_output=True, text=True)
        print(f"Resultado do comando: {result.stdout}")

        for linha in result.stdout.splitlines():

            if "TRANSCRIÇÃO:" in linha:
                transcricao = linha.split("TRANSCRIÇÃO:")[1].strip()

                import ManagerValidateTypesWords as mv
                texto = mv.corrigir_audio_captcha_avancado(transcricao)
                print(f"Texto após correção avançada: {texto}")

                separed = transcricao.replace(" ", ",").replace(".", "")
                listCaracters = separed.split(",")
                        
                print(f"Lista de caracteres após validação: {listCaracters}")
                texto = "".join(listCaracters)
                print(f"Texto final após validação: {texto}")
                list.append(texto)
                break
        index += 1

def RenomearArchivePhoto(list):

    for i in range(len(list)):
        os.rename(f"{dirBase}/AD/Images/{dirImages[i]}", f"{dirBase}/AD/Images/{list[i]}.png")

    

def ExportarTranscricao():
    with open(f"{dirBase}/AD/Transcript/transcricoes{index}.txt", "w", encoding="utf-8") as f:
        for item in list:
            f.write(item + "\n")

if __name__ == "__main__":
    main()