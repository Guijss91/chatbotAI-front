from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

N8N_ENDPOINT = os.getenv('N8N_ENDPOINT', 'https://laboratorio-n8n.nu7ixt.easypanel.host/webhook/chatbot')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    try:
        response = requests.post(N8N_ENDPOINT, json={'question': question}, timeout=30)
        response.raise_for_status()
        n8n_data = response.json()

        # Debug: mostrar a resposta recebida
        print(f"Resposta recebida do n8n: {n8n_data}")

        # Verificar se é lista ou dict e extrair 'output'
        answer = None
        if isinstance(n8n_data, list):
            if len(n8n_data) > 0 and isinstance(n8n_data[0], dict) and 'output' in n8n_data[0]:
                answer = n8n_data[0]['output']
        elif isinstance(n8n_data, dict) and 'output' in n8n_data:
            answer = n8n_data['output']

        if answer is None:
            answer = f'Resposta inesperada do servidor: {n8n_data}'

        return jsonify({'answer': answer})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Erro de conexão: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
