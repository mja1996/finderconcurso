from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from database import Database
from scrapers import ScraperManager
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Inicializar banco de dados
db = Database('concursos.db')

# Agendador de tarefas
scheduler = BackgroundScheduler()

def atualizar_concursos():
    """Função para atualizar concursos em tempo real"""
    print(f"\n[{datetime.now()}] Iniciando atualização de concursos...")
    
    try:
        concursos = ScraperManager.scrape_all()
        
        for concurso in concursos:
            db.inserir_concurso(concurso)
        
        print(f"✓ Concursos atualizados: {len(concursos)}")
        
    except Exception as e:
        print(f"✗ Erro na atualização: {e}")

# Configurar job de atualização (a cada 6 horas)
scheduler.add_job(
    func=atualizar_concursos,
    trigger="interval",
    hours=6,
    id="atualizar_concursos",
    name="Atualizar concursos",
    replace_existing=True
)

# ===== SERVIR O FRONTEND HTML =====
@app.route('/')
def index():
    """Servir o arquivo index.html"""
    try:
        return send_file('index.html')
    except Exception as e:
        print(f"Erro ao servir index.html: {e}")
        return jsonify({'erro': 'index.html não encontrado'}), 404

# ===== API ENDPOINTS =====

@app.route('/api/health', methods=['GET'])
def health():
    """Verificar status da API"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'total_concursos': db.contar_concursos()
    })

@app.route('/api/concursos', methods=['GET'])
def obter_concursos():
    """Obter concursos com filtros"""
    filtros = {
        'estado': request.args.get('estado'),
        'status': request.args.get('status'),
        'fonte': request.args.get('fonte'),
        'busca': request.args.get('busca')
    }
    
    # Remover filtros vazios
    filtros = {k: v for k, v in filtros.items() if v}
    
    concursos = db.obter_concursos(filtros)
    
    return jsonify({
        'total': len(concursos),
        'concursos': concursos,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/concursos/<int:concurso_id>', methods=['GET'])
def obter_concurso(concurso_id):
    """Obter detalhes de um concurso específico"""
    concursos = db.obter_concursos()
    
    concurso = None
    for c in concursos:
        if c['id'] == concurso_id:
            concurso = c
            break
    
    if not concurso:
        return jsonify({'erro': 'Concurso não encontrado'}), 404
    
    return jsonify(concurso)

@app.route('/api/estatisticas', methods=['GET'])
def obter_estatisticas():
    """Obter estatísticas gerais"""
    concursos = db.obter_concursos()
    
    estados = {}
    fontes = {}
    total_vagas = 0
    
    for concurso in concursos:
        estado = concurso.get('estado', 'BR')
        estados[estado] = estados.get(estado, 0) + 1
        
        fonte = concurso.get('fonte', 'unknown')
        fontes[fonte] = fontes.get(fonte, 0) + 1
        
        total_vagas += concurso.get('vagas', 0)
    
    return jsonify({
        'total_concursos': len(concursos),
        'total_vagas': total_vagas,
        'total_estados': len(estados),
        'estados': estados,
        'fontes': fontes,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/busca', methods=['GET'])
def busca_avancada():
    """Busca avançada de concursos"""
    termo = request.args.get('termo', '')
    estado = request.args.get('estado')
    status = request.args.get('status')
    fonte = request.args.get('fonte')
    
    filtros = {'busca': termo}
    if estado:
        filtros['estado'] = estado
    if status:
        filtros['status'] = status
    if fonte:
        filtros['fonte'] = fonte
    
    concursos = db.obter_concursos(filtros)
    
    return jsonify({
        'termo_busca': termo,
        'total_resultados': len(concursos),
        'concursos': concursos,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/atualizar', methods=['POST'])
def atualizar_manual():
    """Forçar atualização de concursos"""
    atualizar_concursos()
    return jsonify({
        'status': 'atualização iniciada',
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def nao_encontrado(e):
    return jsonify({'erro': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def erro_servidor(e):
    return jsonify({'erro': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 CONCURSOS BRASIL FINDER - Backend")
    print("="*60)
    
    print("\n⏳ Iniciando sincronização inicial de concursos...")
    atualizar_concursos()
    
    print("\n⏳ Iniciando scheduler de atualizações automáticas...")
    scheduler.start()
    
    print(f"\n✓ API rodando em http://localhost:5000")
    print(f"✓ Acesse no navegador: http://localhost:5000")
    print(f"✓ Banco de dados: concursos.db")
    print(f"✓ Atualização automática: a cada 6 horas")
    print("\n" + "="*60)
    print("Pressione CTRL+C para parar o servidor")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )
