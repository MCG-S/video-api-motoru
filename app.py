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
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
]

@app.route('/get_video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    
    if not url or not url.startswith(('http://', 'https://')):
        return jsonify({"status": "error", "message": "Gecersiz URL"}), 400

    try:
        # Her istekte rastgele bir kimlik seçiyoruz
        random_user_agent = random.choice(USER_AGENTS)

        ydl_opts = {'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'nocheckcertificate': True,
            'socket_timeout': 20, # Bağlantı süresini biraz artırdık
            
            # --- HİBRİT BAĞLANTI AYARLARI ---
            # 'source_address' satırını siliyoruz veya None yapıyoruz 
            # Böylece işletim sistemi (Hugging Face/Render) en uygun IP'yi seçer.
            'source_address': None, 
            
            # DNS çözümlemesinde hata almamak için önbelleği devre dışı bırakıyoruz
            'cachedir': False,
            
            'user_agent': random.choice(USER_AGENTS),
            'referer': 'https://www.google.com/',
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

