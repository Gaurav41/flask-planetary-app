from flask import Flask,make_response,request
from functools import wraps

app = Flask(__name__)

def auth_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        auth = request.authorization
        if auth and auth.username=="test" and auth.password=="test":
            return f(*args,**kwargs)
        else:
            return make_response("Could not verify your loggin!",401,{'WWW-Authenticate': 'Basic realm="Login Required"'})
    return decorated


@app.route("/")
def index():
    return "<h1>This is index page, Login in not required<h1>"


@app.route("/home")
@auth_required
def home():
    return "<h1>This is home page, login required here<h1>"


if __name__ == "__main__":
    app.run(debug=True)