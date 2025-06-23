from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Pega a chave da API do Asaas da variável de ambiente ou usa placeholder
ASAAS_API_KEY = os.environ.get('ASAAS_API_KEY', 'SUA_API_KEY_AQUI')
ASAAS_API_URL = 'https://www.asaas.com/api/v3'

@app.route('/')
def home():
    return "API Asaas rodando com sucesso!"

@app.route('/cadastrar-vendedor', methods=['POST'])
def cadastrar_vendedor():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    telefone = data.get('telefone')
    plano = data.get('plano')  # 'mensal' ou 'anual'

    if not all([nome, email, telefone, plano]):
        return jsonify({"erro": "Faltando dados obrigatórios"}), 400

    ciclo = 'MONTHLY' if plano == 'mensal' else 'ANNUALLY'
    valor = 45.00 if plano == 'mensal' else 240.00

    # Criar cliente no Asaas
    cliente_response = requests.post(f"{ASAAS_API_URL}/customers", headers={
        "Content-Type": "application/json",
        "access_token": ASAAS_API_KEY
    }, json={
        "name": nome,
        "email": email,
        "phone": telefone
    }).json()

    if 'id' not in cliente_response:
        return jsonify({"erro": "Erro ao criar cliente", "detalhes": cliente_response}), 400

    customer_id = cliente_response['id']

    # Criar assinatura (recorrente)
    assinatura_response = requests.post(f"{ASAAS_API_URL}/subscriptions", headers={
        "Content-Type": "application/json",
        "access_token": ASAAS_API_KEY
    }, json={
        "customer": customer_id,
        "billingType": "UNDEFINED",  # aceita PIX e cartão
        "cycle": ciclo,
        "value": valor,
        "description": f"Assinatura {plano.capitalize()} - Gadaiada"
    }).json()

    return jsonify(assinatura_response)

@app.route('/asaas-webhook', methods=['POST'])
def webhook():
    evento = request.json
    print("Webhook recebido:", evento)

    if evento.get('event') == 'PAYMENT_RECEIVED':
        pagamento = evento.get('payment', {})
        email_cliente = pagamento.get('customer', {}).get('email')

        if email_cliente:
            print(f"Pagamento confirmado para: {email_cliente}")
            ativar_vendedor_no_webkul(email_cliente)

    return '', 200

def ativar_vendedor_no_webkul(email):
    # Aqui você integra com a API do Webkul para ativar o vendedor, por enquanto simulado
    print(f"Vendedor com e-mail {email} foi ativado no sistema (simulado).")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
