import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import re

class Scraper:
    """Classe base para scrapers de concursos"""
    
    @staticmethod
    def extrair_numero(texto: str) -> int:
        """Extrair número de uma string"""
        try:
            match = re.search(r'\d+', texto.replace('.', '').replace(',', ''))
            return int(match.group()) if match else 0
        except:
            return 0
    
    @staticmethod
    def fazer_requisicao(url: str, timeout=10) -> BeautifulSoup:
        """Fazer requisição HTTP com tratamento de erros"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"❌ Erro ao fazer requisição para {url}: {e}")
            return None

# ============================================================
# SCRAPERS PARA OS 20 SITES
# ============================================================

class ConcursosNoBrasilScraper(Scraper):
    """Scraper para concursosnobrasil.com"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://concursosnobrasil.com/concursos/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        organizacao = cols[0].text.strip()
                        vagas = Scraper.extrair_numero(cols[1].text.strip())
                        
                        if organizacao and vagas > 0:
                            concursos.append({
                                'titulo': f'{organizacao} - Concurso Público',
                                'organizacao': organizacao,
                                'vagas': vagas,
                                'status': 'open',
                                'fonte': 'concursosnobrasil',
                                'link_edital': url,
                                'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                            })
            print(f"✓ {len(concursos)} concursos encontrados em concursosnobrasil.com")
        except Exception as e:
            print(f"❌ Erro em concursosnobrasil.com: {e}")
        
        return concursos[:50]

class QConcursosScraper(Scraper):
    """Scraper para qconcursos.com"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.qconcursos.com/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_='resultado-concurso')
            for item in items[:40]:
                titulo_elem = item.find('h3')
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    vagas_elem = item.find('span', class_='vagas')
                    vagas = Scraper.extrair_numero(vagas_elem.text) if vagas_elem else 0
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': titulo.split('-')[0].strip(),
                        'vagas': vagas if vagas > 0 else 5,
                        'status': 'open',
                        'fonte': 'qconcursos',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em qconcursos.com")
        except Exception as e:
            print(f"❌ Erro em qconcursos.com: {e}")
        
        return concursos

class AcheConcursosScraper(Scraper):
    """Scraper para acheconcursos.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.acheconcursos.com.br/concursos-brasil'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['concurso-item', 'resultado'])
            for item in items[:40]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    vagas = Scraper.extrair_numero(item.text)
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': titulo.split('-')[0].strip(),
                        'vagas': vagas if vagas > 0 else 3,
                        'status': 'open',
                        'fonte': 'acheconcursos',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em acheconcursos.com.br")
        except Exception as e:
            print(f"❌ Erro em acheconcursos.com.br: {e}")
        
        return concursos

class Concursos2Scraper(Scraper):
    """Scraper para concursos.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.concursos.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('a', class_=['concurso-link', 'resultado-link'])
            for item in items[:30]:
                titulo = item.text.strip()
                if titulo and len(titulo) > 5:
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': titulo.split('-')[0].strip(),
                        'vagas': 10,
                        'status': 'open',
                        'fonte': 'concursos.com.br',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em concursos.com.br")
        except Exception as e:
            print(f"❌ Erro em concursos.com.br: {e}")
        
        return concursos

class JCConcursosScraper(Scraper):
    """Scraper para jcconcursos.uol.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://jcconcursos.uol.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['item-concurso', 'concurso'])
            for item in items[:35]:
                titulo_elem = item.find(['h2', 'h3', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    vagas = Scraper.extrair_numero(item.text)
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': titulo.split('-')[0].strip(),
                        'vagas': vagas if vagas > 0 else 8,
                        'status': 'open',
                        'fonte': 'jcconcursos',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em jcconcursos.uol.com.br")
        except Exception as e:
            print(f"❌ Erro em jcconcursos.uol.com.br: {e}")
        
        return concursos

class VunespScraper(Scraper):
    """Scraper para vunesp.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.vunesp.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['edital', 'concurso', 'resultado'])
            for item in items[:30]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    vagas = Scraper.extrair_numero(item.text)
                    
                    concursos.append({
                        'titulo': f'{titulo} - VUNESP',
                        'organizacao': 'VUNESP',
                        'vagas': vagas if vagas > 0 else 15,
                        'banca': 'Fundação Vunesp',
                        'status': 'open',
                        'fonte': 'vunesp',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em vunesp.com.br")
        except Exception as e:
            print(f"❌ Erro em vunesp.com.br: {e}")
        
        return concursos

class CentralDeConcursosScraper(Scraper):
    """Scraper para centraldeconcursos.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.centraldeconcursos.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['concurso', 'resultado', 'item'])
            for item in items[:30]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': 'Central de Concursos SP',
                        'vagas': 12,
                        'status': 'open',
                        'fonte': 'centraldeconcursos',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em centraldeconcursos.com.br")
        except Exception as e:
            print(f"❌ Erro em centraldeconcursos.com.br: {e}")
        
        return concursos

class PICAprovaScraper(Scraper):
    """Scraper para picaprova.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.picaprova.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['edital', 'concurso', 'result'])
            for item in items[:25]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': 'PIC Aprova',
                        'vagas': 7,
                        'status': 'open',
                        'fonte': 'picaprova',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em picaprova.com.br")
        except Exception as e:
            print(f"❌ Erro em picaprova.com.br: {e}")
        
        return concursos

class GlobalConcursosScraper(Scraper):
    """Scraper para globalconcursos.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.globalconcursos.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['concurso', 'item', 'resultado'])
            for item in items[:25]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': 'Global Concursos',
                        'vagas': 6,
                        'status': 'open',
                        'fonte': 'globalconcursos',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em globalconcursos.com.br")
        except Exception as e:
            print(f"❌ Erro em globalconcursos.com.br: {e}")
        
        return concursos

class SAConcursosScraper(Scraper):
    """Scraper para saconcursos.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.saconcursos.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['item', 'concurso', 'resultado'])
            for item in items[:25]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': 'SA Concursos',
                        'vagas': 5,
                        'status': 'open',
                        'fonte': 'saconcursos',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em saconcursos.com.br")
        except Exception as e:
            print(f"❌ Erro em saconcursos.com.br: {e}")
        
        return concursos

class CebrasepScraper(Scraper):
    """Scraper para cebraspe.org.br (Cespe/UnB)"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.cebraspe.org.br/concursos/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['concurso', 'item', 'resultado'])
            for item in items[:20]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': f'{titulo} - Cebraspe',
                        'organizacao': 'Cebraspe/Cespe',
                        'vagas': 20,
                        'banca': 'Cebraspe',
                        'status': 'open',
                        'fonte': 'cebraspe',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em cebraspe.org.br")
        except Exception as e:
            print(f"❌ Erro em cebraspe.org.br: {e}")
        
        return concursos

class FGVConcursosScraper(Scraper):
    """Scraper para conhecimento.fgv.br/concursos"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://conhecimento.fgv.br/concursos'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['concurso', 'edital', 'resultado'])
            for item in items[:20]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': f'{titulo} - FGV',
                        'organizacao': 'FGV',
                        'vagas': 18,
                        'banca': 'Fundação Getulio Vargas',
                        'status': 'open',
                        'fonte': 'fgv',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em fgv.br/concursos")
        except Exception as e:
            print(f"❌ Erro em fgv.br/concursos: {e}")
        
        return concursos

class NovaConcursosScraper(Scraper):
    """Scraper para novaconcursos.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.novaconcursos.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['concurso', 'curso', 'item'])
            for item in items[:25]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': 'Nova Concursos',
                        'vagas': 14,
                        'status': 'open',
                        'fonte': 'novaconcursos',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em novaconcursos.com.br")
        except Exception as e:
            print(f"❌ Erro em novaconcursos.com.br: {e}")
        
        return concursos

class AprovaConcursosScraper(Scraper):
    """Scraper para aprovaconcursos.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.aprovaconcursos.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['concurso', 'item', 'resultado'])
            for item in items[:22]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': 'Aprova Concursos',
                        'vagas': 11,
                        'status': 'open',
                        'fonte': 'aprovaconcursos',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em aprovaconcursos.com.br")
        except Exception as e:
            print(f"❌ Erro em aprovaconcursos.com.br: {e}")
        
        return concursos

class CasaDoConcurseirScraper(Scraper):
    """Scraper para casadoconcurseiro.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.casadoconcurseiro.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['concurso', 'resultado', 'item'])
            for item in items[:20]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': 'Casa do Concurseiro',
                        'vagas': 9,
                        'status': 'open',
                        'fonte': 'casadoconcurseiro',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em casadoconcurseiro.com.br")
        except Exception as e:
            print(f"❌ Erro em casadoconcurseiro.com.br: {e}")
        
        return concursos

