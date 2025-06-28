from flask import Flask, request, jsonify
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/chatgpt", methods=["POST"])
def chatgpt_proxy():
    data = request.get_json()
    user_input = data.get("question", "")

    if not user_input:
        return jsonify({ "reply": "Sorry, I didn’t catch that." }), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{ "role": "user", "content": user_input }],
            max_tokens=150
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({ "reply": answer })
    except Exception as e:
        return jsonify({ "reply": "There was an error processing your request." }), 500
