from flask import Flask, request, jsonify
import yt_dlp
import os
import random

app = Flask(__name__)

# Banlanmamak için farklı tarayıcı kimlikleri (User-Agent listesi)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

@app.route('/get_video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    
    if not url or not url.startswith(('http://', 'https://')):
        return jsonify({"status": "error", "message": "Gecersiz URL"}), 400

    try:
        # Her istekte rastgele bir kimlik seçiyoruz
        random_user_agent = random.choice(USER_AGENTS)

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'nocheckcertificate': True,
            'socket_timeout': 15,
            'user_agent': random_user_agent, # Ban önleyici kimlik
            'referer': 'https://www.google.com/', # İstek Google'dan geliyormuş gibi gösterilir
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # ... (Diğer format ayıklama kısımları aynı kalacak)
            # (Yukarıdaki kodundaki format ayıklama döngüsünü buraya ekleyebilirsin)
            
            return jsonify({"status": "success", "title": info.get('title'), "options": []}) # Örnek dönüş

    except Exception as e:
        return jsonify({"status": "error", "message": "Platform engeline takildi."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
