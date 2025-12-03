from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import random

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# ইউটিউবকে বোকা বানানোর জন্য বিভিন্ন ব্রাউজারের নাম
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    url = request.form.get('url')
    
    # সার্ভার ব্লকিং এড়ানোর জন্য এক্সট্রা সেটিংস
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'user_agent': random.choice(USER_AGENTS), # র‍্যান্ডম ব্রাউজার ব্যবহার করবে
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'status': 'success',
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration_string'),
            })
    except Exception as e:
        # এরর মেসেজ প্রিন্ট করবে যাতে বোঝা যায় সমস্যা কোথায়
        print(f"Server Error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'ইউটিউব সার্ভার আইপি ব্লক করেছে। দয়া করে লোকাল ভার্সন ব্যবহার করুন।'})

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    
    ydl_opts = {
        'format': 'best[ext=mp4][height<=720][acodec!=none]',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'nocheckcertificate': True,
        'geo_bypass': True,
        'user_agent': random.choice(USER_AGENTS),
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Download Failed: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)