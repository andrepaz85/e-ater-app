from flask import Flask, render_template, request, send_file
import google.generativeai as genai
from gtts import gTTS
import os
import io
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
    
    prompt = "Você é um agrônomo amigo. Responda de forma curta e simples em português para um agricultor. Ajude com o que ver na foto ou ouvir no áudio."
    conteudos = [prompt]

    try:
        # Processa Imagem
        if imagem_file:
            img_bytes = imagem_file.read()
            if len(img_bytes) > 0:
                conteudos.append({'mime_type': 'image/jpeg', 'data': img_bytes})

        # Processa Áudio
        if audio_file:
            aud_bytes = audio_file.read()
            if len(aud_bytes) > 0:
                conteudos.append({'mime_type': 'audio/webm', 'data': aud_bytes})

        # Se nada foi enviado
        if len(conteudos) == 1:
            texto_resposta = "Não recebi sua foto ou áudio. Tente novamente, por favor."
        else:
            # Chama a IA
            response = model.generate_content(conteudos)
            texto_resposta = response.text

    except Exception as e:
        print(f"Erro: {e}")
        texto_resposta = "Tive um problema para entender. Pode repetir?"

    # Gera a Voz da Resposta
    try:
        tts = gTTS(text=texto_resposta, lang='pt', tld='com.br')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return send_file(fp, mimetype="audio/mpeg")
    except:
        return "Erro no áudio", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
