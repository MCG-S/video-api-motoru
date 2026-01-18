from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/get_video', methods=['GET'])
def get_video():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'status': 'error', 'message': 'Link gonderilmedi'}), 400

    # yt-dlp Ayarları (Sadece linki bul, indirme yapma)
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'simulate': True, 
        'forceurl': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Bilgileri çek
            info = ydl.extract_info(video_url, download=False)
            
            # Bazen video direkt gelir, bazen liste içinde gelir
            if 'entries' in info:
                target = info['entries'][0]
            else:
                target = info

            return jsonify({
                'status': 'success',
                'download_url': target.get('url'),
                'title': target.get('title', 'Video'),
                'platform': target.get('extractor_key')
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)