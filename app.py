from flask import Flask, render_template, request, send_file
import google.generativeai as genai
from gtts import gTTS
import os
import uuid

app = Flask(__name__)

# Configuração da Chave
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar-duvida', methods=['POST'])
def processar_duvida():
    audio_file = request.files.get('audio')
    imagem_file = request.files.get('imagem')
    
    # Prompt focado em acessibilidade
    prompt = "Aja como um técnico agrícola amigo e experiente. Responda de forma curta e simples em português, para um agricultor que não sabe ler. Analise a foto ou o áudio e dê uma solução prática."
    conteudos = [prompt]

    temp_paths = []

    try:
        # Processar Imagem
        if imagem_file and imagem_file.filename != '':
            img_path = f"img_{uuid.uuid4().hex}.jpg"
            imagem_file.save(img_path)
            temp_paths.append(img_path)
            img_upload = genai.upload_file(img_path)
            conteudos.append(img_upload)

        # Processar Áudio
        if audio_file and audio_file.filename != '':
            audio_path = f"aud_{uuid.uuid4().hex}.webm"
            audio_file.save(audio_path)
            temp_paths.append(audio_path)
            audio_upload = genai.upload_file(audio_path)
            conteudos.append(audio_upload)

        if len(conteudos) == 1:
            texto_resposta = "Olá! Por favor, tente enviar a foto ou o áudio novamente para eu poder ajudar."
        else:
            # Gerar conteúdo
            response = model.generate_content(conteudos)
            texto_resposta = response.text

    except Exception as e:
        print(f"ERRO TÉCNICO: {e}")
        texto_resposta = "Peço desculpa, tive um pequeno problema no sistema. Pode tentar falar de novo agora?"

    # Gerar Voz
    try:
        tts = gTTS(text=texto_resposta, lang='pt', tld='com.br')
        res_path = f"res_{uuid.uuid4().hex}.mp3"
        tts.save(res_path)
        temp_paths.append(res_path)
        return send_file(res_path, mimetype="audio/mpeg")
    except:
        return "Erro ao gerar áudio", 500
    finally:
        # Limpeza de ficheiros temporários para não travar o Render
        for p in temp_paths:
            if os.path.exists(p) and "res_" not in p: # Mantém a resposta para envio
                try: os.remove(p)
                except: pass

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
