import os
import sys

dirImages = os.listdir('C://Users/asafe/Downloads/AD/Images/')
dirAudio = os.listdir('C://Users/asafe/Downloads/AD/Audio/')
dirTranscripts = os.listdir('C://Users/asafe/Downloads/AD/Transcript/')

def removeFiles():
    for i in range(len(dirAudio)):
        try:
            os.remove(f"C://Users/asafe/Downloads/AD/Audio/{dirAudio[i]}")
        except Exception:
            pass

    for i in range(len(dirImages)):
        try:
            os.remove(f"C://Users/asafe/Downloads/AD/Images/{dirImages[i]}")
        except Exception:
            pass
    for i in range(len(dirTranscripts)):
        try:
            os.remove(f"C://Users/asafe/Downloads/AD/Transcript/{dirTranscripts[i]}")
        except Exception:
            pass

if __name__ == "__main__":
    # sys.argv[1] pega a primeira palavra digitada após o nome do script
    if len(sys.argv) > 1 and sys.argv[1] == "removeFiles":
        print("Executando removeFiles...")
        removeFiles()
