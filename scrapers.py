import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import re
import warnings
warnings.filterwarnings('ignore')

class Scraper:
    """Classe base para scrapers de concursos"""

    @staticmethod
    def limpar_titulo(titulo: str) -> str:
        """Remove espaços extras e caracteres desnecessários"""
        return re.sub(r'\s+', ' ', titulo).strip()

    @staticmethod
    def contem_palavra_ou_variacao(texto: str, palavras: List[str]) -> bool:
        """Busca palavra ou variações (plural, diminutivo, conjugações)"""
        texto_lower = texto.lower()
        for palavra in palavras:
            if f' {palavra} ' in f' {texto_lower} ':
                return True
            if texto_lower.startswith(palavra + ' '):
                return True
            if texto_lower.endswith(f' {palavra}'):
                return True
            variações = [
                palavra,
                palavra + 's', palavra + 'a', palavra + 'as',
                palavra + 'o', palavra + 'os', palavra + 'ão', palavra + 'ões',
                palavra + 'inho', palavra + 'inhos', palavra + 'inha', palavra + 'inhas',
                palavra + 'ado', palavra + 'ados', palavra + 'ação', palavra + 'ações',
                palavra + 'mente',
            ]
            for var in variações:
                if var in texto_lower:
                    return True
        return False

    @staticmethod
    def eh_numero_telefone(texto: str) -> bool:
        """Verifica se o texto é um número de telefone"""
        patterns = [
            r'^\(?\d{2}\)?[\s-]?\d{4,5}[\s-]?\d{4}$',
            r'^\d{2}\s\d{4,5}\s\d{4}$',
            r'^\(\d{2}\)\s?\d{4}-\d{4}$',
            r'^\+55\s\d{2}\s\d{4,5}-?\d{4}$',
        ]
        for pattern in patterns:
            if re.search(pattern, texto.strip()):
                return True
        return False

    @staticmethod
    def tem_preco(texto: str) -> bool:
        """Verifica se contém preço"""
        patterns = [r'r\$\s*[\d.,]+', r'por\s*r\$', r'/mês', r'/ano', r'^\d+,?\d{2}$']
        texto_lower = texto.lower()
        for pattern in patterns:
            if re.search(pattern, texto_lower):
                return True
        return False

    @staticmethod
    def eh_titulo_valido(titulo: str) -> bool:
        """Verifica se o título é um concurso público válido"""
        if not titulo or len(titulo) < 10:
            return False
        if re.match(r'^\d', titulo):
            return False
        if Scraper.eh_numero_telefone(titulo):
            return False
        if Scraper.tem_preco(titulo):
            return False

        texto_lower = titulo.lower()
        
        palavras_invalidas = [
            'assinatura', 'completa', 'pacote', 'combo', 'plano',
            'aula', 'curso', 'conteúdo', 'material', 'apostila', 'live',
            'webinar', 'videoaula', 'tutorial', 'treinamento', 'capacitação',
            'professor', 'instrutor', 'mentor', 'coach', 'palestrante',
            'resultado', 'gabarito', 'prova', 'resposta', 'correção',
            'sorteio', 'promoção', 'desconto', 'cupom', 'oferta',
            'valor', 'custa', 'pague', 'pagamento', 'cartão',
            'clique', 'saiba', 'confira', 'veja', 'baixe',
            'whatsapp', 'telegram', 'instagram', 'facebook', 'twitter',
            'inscrição', 'inscreva', 'aprenda', 'domine',
            'prepare-se', 'prepare', 'estude', 'estudo', 'aprova'
        ]

        if Scraper.contem_palavra_ou_variacao(titulo, palavras_invalidas):
            return False

        palavras_concurso = [
            'concurso', 'edital', 'seleção', 'processo', 'vaga', 'cargo',
            'analista', 'técnico', 'assistente', 'agente', 'auditor',
            'inspetor', 'perito', 'fiscal', 'advogado', 'juiz',
            'médico', 'enfermeiro', 'engenheiro', 'arquiteto',
            'prefeitura', 'câmara', 'tribunal', 'ministério', 'secretaria',
            'governo', 'estado', 'município', 'federal', 'público',
            'instituição', 'autarquia', 'fundação', 'empresa pública',
            'abertura', 'abertas', 'aberto',
        ]

        if not Scraper.contem_palavra_ou_variacao(titulo, palavras_concurso):
            return False

        if not any(pattern in texto_lower for pattern in [' - ', ' de ', ' para ', 'edital', 'concurso', 'vaga', 'cargo']):
            if len(titulo.split()) < 3:
                return False

        return True

    @staticmethod
    def extrair_numero(texto: str) -> int:
        """Extrair número de vagas de uma string"""
        try:
            match = re.search(r'(\d+)\s*(?:vaga|posto|lugar|selecionado|aprovado)', texto, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                if 1 <= num <= 10000:
                    return num
            match = re.search(r'\d+', texto.replace('.', '').replace(',', ''))
            if match:
                num = int(match.group())
                if num > 10000 or num < 1:
                    return 0
                return num
        except:
            pass
        return 1

    @staticmethod
    def extrair_estado(texto: str) -> str:
        """Extrair estado (UF)"""
        estados_br = {'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                      'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                      'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'}
        patterns = [r'\(([A-Z]{2})\)', r'-\s*([A-Z]{2})\s*$', r'-\s*([A-Z]{2})\s*-', r'([A-Z]{2})\s*-']
        for pattern in patterns:
            match = re.search(pattern, texto)
            if match:
                uf = match.group(1).upper()
                if uf in estados_br:
                    return uf
        return ''

    @staticmethod
    def fazer_requisicao(url: str, timeout=10) -> BeautifulSoup:
        """Fazer requisição HTTP com tratamento de erros"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            }
            response = requests.get(url, headers=headers, timeout=timeout, verify=False)
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            return None

    @staticmethod
    def extrair_concursos_generico(soup: BeautifulSoup, fonte: str, url: str, max_items=100) -> List[Dict]:
        """Extrai concursos de forma genérica, procurando por padrões comuns"""
        concursos = []
        if not soup:
            return concursos
        
        try:
            # Procura por texto contendo números seguido de "vaga(s)"
            links = soup.find_all('a', limit=max_items)
            
            for link in links:
                texto = Scraper.limpar_titulo(link.get_text())
                
                if not texto or len(texto) < 10:
                    continue
                
                # Verifica se é um concurso válido
                if Scraper.eh_titulo_valido(texto):
                    vagas = Scraper.extrair_numero(link.parent.get_text() if link.parent else texto)
                    if vagas > 0:
                        estado = Scraper.extrair_estado(texto)
                        concursos.append({
                            'titulo': texto,
                            'organizacao': texto.split('-')[0].strip()[:50],
                            'vagas': vagas,
                            'estado': estado,
                            'status': 'open',
                            'fonte': fonte,
                            'link_edital': url,
                            'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                        })
            
            # Se não encontrou por links, procura em todos os textos
            if len(concursos) == 0:
                textos = soup.find_all(string=True)
                for i, texto_raw in enumerate(textos[:500]):
                    texto = Scraper.limpar_titulo(texto_raw)
                    if len(texto) > 10 and Scraper.eh_titulo_valido(texto):
                        # Procura vagas na próxima linha ou contexto
                        contexto = ' '.join([t.get_text() for t in textos[max(0, i-2):min(len(textos), i+3)]])
                        vagas = Scraper.extrair_numero(contexto)
                        if vagas > 0:
                            estado = Scraper.extrair_estado(texto)
                            concursos.append({
                                'titulo': texto,
                                'organizacao': texto.split('-')[0].strip()[:50],
                                'vagas': vagas,
                                'estado': estado,
                                'status': 'open',
                                'fonte': fonte,
                                'link_edital': url,
                                'data_publicacao': datetime.now().strftime('%Y-%m-%d')
                            })
        except:
            pass
        
        return concursos[:max_items]

# ============================================================
# SCRAPERS - VERSÃO ROBUSTA COM FALLBACK GENÉRICO
# ============================================================

class ConcursosNoBrasilScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://concursosnobrasil.com/concursos/'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'concursosnobrasil', url, 100)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class QConcursosScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://www.qconcursos.com/'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'qconcursos', url, 100)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class AcheConcursosScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://www.acheconcursos.com.br/'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'acheconcursos', url, 80)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class CebrasepScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://www.cebraspe.org.br/concursos/'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'cebraspe', url, 60)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class VunespScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://www.vunesp.com.br/'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'vunesp', url, 60)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class FGVScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://conhecimento.fgv.br/concursos'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'fgv', url, 50)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class IbfcConcursosScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://www.ibfc.org.br/concursos/'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'ibfc', url, 50)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class GlobalConcursosScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://www.globalconcursos.com.br/'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'globalconcursos', url, 80)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class JCConcursosScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://jcconcursos.uol.com.br/'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'jcconcursos', url, 80)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class KoncursosScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://www.konkursos.com.br/'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'konkursos', url, 80)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class PciConcursosScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://www.pciconcursos.com.br/'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'pciconcursos', url, 80)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

class ConcursosScraper(Scraper):
    @staticmethod
    def scrape() -> List[Dict]:
        url = 'https://www.concursos.com.br/abertos'
        soup = Scraper.fazer_requisicao(url)
        concursos = Scraper.extrair_concursos_generico(soup, 'concursos.com.br', url, 80)
        print(f"  ✓ {len(concursos)} concursos")
        return concursos

# ============================================================
# MANAGER DE SCRAPERS
# ============================================================

class ScraperManager:
    """Gerenciador de scrapers de concursos públicos"""

    scrapers = [
        ConcursosNoBrasilScraper,
        QConcursosScraper,
        AcheConcursosScraper,
        CebrasepScraper,
        VunespScraper,
        FGVScraper,
        IbfcConcursosScraper,
        GlobalConcursosScraper,
        JCConcursosScraper,
        KoncursosScraper,
        PciConcursosScraper,
        ConcursosScraper,
    ]

    @classmethod
    def scrape_all(cls) -> List[Dict]:
        """Executar todos os scrapers"""
        todos_concursos = []
        print("\n" + "="*70)
        print("🔄 SINCRONIZAÇÃO DE CONCURSOS PÚBLICOS ABERTOS")
        print("="*70)
        print(f"📊 Total de fontes: {len(cls.scrapers)} sites")
        print("="*70)

        for scraper_class in cls.scrapers:
            print(f"\n📍 {scraper_class.__name__}...")
            try:
                concursos = scraper_class.scrape()
                todos_concursos.extend(concursos)
            except Exception as e:
                print(f"  ❌ Erro: {str(e)[:40]}")

        # Remover duplicatas
        concursos_unicos = []
        titulos_vistos = set()
        for concurso in todos_concursos:
            chave = f"{concurso.get('titulo')}_{concurso.get('fonte')}"
            if chave not in titulos_vistos:
                titulos_vistos.add(chave)
                concursos_unicos.append(concurso)

        print("\n" + "="*70)
        print(f"✅ SINCRONIZAÇÃO CONCLUÍDA")
        print(f"  📊 Total: {len(concursos_unicos)} concursos únicos")
        print(f"  🌐 Fontes ativas: {len(cls.scrapers)} agregadores")
        print(f"  🗓️  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

        return concursos_unicos
