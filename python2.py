import openai
from flask import Flask, request, jsonify
import os
import hashlib
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

cache = {}

def get_code_hash(code: str) -> str:
    """Return a SHA256 hash of the code."""
    return hashlib.sha256(code.encode('utf-8')).hexdigest()

def explain_code(code: str) -> str:
    """Call OpenAI to explain the code, or return from cache if available."""
    code_hash = get_code_hash(code)

    if code_hash in cache:
        print("✅ Using cached response.")
        return cache[code_hash]

    # Not cached: call OpenAI
    prompt = f"Explain the following Python code in detail:\n\n{code}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    explanation = response.choices[0].message.content
    cache[code_hash] = explanation  # Store in cache
    print("💡 Cached new explanation.")
    return explanation

@app.route("/upload", methods=["POST"])
def upload_and_explain():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save and read file content
    code = file.read().decode("utf-8")

    try:
        explanation = explain_code(code)
        return jsonify({
            "original_code": code,
            "explanation": explanation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)