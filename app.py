"""
================================================
  EDGE TTS API SERVER
  Deploy: Railway.app
  Use: N8N se text bhejo → MP3 wapas aaye
================================================
"""

from flask import Flask, request, send_file, jsonify
import edge_tts
import asyncio
import tempfile
import os
import base64

app = Flask(__name__)

# ─── HEALTH CHECK ─────────────────────────────
@app.route('/')
def home():
    return jsonify({
        "status": "✅ Edge TTS API Running!",
        "endpoints": {
            "POST /generate": "Text → MP3 file (download)",
            "POST /generate-base64": "Text → Base64 MP3 (N8N ke liye BEST)",
            "GET  /voices": "Saari Hindi voices list"
        },
        "example": {
            "url": "/generate-base64",
            "body": {
                "text": "Namaskar doston!",
                "voice": "hi-IN-MadhurNeural",
                "speed": "+0%",
                "pitch": "+0Hz"
            }
        }
    })


# ─── VOICES LIST ──────────────────────────────
@app.route('/voices', methods=['GET'])
def voices():
    return jsonify({
        "hindi_voices": [
            {"id": "hi-IN-MadhurNeural",  "gender": "Male",   "style": "YouTube Best ⭐"},
            {"id": "hi-IN-SwaraNeural",   "gender": "Female", "style": "Professional"},
            {"id": "hi-IN-NeerjaNeural",  "gender": "Female", "style": "Natural"},
        ],
        "english_voices": [
            {"id": "en-US-GuyNeural",    "gender": "Male",   "style": "Professional"},
            {"id": "en-US-JennyNeural",  "gender": "Female", "style": "Friendly"},
        ]
    })


# ─── GENERATE MP3 (Direct Download) ──────────
@app.route('/generate', methods=['POST'])
def generate():
    """
    N8N → POST /generate
    Body: { "text": "...", "voice": "hi-IN-MadhurNeural" }
    Returns: MP3 file
    """
    try:
        data  = request.json or {}
        text  = data.get('text', '').strip()
        voice = data.get('voice', 'hi-IN-MadhurNeural')
        speed = data.get('speed', '+0%')
        pitch = data.get('pitch', '+0Hz')

        if not text:
            return jsonify({"error": "Text field empty hai!"}), 400

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tmp.close()

        async def run():
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=speed,
                pitch=pitch
            )
            await communicate.save(tmp.name)

        asyncio.run(run())

        return send_file(
            tmp.name,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='audio.mp3'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── GENERATE BASE64 (N8N ke liye BEST) ──────
@app.route('/generate-base64', methods=['POST'])
def generate_base64():
    """
    N8N → POST /generate-base64
    Body: { "text": "...", "voice": "hi-IN-MadhurNeural" }
    Returns: { "audio_base64": "...", "voice": "...", "characters": 123 }
    N8N mein base64 ko decode karke use karo!
    """
    try:
        data  = request.json or {}
        text  = data.get('text', '').strip()
        voice = data.get('voice', 'hi-IN-MadhurNeural')
        speed = data.get('speed', '+0%')
        pitch = data.get('pitch', '+0Hz')

        if not text:
            return jsonify({"error": "Text field empty hai!"}), 400

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tmp.close()

        async def run():
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=speed,
                pitch=pitch
            )
            await communicate.save(tmp.name)

        asyncio.run(run())

        # MP3 ko base64 mein convert karo
        with open(tmp.name, 'rb') as f:
            audio_data = f.read()

        os.unlink(tmp.name)

        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        return jsonify({
            "success": True,
            "audio_base64": audio_base64,
            "voice": voice,
            "characters": len(text),
            "format": "mp3",
            "usage": "N8N mein 'Write Binary File' node se decode karo"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── START ────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"\n✅ Edge TTS API Server running on port {port}\n")
    app.run(host='0.0.0.0', port=port, debug=False)
