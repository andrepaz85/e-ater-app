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
    
    # Instruções simplificadas para a IA
    prompt = "Aja como um técnico agrícola amigo. Responda em português simples, para quem não sabe ler. Seja direto e ajude com a foto ou áudio enviado."
    conteudos = [prompt]

    try:
        if imagem_file:
            # Salva temporariamente para enviar à IA
            img_path = f"{uuid.uuid4().hex}.jpg"
            imagem_file.save(img_path)
            img_data = genai.upload_file(img_path)
            conteudos.append(img_data)
        
        if audio_file:
            audio_path = f"{uuid.uuid4().hex}.webm"
            audio_file.save(audio_path)
            audio_data = genai.upload_file(audio_path)
            conteudos.append(audio_data)

        # Gera a resposta
        resposta = model.generate_content(conteudos)
        texto_resposta = resposta.text

    except Exception as e:
        print(f"Erro: {e}")
        texto_resposta = "Não consegui entender bem. Pode tentar falar de novo ou tirar outra foto?"

    # Transforma em áudio (Voz)
    tts = gTTS(text=texto_resposta, lang='pt', tld='com.br')
    res_path = f"res_{uuid.uuid4().hex}.mp3"
    tts.save(res_path)
    
    return send_file(res_path, mimetype="audio/mpeg")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
