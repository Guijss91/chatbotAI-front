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
    chat_id = data.get('chatId')  # pegar o chatId enviado

    if not question:
        return jsonify({'error': 'No question provided'}), 400
    if not chat_id:
        return jsonify({'error': 'No chatId provided'}), 400

    print(f"Tentando conectar em: {N8N_ENDPOINT} com chatId: {chat_id}")

    try:
        # Enviar question + chatId para n8n
        post_data = {'question': question, 'chatId': chat_id}
        response = requests.post(N8N_ENDPOINT, json=post_data, timeout=180)
        response.raise_for_status()
        n8n_data = response.json()

        print(f"Resposta recebida do n8n: {n8n_data}")

        answer = None
        if isinstance(n8n_data, list):
            if len(n8n_data) > 0 and isinstance(n8n_data[0], dict) and 'output' in n8n_data[0]:
                answer = n8n_data[0]['output']
        elif isinstance(n8n_data, dict) and 'output' in n8n_data:
            answer = n8n_data['output']

        if answer is None:
            answer = f'Resposta inesperada do servidor: {n8n_data}'

        return jsonify({'answer': answer})

    except requests.exceptions.Timeout:
        error_msg = 'Timeout: O servidor demorou mais de 180 segundos para responder'
        print(error_msg)
        return jsonify({'error': error_msg}), 504

    except requests.exceptions.ConnectionError as e:
        error_msg = f'Erro de conexão: Não foi possível conectar ao servidor. {str(e)}'
        print(error_msg)
        return jsonify({'error': error_msg}), 503

    except requests.exceptions.HTTPError as e:
        error_msg = f'Erro HTTP {response.status_code}: {response.text}'
        print(error_msg)
        return jsonify({'error': error_msg}), response.status_code

    except requests.exceptions.RequestException as e:
        error_msg = f'Erro de requisição: {str(e)}'
        print(error_msg)
        return jsonify({'error': error_msg}), 500

    except Exception as e:
        error_msg = f'Erro geral: {str(e)}'
        print(f"Erro inesperado: {error_msg}")
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    print(f"Chatbot iniciado. Endpoint configurado: {N8N_ENDPOINT}")
    app.run(host='0.0.0.0', port=5000, debug=True)
