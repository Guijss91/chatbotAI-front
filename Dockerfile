FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Remover endpoint padrão - usar variável de ambiente
# ENV N8N_ENDPOINT=http://host.docker.internal:5678/webhook/chatbot

CMD ["python", "app.py"]
