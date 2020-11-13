import flask
from flask import request, stream_with_context

import os
from flask import Flask, render_template
from werkzeug import secure_filename

app = Flask(__name__)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    # 设置请求内容的大小限制，即限制了上传文件的大小
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

    # 设置上传文件存放的目录
    UPLOAD_FOLDER = './upload'
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    # 设置允许上传的文件类型
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'xlsx'])

    # 检查文件类型是否合法
    def allowed_file(filename):
        # 判断文件的扩展名是否在配置项ALLOWED_EXTENSIONS中
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    if request.method == 'POST':
        # 获取上传过来的文件对象
        company = request.args
        file = request.files['file']
        # 检查文件对象是否存在，且文件名合法
        if file and allowed_file(file.filename):
            # 去除文件名中不合法的内容
            filename = secure_filename(file.filename)
            # 将文件保存在本地UPLOAD_FOLDER目录下
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return 'Upload Successfully'
        else:  # 文件不合法
            return 'Upload Failed'
    else:  # GET方法
        return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100)