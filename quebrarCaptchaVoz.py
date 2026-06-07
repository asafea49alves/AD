import os
import subprocess

dirImages = os.listdir('C://Users/asafe/Downloads/AD/Images/')
dirAudio = os.listdir('C://Users/asafe/Downloads/AD/Audio/')
list = []
index = 0

def main():
    TranscriptList()
    if list.__len__() > 0:
        RenomearArchivePhoto(list)
        ExportarTranscricao()

def ValidIfContaisTextOfNumber(frase):

    listaNumerosditada = ["um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "zero"]
    listaNumerosNumeral = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]

    if frase in listaNumerosditada:
        indice = listaNumerosditada.index(frase)
        return str(listaNumerosNumeral[indice])

    print("Validando padrões de letras e frases...")
    
    print("Validação concluída.")
    

def TranscriptList():
    global index
    
    while index < len(dirAudio):

        result = subprocess.run([f"python3", "trascrever.py", f"C://Users/asafe/Downloads/AD/Audio/{dirAudio[index]}", "-v", "0.9"], capture_output=True, text=True)
        print(f"Resultado do comando: {result.stdout}")

        for linha in result.stdout.splitlines():

            if "TRANSCRIÇÃO:" in linha:
                transcricao = linha.split("TRANSCRIÇÃO:")[1].strip()
                texto = ValidIfContaisTextOfNumber(transcricao)

                separed = transcricao.replace(" ", ",").replace(".", "")
                listCaracters = separed.split(",")

                for i in range(len(listCaracters)):
                    if listCaracters[i].lower().__contains__("ps") or listCaracters[i].lower().__contains__("psu") or listCaracters[i].lower().__contains__("ips") or listCaracters[i].lower().__contains__("ipsu"):
                        listCaracters[i] = "y"
                        
                print(f"Lista de caracteres após validação: {listCaracters}")
                texto = "".join(listCaracters)
                print(f"Texto final após validação: {texto}")
                list.append(texto)
                break
        index += 1

def RenomearArchivePhoto(list):

    for i in range(len(list)):
        os.rename(f"C://Users/asafe/Downloads/AD/Images/{dirImages[i]}", f"C://Users/asafe/Downloads/AD/Images/{list[i]}.png")

    

def ExportarTranscricao():
    with open(f"C://Users/asafe/Downloads/AD/Transcript/transcricoes{index}.txt", "w", encoding="utf-8") as f:
        for item in list:
            f.write(item + "\n")

if __name__ == "__main__":
    main()