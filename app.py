from flask import Flask, request, jsonify
import openai
import os
import traceback

# Uncomment for local dev with a .env file:
# from dotenv import load_dotenv
# load_dotenv()

# Ensure your OpenAI key is set in Render env vars or your local .env
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "up": True,
        "openai_key_set": bool(openai.api_key)
    })

@app.route("/", methods=["POST"])
def alexa_handler():
    data = request.get_json(force=True)

    try:
        question = data["request"]["intent"]["slots"]["question"]["value"]
    except Exception:
        question = None

    if not question:
        speak = "Sorry, I didn't catch your question. Please try again."
    else:
        print("📨 Received question:", question)
        try:
            # New v1+ call
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": question}],
                max_tokens=150
            )
            answer = resp.choices[0].message.content.strip()
            print("✅ ChatGPT response received")
            speak = answer
        except Exception as e:
            traceback.print_exc()
            print("❌ ChatGPT call failed:", repr(e))
            speak = "There was an error talking to ChatGPT. Please try again later."

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
