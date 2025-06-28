from flask import Flask, request, jsonify
import openai
import os
import traceback

# -- Local development: load .env if present --
# from dotenv import load_dotenv
# load_dotenv()

# -- Ensure your OpenAI key is set in Render env vars or your local .env --
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "up": True,
        "openai_key_set": bool(openai.api_key)
    })

# Main Alexa endpoint
@app.route("/", methods=["POST"])
def alexa_handler():
    data = request.get_json(force=True)

    # Extract the question slot
    try:
        question = data["request"]["intent"]["slots"]["question"]["value"]
    except Exception:
        question = None

    if not question:
        speak = "Sorry, I didn't catch your question. Please try again."
    else:
        try:
            # Call ChatGPT
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}],
                max_tokens=150
            )
            speak = resp.choices[0].message.content.strip()
        except Exception as e:
            # Log full traceback for debugging in Render logs
            traceback.print_exc()
            print("❌ ChatGPT call failed:", repr(e))
            speak = "There was an error talking to ChatGPT. Please try again later."

    # Build Alexa-compatible JSON response
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
    app.run(host="0.0.0.0", port=port)
