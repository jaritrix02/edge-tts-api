from flask import Flask, request, send_file, jsonify
from gtts import gTTS
import tempfile, os, base64

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "✅ Hindi TTS API Running! (Google TTS)"})

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json or {}
        text = data.get('text', '').strip()
        lang = data.get('lang', 'hi')
        if not text:
            return jsonify({"error": "Text empty hai!"}), 400
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tmp.close()
        gTTS(text=text, lang=lang, slow=False).save(tmp.name)
        return send_file(tmp.name, mimetype='audio/mpeg',
                        as_attachment=True, download_name='audio.mp3')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-base64', methods=['POST'])
def generate_base64():
    try:
        data = request.json or {}
        text = data.get('text', '').strip()
        lang = data.get('lang', 'hi')
        if not text:
            return jsonify({"error": "Text empty hai!"}), 400
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tmp.close()
        gTTS(text=text, lang=lang, slow=False).save(tmp.name)
        with open(tmp.name, 'rb') as f:
            audio_data = f.read()
        os.unlink(tmp.name)
        return jsonify({
            "success": True,
            "audio_base64": base64.b64encode(audio_data).decode('utf-8'),
            "lang": lang,
            "characters": len(text),
            "format": "mp3"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
