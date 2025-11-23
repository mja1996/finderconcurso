# Concursos Brasil Finder - Sistema Completo com Dados Reais

## 📋 Estrutura do Projeto

```
concursos-brasil-finder/
├── app.py                 # API Flask principal
├── database.py            # Gerenciador de banco de dados SQLite
├── scrapers.py            # Scrapers para múltiplos sites
├── requirements.txt       # Dependências Python
├── README.md              # Este arquivo
└── concursos.db          # Banco de dados (criado automaticamente)
```

## 🚀 Instalação e Execução

### 1. Pré-requisitos
- Python 3.8+
- pip

### 2. Instalação das Dependências

```bash
# Clonar ou descarregar o projeto
cd concursos-brasil-finder

# Criar ambiente virtual (opcional, mas recomendado)
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Executar o Backend

```bash
python app.py
```

A API estará disponível em: `http://localhost:5000`

## 📊 Endpoints da API

### Verificar Status
```
GET /api/health
```

### Obter Concursos
```
GET /api/concursos?estado=SP&status=open&fonte=qconcursos&busca=professor
```

### Obter Estatísticas
```
GET /api/estatisticas
```

### Busca Avançada
```
GET /api/busca?termo=engenheiro&estado=RJ&status=open
```

### Forçar Atualização Manual
```
POST /api/atualizar
```

## 🔄 Atualização Automática em Tempo Real

O sistema atualiza automaticamente a cada 6 horas, buscando dados de:

- Concursos No Brasil
- QConcursos
- Ache Concursos
- Concursos.com.br
- E mais...

## 💾 Banco de Dados

Dados armazenados para cada concurso:
- Título
- Organização
- Estado
- Escolaridade
- Número de vagas
- Salário
- Banca examinadora
- Status (aberto/previsto/encerrado)
- Data de publicação
- Link para candidatura
- Descrição

## 🛠️ Personalizações

### Adicionar Novo Scraper

1. Adicione em `scrapers.py`:

```python
class NovoScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://exemplo.com/concursos'
        soup = Scraper.fazer_requisicao(url)
        # ... lógica de extração
        return concursos
```

2. Registre em `ScraperManager`:

```python
scrapers = [
    ConcursosNoBrasilScraper,
    QConcursosScraper,
    NovoScraper  # Adicionar aqui
]
```

### Alterar Frequência de Atualização

Em `app.py`, procure:

```python
scheduler.add_job(
    func=atualizar_concursos,
    trigger="interval",
    hours=6,  # Alterar este valor (em horas)
    ...
)
```

## 📱 Frontend (Integração)

O frontend conecta via:

```javascript
// Exemplo com fetch
fetch('http://localhost:5000/api/concursos?estado=SP&status=open')
  .then(res => res.json())
  .then(data => {
    console.log('Concursos:', data.concursos);
    console.log('Total:', data.total);
  });
```

## 🔒 Segurança

- Validação de entrada em todos os endpoints
- Rate limiting (implementar conforme necessário)
- CORS habilitado para desenvolvimento

## 📝 Logs

O sistema gera logs de:
- Scrapers em execução
- Concursos encontrados
- Erros de conexão
- Atualizações bem-sucedidas

## 🐛 Solução de Problemas

### Erro de conexão com sites
- Verificar conexão de internet
- Sites podem estar em manutenção
- Aguardar próxima atualização automática

### Banco de dados bloqueado
- Fechar a aplicação
- Deletar `concursos.db`
- Reiniciar

### Dependências não encontradas
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📈 Performance

- Cache de dados em SQLite
- Paginação de resultados (1000 máximo)
- Busca indexada por campo
- Atualização assíncrona

## 🔄 Próximas Melhorias

- [ ] Integração com webhooks para notificações
- [ ] Sistema de favoritos
- [ ] Alertas por email
- [ ] Dashboard com gráficos
- [ ] API GraphQL
- [ ] Cache Redis
- [ ] Autenticação de usuários

## 📞 Suporte

Para problemas, dúvidas ou sugestões, verifique:
1. Status da conexão
2. Versão do Python
3. Dependências instaladas

---

**Desenvolvido com ❤️ para ajudar na busca de concursos públicos no Brasil**
