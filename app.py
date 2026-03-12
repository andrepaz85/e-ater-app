from flask import Flask, render_template, request, send_file
import google.generativeai as genai
from gtts import gTTS
import os
import uuid

app = Flask(__name__)

# O Render vai injetar sua chave aqui com segurança depois
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar-duvida', methods=['POST'])
def processar_duvida():
    # Recebe os arquivos do celular
    audio_file = request.files.get('audio')
    imagem_file = request.files.get('imagem')
    
    conteudos = ["""Você é um especialista em agroecologia do projeto 'e-ATER Agroecologia'. 
    O usuário é um agricultor familiar que não sabe ler. 
    Responda de forma extremamente simples, curta, direta e amigável, como se estivesse conversando na roça. 
    Não use palavras difíceis. Vá direto ao ponto para ajudar com a praga, manejo ou dúvida."""]

    temp_files = []

    try:
        # Processa a Imagem (se tiver)
        if imagem_file:
            img_path = f"temp_{uuid.uuid4().hex}.jpg"
            imagem_file.save(img_path)
            # O Gemini precisa da imagem abrindo pelo PIL na API atual, ou upload
            img_upload = genai.upload_file(path=img_path)
            conteudos.append(img_upload)
            temp_files.append(img_path)

        # Processa o Áudio (se tiver)
        if audio_file:
            audio_path = f"temp_{uuid.uuid4().hex}.webm"
            audio_file.save(audio_path)
            audio_upload = genai.upload_file(path=audio_path)
            conteudos.append(audio_upload)
            temp_files.append(audio_path)

        # Gera a resposta com a IA
        if not audio_file and not imagem_file:
            texto_resposta = "Por favor, grave um áudio ou envie uma foto."
        else:
            resposta = model.generate_content(conteudos)
            texto_resposta = resposta.text

    except Exception as e:
        texto_resposta = "Desculpe, tive um problema para entender a gravação. Tente falar um pouco mais perto do celular."

    # Transforma a resposta em Voz
    tts = gTTS(text=texto_resposta, lang='pt', tld='com.br')
    resposta_audio_path = f"resposta_{uuid.uuid4().hex}.mp3"
    tts.save(resposta_audio_path)

    # Limpa os arquivos temporários do servidor
    for f in temp_files:
        if os.path.exists(f): os.remove(f)

    # Devolve o áudio pronto pro celular tocar
    return send_file(resposta_audio_path, mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(debug=True)
