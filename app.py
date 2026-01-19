from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/get_video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({"status": "error", "message": "URL parametresi eksik"}), 400

    try:
        # Seçenekleri al (Listeletme Modu)
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 1. Başlık ve Resim
            title = info.get('title', 'Bilinmeyen Video')
            thumbnail = info.get('thumbnail', '')
            platform = info.get('extractor_key', 'Unknown')

            options = []

            # 2. Resim Seçeneği (Thumbnail)
            if thumbnail:
                options.append({
                    'type': 'image',
                    'quality': 'Kapak Resmi (HD)',
                    'format': 'jpg',
                    'url': thumbnail,
                    'size': 'Bilinmiyor'
                })

            # 3. Formatları Tara ve Sınıflandır
            formats = info.get('formats', [])
            for f in formats:
                # Sadece doğrudan erişilebilir linkleri al (m3u8 gibi yayınları atla)
                if 'url' not in f or '.m3u8' in f['url']:
                    continue

                # Dosya boyutunu hesapla (varsa)
                filesize = f.get('filesize')
                size_str = f"{filesize / (1024 * 1024):.1f} MB" if filesize else "Bilinmiyor"

                # A) VİDEO (Hem Sesi Hem Görüntüsü Olanlar)
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    height = f.get('height', 0)
                    options.append({
                        'type': 'video',
                        'quality': f"{height}p Video + Ses",
                        'format': f.get('ext', 'mp4'),
                        'url': f['url'],
                        'size': size_str,
                        'height': height # Sıralama için
                    })
                
                # B) SADECE SES (MP3/M4A)
                elif f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    options.append({
                        'type': 'audio',
                        'quality': 'Ses Dosyası (Müzik)',
                        'format': f.get('ext', 'mp3'),
                        'url': f['url'],
                        'size': size_str,
                        'height': 0
                    })

            # Videoları kalitesine göre sırala (Yüksekten düşüğe)
            # Python'da listeyi sıralama
            options.sort(key=lambda x: x.get('height', 0), reverse=True)

            return jsonify({
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "platform": platform,
                "options": options
            })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
