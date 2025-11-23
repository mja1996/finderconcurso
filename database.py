import sqlite3
import json
from datetime import datetime
from typing import List, Dict

class Database:
    def __init__(self, db_path='concursos.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Inicializar banco de dados com tabelas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de concursos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                organizacao TEXT NOT NULL,
                estado TEXT,
                escolaridade TEXT,
                vagas INTEGER,
                salario TEXT,
                banca TEXT,
                fonte TEXT,
                status TEXT,
                data_publicacao DATE,
                link_edital TEXT,
                descricao TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(titulo, organizacao, fonte)
            )
        ''')
        
        # Tabela de log de atualizações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS atualizacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fonte TEXT,
                total_concursos INTEGER,
                novos INTEGER,
                atualizados INTEGER,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def inserir_concurso(self, concurso: Dict) -> bool:
        """Inserir ou atualizar concurso"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO concursos 
                (titulo, organizacao, estado, escolaridade, vagas, salario, 
                 banca, fonte, status, data_publicacao, link_edital, descricao, data_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                concurso.get('titulo'),
                concurso.get('organizacao'),
                concurso.get('estado'),
                concurso.get('escolaridade'),
                concurso.get('vagas', 0),
                concurso.get('salario'),
                concurso.get('banca'),
                concurso.get('fonte'),
                concurso.get('status', 'open'),
                concurso.get('data_publicacao'),
                concurso.get('link_edital'),
                concurso.get('descricao')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao inserir concurso: {e}")
            return False
    
    def obter_concursos(self, filtros: Dict = None) -> List[Dict]:
        """Obter concursos com filtros opcionais"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM concursos WHERE 1=1"
        params = []
        
        if filtros:
            if filtros.get('estado'):
                query += " AND estado = ?"
                params.append(filtros['estado'])
            
            if filtros.get('status'):
                query += " AND status = ?"
                params.append(filtros['status'])
            
            if filtros.get('fonte'):
                query += " AND fonte = ?"
                params.append(filtros['fonte'])
            
            if filtros.get('busca'):
                query += " AND (titulo LIKE ? OR organizacao LIKE ? OR descricao LIKE ?)"
                termo = f"%{filtros['busca']}%"
                params.extend([termo, termo, termo])
        
        query += " ORDER BY data_publicacao DESC LIMIT 1000"
        
        cursor.execute(query, params)
        concursos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return concursos
    
    def contar_concursos(self) -> int:
        """Contar total de concursos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM concursos")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def limpar_concursos(self):
        """Limpar banco antes de atualizar"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM concursos")
        conn.commit()
        conn.close()
    
    def registrar_atualizacao(self, fonte: str, total: int, novos: int, atualizados: int):
        """Registrar log de atualização"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO atualizacoes (fonte, total_concursos, novos, atualizados)
            VALUES (?, ?, ?, ?)
        ''', (fonte, total, novos, atualizados))
        conn.commit()
        conn.close()
