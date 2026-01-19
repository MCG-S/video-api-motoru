from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/get_video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    
    # URL Güvenlik Kontrolü
    if not url or not url.startswith(('http://', 'https://')):
        return jsonify({"status": "error", "message": "Gecersiz URL formati"}), 400

    try:
        # Sunucu Kaynaklarını Korumak İçin Ayarlar
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'nocheckcertificate': True,
            'socket_timeout': 15,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Ana Veriler
            title = info.get('title', 'Bilinmeyen Video')
            thumbnail = info.get('thumbnail', '')
            platform = info.get('extractor_key', 'Unknown')
            options = []

            # Kapak Resmi Seçeneği
            if thumbnail:
                options.append({
                    'type': 'image',
                    'quality': 'Kapak Resmi (HD)',
                    'format': 'jpg',
                    'url': thumbnail,
                    'size': 'Bilinmiyor'
                })

            # Formatları Ayıkla (Sadece doğrudan linki olanlar)
            formats = info.get('formats', [])
            for f in formats:
                if 'url' not in f or '.m3u8' in f['url'] or 'manifest' in f['url']:
                    continue

                filesize = f.get('filesize') or f.get('filesize_approx')
                size_str = f"{filesize / (1024 * 1024):.1f} MB" if filesize else "Bilinmiyor"

                # Video + Ses (Progressive)
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    height = f.get('height', 0)
                    options.append({
                        'type': 'video',
                        'quality': f"{height}p",
                        'format': f.get('ext', 'mp4'),
                        'url': f['url'],
                        'size': size_str,
                        'height': height
                    })
                
                # Sadece Ses
                elif f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    options.append({
                        'type': 'audio',
                        'quality': 'Ses (MP3/M4A)',
                        'format': f.get('ext', 'm4a'),
                        'url': f['url'],
                        'size': size_str,
                        'height': 0
                    })

            # Kalite Sıralaması (Yüksekten düşüğe)
            options.sort(key=lambda x: x.get('height', 0), reverse=True)

            return jsonify({
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "platform": platform,
                "options": options
            })

    except Exception as e:
        return jsonify({"status": "error", "message": "Platform engeline takildi veya link hatali."}), 500

if __name__ == '__main__':
    # Render'ın dinamik port ataması için zorunlu
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