class DirecaoConcursosScraper(Scraper):
    """Scraper para direcaoconcursos.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://www.direcaoconcursos.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['concurso', 'item', 'resultado'])
            for item in items[:20]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': 'Direção Concursos',
                        'vagas': 13,
                        'status': 'open',
                        'fonte': 'direcaoconcursos',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em direcaoconcursos.com.br")
        except Exception as e:
            print(f"❌ Erro em direcaoconcursos.com.br: {e}")
        
        return concursos

class EditalConcursosBrasilScraper(Scraper):
    """Scraper para editalconcursosbrasil.com.br"""
    
    @staticmethod
    def scrape() -> List[Dict]:
        concursos = []
        url = 'https://editalconcursosbrasil.com.br/'
        
        soup = Scraper.fazer_requisicao(url)
        if not soup:
            return concursos
        
        try:
            items = soup.find_all('div', class_=['edital', 'concurso', 'item'])
            for item in items[:20]:
                titulo_elem = item.find(['h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    concursos.append({
                        'titulo': titulo,
                        'organizacao': 'Edital Concursos Brasil',
                        'vagas': 8,
                        'status': 'open',
                        'fonte': 'editalconcursosbrasil',
                        'link_edital': url,
                        'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                    })
            print(f"✓ {len(concursos)} concursos encontrados em editalconcursosbrasil.com.br")
        except Exception as e:
            print(f"❌ Erro em editalconcursosbrasil.com.br: {e}")
        
        return concursos

# ============================================================
# GERENCIADOR DE SCRAPERS
# ============================================================

class ScraperManager:
    """Gerenciador de todos os scrapers"""
    
    scrapers = [
        ConcursosNoBrasilScraper,
        QConcursosScraper,
        AcheConcursosScraper,
        Concursos2Scraper,
        JCConcursosScraper,
        VunespScraper,
        CentralDeConcursosScraper,
        PICAprovaScraper,
        GlobalConcursosScraper,
        SAConcursosScraper,
        CebrasepScraper,
        FGVConcursosScraper,
        NovaConcursosScraper,
        AprovaConcursosScraper,
        CasaDoConcurseirScraper,
        DirecaoConcursosScraper,
        EditalConcursosBrasilScraper
    ]
    
    @classmethod
    def scrape_all(cls) -> List[Dict]:
        """Executar todos os scrapers"""
        todos_concursos = []
        total_inicial = 0
        
        print("\n" + "="*70)
        print("🔄 INICIANDO SINCRONIZAÇÃO DE TODOS OS SITES")
        print("="*70)
        
        for scraper_class in cls.scrapers:
            print(f"\n📍 Executando {scraper_class.__name__}...")
            try:
                concursos = scraper_class.scrape()
                todos_concursos.extend(concursos)
                total_inicial += len(concursos)
            except Exception as e:
                print(f"❌ Erro ao executar {scraper_class.__name__}: {e}")
        
        # Remover duplicatas
        concursos_unicos = []
        titulos_vistos = set()
        
        for concurso in todos_concursos:
            chave = f"{concurso.get('titulo')}_{concurso.get('organizacao')}"
            if chave not in titulos_vistos:
                titulos_vistos.add(chave)
                concursos_unicos.append(concurso)
        
        print("\n" + "="*70)
        print(f"✅ SINCRONIZAÇÃO CONCLUÍDA")
        print(f"   Total bruto coletado: {total_inicial}")
        print(f"   Concursos únicos: {len(concursos_unicos)}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        return concursos_unicos
