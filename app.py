from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

# ডাউনলোড ফোল্ডার
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    url = request.form.get('url')
    ydl_opts = {'quiet': True, 'no_warnings': True}
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
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    
    # 🔴 উইন্ডোজের জন্য স্পেশাল সেটিংস 🔴
    # '18' এবং '22' হলো ইউটিউবের ইউনিভার্সাল ফরম্যাট কোড।
    # এগুলো যেকোনো পিসিতে সাউন্ডসহ স্মুথলি চলবে।
    ydl_opts = {
        'format': '22/18/best[ext=mp4][acodec!=none]',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'overwrites': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)