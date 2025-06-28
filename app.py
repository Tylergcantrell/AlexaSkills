from flask import Flask, request, jsonify
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Catch-all Alexa endpoint
@app.route("/", methods=["POST"])
def alexa_handler():
    data = request.get_json(force=True)

    # 1) Extract the question slot from Alexa's payload
    try:
        question = data["request"]["intent"]["slots"]["question"]["value"]
    except Exception:
        question = None

    if not question:
        speak = "Sorry, I didn't catch your question. Please try again."
    else:
        # 2) Send it to ChatGPT
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}],
                max_tokens=150
            )
            answer = resp.choices[0].message.content.strip()
            speak = answer
        except Exception:
            speak = "There was an error talking to ChatGPT. Please try again later."

    # 3) Build and return a valid Alexa response
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": speak
            },
            "shouldEndSession": True
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Render expects either PORT=10000 or PORT=8080 depending on your service
    app.run(host="0.0.0.0", port=port)
