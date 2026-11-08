
from securerelease import create_app
from flask import jsonify

app = create_app()

APP_VERSION = "1.0.0"


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to SecureRelease",
        "application": "SecureRelease DevSecOps Platform",
        "version": APP_VERSION
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    }), 200


@app.route("/version")
def version():
    return jsonify({
        "version": APP_VERSION
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
