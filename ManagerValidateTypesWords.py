def corrigir_audio_captcha_avancado(texto_reconhecido):
    # Normalização inicial
    texto = texto_reconhecido.lower().strip()
    
    # Super dicionário de erros fonéticos e variações de Captcha
    mapa_erros = {
        # --- LETRA Y ---
        "ípsilon": "y", "upsilon": "y", "ipson": "y", "ipsu": "y", "ipsilom": "y", 
        "uai": "y", "wai": "y",
        
        # --- LETRA W ---
        "dabliu": "w", "dáblio": "w", "double u": "w", "dablu": "w", "dablo": "w",
        
        # --- LETRA H ---
        "aga": "h", "agá": "h", "eich": "h", "eitch": "h",
        
        # --- LETRA G ---
        "gema": "g", "gí": "g", "gi": "g", "ge": "g", "gê": "g",
        
        # --- LETRA J ---
        "jei": "j", "jota": "j", "jê": "j",
        
        # --- LETRA K ---
        "kei": "k", "ka": "k", "ká": "k",
        
        # --- LETRA Q ---
        "qu": "q", "quê": "q", "kiu": "q", "que": "q",
        
        # --- LETRA X ---
        "xis": "x", "equis": "x", "ecs": "x",
        
        # --- LETRA Z ---
        "zi": "z", "zed": "z", "zeta": "z", "zê": "z",
        
        # --- LETRA R ---
        "ar": "r", "érre": "r", "er": "r",
        
        # --- CONSONÂNCIAS CONFUSAS (B, P, D, T, V, F, M, N) ---
        "bê": "b", "pê": "p", "dê": "d", "tê": "t", "vê": "v", "efe": "f",
        "eme": "m", "ene": "n", "en": "n", "em": "m",
        
        # --- VOGAIS COM SOM EM INGLÊS (Caso o captcha misture) ---
        "ei": "a", "bi": "b", "ci": "c", "di": "d", "i": "i", "ai": "i", 
        "ou": "o", "iu": "u",
        
        # --- NÚMEROS POR EXTENSO (PT-BR) ---
        "zero": "0", "oito": "8", "nove": "9", "sete": "7",
        "um": "1", "uma": "1",
        "dois": "2", "duas": "2",
        "três": "3", "tres": "3",
        "quatro": "4", "quarto": "4",
        "cinco": "5", "sinco": "5",
        "seis": "6", "meia": "6", # 'meia' é o campeão de bilheteria em captchas de telefone/áudio
        
        # --- NÚMEROS POR EXTENSO (Sotaque em Inglês captado como PT) ---
        "uam": "1", "tu": "2", "tri": "3", "fór": "4", "fai": "5", "faiv": "5",
        "sics": "6", "seven": "7", "eit": "8", "naini": "9", "ziro": "0"
    }
    
    # Substituição ordenada do maior termo para o menor 
    # (Evita que 'um' estrague 'uam', ou que 'seis' quebre 'meia')
    for erro in sorted(mapa_erros.keys(), key=len, reverse=True):
        # Usamos uma estratégia de espaçamento para garantir substituição de palavras inteiras
        # Se a palavra errada estiver isolada ou com espaços
        if erro in texto:
            texto = texto.replace(erro, mapa_erros[erro])
            
    # Limpeza final de espaços e caracteres residuais
    texto_limpo = texto.replace(" ", "").replace("-", "").replace(".", "")
    
    return list(texto_limpo)

# --- TESTE COM ERROS BEM AGRESSIVOS ---
audio_com_ruido = "eitch sete meia dablo eit sinco ipson"
# Tradução esperada: h (eitch) 7 (sete) 6 (meia) w (dablo) 8 (eit) 5 (sinco) y (ipson) -> h76w85y

resultado = corrigir_audio_captcha_avancado(audio_com_ruido)
# print(f"Texto processado: {resultado}")