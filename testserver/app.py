from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["POST"])
def receive_superhook():
    app.logger.info(request.form)
    return "", 200

if __name__ == "__main__":
    app.run(debug=True, port=8090)
