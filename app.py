from flask import Flask, request, jsonify, g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from craw import Craw
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.before_request
def before():
    print(request.path)
    if request.path in ['/login']:
        return
    print(request.path)
    token = request.headers.get("token")
    if token is None:
        return jsonify({'msg': 'token不能为空', 'code': 400})
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except Exception as e:
        print(e)
        return jsonify({'msg': 'token解析失败', 'code': 400})
    g.username = data['username']
    g.craw = cache.get(g.username)
    if g.craw is None:
        return jsonify({'msg': 'token已失效', 'code': 400})


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    craw = Craw(username, password)
    if craw.login():
        cache.set(username, craw, 60 * 10)
        s = Serializer(app.config['SECRET_KEY'], expires_in=60 * 10)
        return s.dumps({'username': username})


@app.route('/exams', methods=['GET'])
def get_exams():
    return jsonify({'data': g.craw.get_exams()})


@app.route('/record', methods=['GET'])
def get_records():
    return jsonify({'data': g.craw.get_records()})


@app.route('/kb', methods=['GET'])
def get_kb():
    return jsonify({'data': g.craw.get_curriculum()})


if __name__ == '__main__':
    app.run()
