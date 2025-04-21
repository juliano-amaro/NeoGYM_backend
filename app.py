from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()

FBKEY = json.loads(os.getenv('CONFIG_FIREBASE'))

cred = credentials.Certificate(FBKEY)
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def index():
    return 'API TÁ FUNCIONANDO'

@app.route('/academia', methods=['GET'])
def consulta_lista():
    alunos = []
    lista = db.collection('aluno').stream()
    for item in lista:
        alunos.append(item.to_dict())

    if alunos:
        return jsonify(alunos), 200
    
    else:
        return jsonify({{'mensagem': 'Erro! nenhum aluno registrado!'}}), 400

@app.route('/academia/<id>', methods=['GET'])
def buscar_id(id):  

    doc_ref = db.collection('aluno').document(id)
    doc = doc_ref.get().to_dict()
    
    if doc:
        return jsonify(doc), 200
    
    else:
        return ({'mensagem':'Aluno não encontrado'}), 400

@app.route('/academia/consulta', methods=['POST'])
def busca_cpf():
    
    dados = request.json

    if "cpf" not in dados:
        return jsonify({'mensagem':'Erro! Campo CPF é obrigatório'})

    cpf = dados['cpf']
    
    alunos_ref = db.collection('aluno')
    busca = alunos_ref.where('cpf', '==', cpf).stream()
    
    aluno_encontrado = None
    for doc in busca:
        aluno_encontrado = doc.to_dict()
        break

    if aluno_encontrado:
        return jsonify({'aluno': aluno_encontrado}), 200
    else:
        return jsonify({'mensagem':'Aluno não encontrado'}), 404

@app.route('/academia/consulta/nome', methods=['POST'])
def buscar_nome():
    dados = request.json

    if "nome" not in dados:
        return jsonify({'mensagem': 'Erro! Campo NOME é obrigatório'})
    
    cpf = dados['nome']

    aluno_ref = db.collection('aluno')
    busca = aluno_ref.where('cpf', '==', cpf).stream()

    aluno_encontrado = None
    for doc in busca:
        aluno_encontrado = doc.to_dict()

    if aluno_encontrado:
        return jsonify({'aluno': aluno_encontrado}), 200
    else:
        return jsonify({'mensagem': 'aluno não encontrado!'}), 404

    
@app.route('/academia', methods=['POST'])
def cadastro_aluno():

    dados = request.json

    if 'cpf' not in dados or 'nome' not in dados or 'cpf' not in dados:
        return jsonify({'mensagem': 'Erro! Campos cpf, nome e status são obrigatórios!'}), 400
    
    # Contador
    contador_ref = db.collection('controle_id').document('contador')
    contador_doc = contador_ref.get().to_dict()
    ultimo_id = contador_doc.get('id')
    novo_id = int(ultimo_id) + 1
    contador_ref.update({'id': novo_id})

    db.collection('aluno').document(str(novo_id)).set({
        "id": novo_id,
        "cpf": dados['cpf'],
        "nome": dados['nome'],
        "status": dados['status']
    })

    return jsonify({'mensagem':'Sucesso!! Aluno cadastrado!'}), 201
   
@app.route('/academia/update/aluno/<id>', methods=['PUT'])
def update_aluno(id):
    dados = request.json

    if 'cpf' not in dados or 'nome' not in dados or 'cpf' not in dados:
        return jsonify({'mensagem': 'Erro! Campos cpf, nome e status são obrigatórios!'}), 400

    doc_ref = db.collection('aluno').document(id)
    doc = doc_ref.get()

    if doc.exists:
        doc_ref.update({
            "cpf": dados['cpf'],
            "nome": dados['nome'],
            "status": dados['status']
        })
        return jsonify({'mensagem':'Sucesso! Aluno Editado!'}), 201
    
    else:
        return jsonify({'mensagem':'Erro! Aluno não encontrado!'}), 404
    
@app.route('/academia/delete/aluno/<id>', methods=['DELETE'])
def deletar_aluno(id):
    doc_ref = db.collection('aluno').document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({'mensagem': 'Erro! Aluno não encontrado!'})
    
    doc_ref.delete()
    return jsonify({'mensagem': 'Aluno excluída com sucesso!'}), 200

if __name__ == '__main__':
    app.run()