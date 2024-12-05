from flask import Flask, send_file

app = Flask(__name__)

@app.route('/download/<filename>')
def download(filename):
    file_path = f"/home/sikandar/Movies/{filename}"
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)