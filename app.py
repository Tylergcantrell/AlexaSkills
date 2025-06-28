from flask import Flask, request, jsonify
import openai
import os

# If you’re developing locally with a .env file, uncomment these two lines:
# from dotenv import load_dotenv
# load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Health check to confirm env var is visible
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "up": True,
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY"))
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
        # Call ChatGPT
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}],
                max_tokens=150
            )
            answer = resp.choices[0].message.content.strip()
            speak = answer
        except Exception as e:
            # Log real error for debugging
            print("❌ ChatGPT call failed:", repr(e))
            speak = "There was an error talking to ChatGPT. Please try again later."

    # Build Alexa-compatible response
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
    # Render will provide PORT; default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
