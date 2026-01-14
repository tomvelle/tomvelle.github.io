from flask import Flask, jsonify, render_template, request
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lyrics")
def get_lyrics():
    with open("lyrics.json", "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route("/mark_sung", methods=["POST"])
def mark_sung():
    idx = request.json["index"]
    with open("lyrics.json", "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[idx]["sung"] = True
        f.seek(0)
        json.dump(data, f, indent=2)
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=True)
