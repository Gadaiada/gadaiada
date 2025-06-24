from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ASAAS_API_KEY = os.environ.get('ASAAS_API_KEY', '$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmFmMGM3OWYyLWRkYWUtNDk1Yi05MGJmLWQ3NmM0MjNiM2Y1MTo6JGFhY2hfY2E3NWJhNTEtZjAxNS00OTYyLTk4YzQtYmFiNDE3ZTAwZWIz')
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
    plano = data.get('plano')

    if not all([nome, email, telefone, plano]):
        return jsonify({"erro": "Faltando dados obrigatórios"}), 400

    ciclo = 'MONTHLY' if plano == 'mensal' else 'ANNUALLY'
    valor = 45.00 if plano == 'mensal' else 240.00

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

    assinatura_response = requests.post(f"{ASAAS_API_URL}/subscriptions", headers={
        "Content-Type": "application/json",
        "access_token": ASAAS_API_KEY
    }, json={
        "customer": customer_id,
        "billingType": "UNDEFINED",
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
    print(f"Vendedor com e-mail {email} foi ativado no sistema (simulado).")

# Apenas para desenvolvimento local
if __name__ == "__main__":
    app.run(debug=True)
