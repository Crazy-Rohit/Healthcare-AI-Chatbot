from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from datetime import datetime
import os
from flask_cors import CORS

app = Flask(__name__, template_folder='temp')
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDn1IBkPUC7Ux0jvjfBfGTLh0XiTb9sAqg"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')

# Store chat history
chat_histories = {}


def create_medical_context():
    return (
        "You are Swaasth AI, a medical assistant chatbot. Your role is to:"
        "1. Provide general health information and guidance"
        "2. Help users understand medical terms and conditions"
        "3. Suggest when to seek professional medical help"
        "4. Never provide definitive medical diagnoses"
        "5. Always encourage users to consult healthcare professionals for specific medical advice"
        "6. Maintain user privacy and confidentiality"
    )


@app.route('/')
def home():
    return render_template('chatbot.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        user_id = data.get('user_id', 'default_user')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Initialize chat history for new users
        if user_id not in chat_histories:
            chat_histories[user_id] = []
            chat_histories[user_id].append({
                'role': 'system',
                'content': create_medical_context()
            })

        # Generate response from Gemini
        response = model.generate_content(user_message)
        raw_response = response.text

        # Format response to structured output
        formatted_response = format_response(raw_response)

        # Prepare response data
        response_data = {
            'message': formatted_response,
            'timestamp': datetime.now().isoformat(),
            'bot_name': 'Swaasth AI',
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging purpose
        return jsonify({'error': str(e)}), 500


def format_response(text):
    """
    Formats the response text into a structured format with paragraphs and bullet points.
    """
    lines = text.split("\n")
    formatted_text = "<p>"  # Start with a paragraph

    for line in lines:
        line = line.strip()
        if not line:
            formatted_text += "</p><p>"  # Separate paragraphs
        elif line.startswith("-") or line.startswith("*"):
            formatted_text += f"<li>{line[1:].strip()}</li>"
        else:
            formatted_text += f"{line} "

    formatted_text += "</p>"  # End paragraph
    return formatted_text.replace("<p></p>", "")  # Remove empty paragraphs


if __name__ == '__main__':
    app.run(debug=True, port=5000)
