"""
Script para coletar dados históricos de COPAS (eliminatórias)
Target: ~800 partidas de copas para retreino do modelo ML

COPAS PRINCIPAIS:
- FA Cup (Inglaterra)
- Copa del Rey (Espanha) 
- DFB-Pokal (Alemanha)
- Coppa Italia (Itália)
- Coupe de France (França)
- KNVB Beker (Holanda)
- Croky Cup (Bélgica)
- Taça de Portugal (Portugal)
"""
import os
import sys
import django
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CupDataCollector:
    """Coleta dados históricos de competições de COPA"""
    
    # IDs das principais copas (API-Football)
    CUP_COMPETITIONS = {
        # Inglaterra
        45: "FA Cup",
        46: "League Cup (EFL Cup)",
        48: "Community Shield",
        
        # Espanha
        143: "Copa del Rey",
        556: "Supercopa de España",
        
        # Alemanha
        81: "DFB-Pokal",
        529: "DFL-Supercup",
        
        # Itália
        137: "Coppa Italia",
        547: "Supercoppa Italiana",
        
        # França
        66: "Coupe de France",
        526: "Trophée des Champions",
        
        # Holanda
        94: "KNVB Beker",
        
        # Bélgica
        147: "Croky Cup (Belgian Cup)",
        
        # Portugal
        96: "Taça de Portugal",
        97: "Taça da Liga",
        
        # Internacional
        2: "Champions League",  # Fases eliminatórias
        3: "Europa League",     # Fases eliminatórias
        848: "Conference League", # Fases eliminatórias
    }
    
    # Temporadas (últimas 3-4 temporadas para ter dados recentes)
    SEASONS = [2021, 2022, 2023, 2024, 2025]
    
    def __init__(self):
        self.api = APIFootballService()
        self.enricher = MatchDataEnricher()
        self.engineer = FeatureEngineer()
        self.collected = []
        self.errors = []
        
    def collect_cup_matches(self, target_matches=800, output_file='cup_training_dataset.json'):
        """
        Coleta partidas de copas para retreino
        
        Args:
            target_matches: Número alvo de partidas (default: 800)
            output_file: Arquivo de saída JSON
        """
        logger.info("="*80)
        logger.info("🏆 COLETANDO DADOS HISTÓRICOS DE COPAS PARA RETREINO ML")
        logger.info("="*80)
        logger.info(f"📊 Target: {target_matches} partidas de copas")
        logger.info(f"🏆 Competições: {len(self.CUP_COMPETITIONS)}")
        logger.info(f"📅 Temporadas: {self.SEASONS}")
        logger.info("="*80)
        
        total_collected = 0
        
        for cup_id, cup_name in self.CUP_COMPETITIONS.items():
            logger.info(f"\n{'='*80}")
            logger.info(f"🏆 {cup_name} (ID: {cup_id})")
            logger.info(f"{'='*80}")
            
            cup_collected = 0
            
            for season in self.SEASONS:
                if total_collected >= target_matches:
                    logger.info(f"✅ Target atingido ({total_collected} partidas)")
                    break
                
                logger.info(f"\n📅 Temporada {season}/{season+1}")
                
                try:
                    # Buscar fixtures finalizadas
                    fixtures = self._fetch_cup_fixtures(cup_id, season)
                    
                    if not fixtures:
                        logger.warning(f"⚠️ Nenhuma partida encontrada")
                        continue
                    
                    logger.info(f"📋 {len(fixtures)} partidas encontradas")
                    
                    # Processar cada partida
                    for fixture in fixtures:
                        if total_collected >= target_matches:
                            break
                        
                        try:
                            match_data = self._process_cup_fixture(fixture, cup_id, cup_name, season)
                            
                            if match_data:
                                self.collected.append(match_data)
                                cup_collected += 1
                                total_collected += 1
                                
                                if total_collected % 50 == 0:
                                    logger.info(f"✅ Progresso: {total_collected}/{target_matches} ({total_collected/target_matches*100:.1f}%)")
                                    # Salvar checkpoint
                                    self._save_checkpoint(output_file)
                        
                        except Exception as e:
                            logger.error(f"❌ Erro ao processar fixture {fixture.get('fixture', {}).get('id')}: {e}")
                            self.errors.append({
                                'fixture_id': fixture.get('fixture', {}).get('id'),
                                'error': str(e),
                                'competition': cup_name,
                                'season': season
                            })
                        
                        # Rate limiting (300 req/dia free, ~0.3s por request = seguro)
                        time.sleep(0.5)
                
                except Exception as e:
                    logger.error(f"❌ Erro na temporada {season}: {e}")
                    continue
            
            logger.info(f"✅ {cup_name}: {cup_collected} partidas coletadas")
        
        # Salvar dataset final
        self._save_dataset(output_file)
        
        logger.info("\n" + "="*80)
        logger.info("✅ COLETA FINALIZADA")
        logger.info("="*80)
        logger.info(f"📊 Total coletado: {total_collected} partidas de copas")
        logger.info(f"❌ Erros: {len(self.errors)}")
        logger.info(f"💾 Dataset salvo em: {output_file}")
        logger.info("="*80)
        
        return self.collected
    
    def _fetch_cup_fixtures(self, league_id, season):
        """Busca fixtures finalizadas de uma copa/temporada"""
        try:
            logger.info(f"   🔍 Buscando fixtures da API...")
            
            # Buscar fixtures da copa
            fixtures_raw = self.api._make_request('fixtures', {
                'league': league_id,
                'season': season
            }, cache_type='fixtures')
            
            if not fixtures_raw:
                return []
            
            # Filtrar por status FT (Full Time) e knockout stages
            valid_fixtures = []
            knockout_rounds = [
                'final', 'semi-final', 'quarter-final', 'round of 16',
                'final', 'semifinal', 'quarterfinal', '8th finals',
                '3rd place final', 'semi-finals', 'quarter-finals',
                'round of 32', 'round of 64'
            ]
            
            for fixture in fixtures_raw:
                # Status finalizado
                status = fixture.get('fixture', {}).get('status', {}).get('short', '')
                if status not in ['FT', 'AET', 'PEN']:
                    continue
                
                # Resultado válido
                home_goals = fixture.get('goals', {}).get('home')
                away_goals = fixture.get('goals', {}).get('away')
                if home_goals is None or away_goals is None:
                    continue
                
                # OPCIONAL: Priorizar fases eliminatórias (semi, final, etc.)
                round_name = fixture.get('league', {}).get('round', '').lower()
                is_knockout = any(kr in round_name for kr in knockout_rounds)
                
                # Aceitar TODAS as partidas de copa (inclusive fases de grupos)
                # Mas marcar se é knockout para análise
                fixture['is_knockout'] = is_knockout
                valid_fixtures.append(fixture)
            
            logger.info(f"   ✅ {len(valid_fixtures)} partidas válidas (knockout: {sum(1 for f in valid_fixtures if f.get('is_knockout'))})")
            return valid_fixtures
        
        except Exception as e:
            logger.error(f"   ❌ Erro ao buscar fixtures: {e}")
            return []
    
    def _process_cup_fixture(self, fixture, cup_id, cup_name, season):
        """
        Processa uma partida de copa: enriquece + extrai features + label
        
        Returns:
            dict: {
                'fixture_id': int,
                'competition': str,
                'competition_type': 'cup',
                'is_knockout': bool,
                'season': int,
                'features': {...},
                'label': int,  # 0=Casa, 1=Empate, 2=Fora
                'result': {...}
            }
        """
        fixture_id = fixture['fixture']['id']
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']
        home_goals = fixture['goals']['home']
        away_goals = fixture['goals']['away']
        round_name = fixture.get('league', {}).get('round', 'Unknown')
        is_knockout = fixture.get('is_knockout', False)
        
        logger.info(f"   🔧 Processando: {home_team} vs {away_team} ({round_name})")
        
        # Determinar label (resultado)
        if home_goals > away_goals:
            label = 0  # Casa venceu
        elif away_goals > home_goals:
            label = 2  # Fora venceu
        else:
            label = 1  # Empate (tempo normal)
        
        try:
            # Enriquecer dados
            match_data = {'api_id': fixture_id}
            enriched = self.enricher.enrich(match_data)
            
            # Extrair features
            features = self.engineer.engineer_all_features(enriched)
            
            # Flatten features para ML
            flat_features = {}
            for category, feature_dict in features.items():
                if isinstance(feature_dict, dict):
                    for key, value in feature_dict.items():
                        flat_features[f"{category}.{key}"] = value
            
            return {
                'fixture_id': fixture_id,
                'competition': cup_name,
                'competition_id': cup_id,
                'competition_type': 'cup',
                'is_knockout': is_knockout,
                'round': round_name,
                'season': season,
                'teams': {
                    'home': home_team,
                    'away': away_team
                },
                'features': flat_features,
                'label': label,
                'result': {
                    'home_goals': home_goals,
                    'away_goals': away_goals,
                    'total_goals': home_goals + away_goals,
                    'winner': 'home' if label == 0 else ('away' if label == 2 else 'draw')
                }
            }
        
        except Exception as e:
            logger.error(f"   ❌ Erro ao processar fixture {fixture_id}: {e}")
            raise
    
    def _save_checkpoint(self, output_file):
        """Salva checkpoint durante coleta"""
        output_path = Path(__file__).parent / 'ml_training' / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'total_matches': len(self.collected),
                    'competitions': list(set(m['competition'] for m in self.collected)),
                    'seasons': list(set(m['season'] for m in self.collected)),
                    'collected_at': datetime.now().isoformat(),
                    'checkpoint': True
                },
                'matches': self.collected
            }, f, indent=2, ensure_ascii=False)
    
    def _save_dataset(self, output_file):
        """Salva dataset final"""
        output_path = Path(__file__).parent / 'ml_training' / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        # Estatísticas
        knockout_count = sum(1 for m in self.collected if m.get('is_knockout'))
        competitions = {}
        for match in self.collected:
            comp = match['competition']
            competitions[comp] = competitions.get(comp, 0) + 1
        
        metadata = {
            'total_matches': len(self.collected),
            'knockout_matches': knockout_count,
            'group_stage_matches': len(self.collected) - knockout_count,
            'competitions': competitions,
            'seasons': list(set(m['season'] for m in self.collected)),
            'label_distribution': {
                'home_wins': sum(1 for m in self.collected if m['label'] == 0),
                'draws': sum(1 for m in self.collected if m['label'] == 1),
                'away_wins': sum(1 for m in self.collected if m['label'] == 2)
            },
            'collected_at': datetime.now().isoformat(),
            'errors': len(self.errors)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': metadata,
                'matches': self.collected,
                'errors': self.errors
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📊 ESTATÍSTICAS DO DATASET:")
        logger.info(f"   Total: {metadata['total_matches']} partidas")
        logger.info(f"   Knockout: {metadata['knockout_matches']} ({metadata['knockout_matches']/max(metadata['total_matches'],1)*100:.1f}%)")
        logger.info(f"   Group Stage: {metadata['group_stage_matches']} ({metadata['group_stage_matches']/max(metadata['total_matches'],1)*100:.1f}%)")
        logger.info(f"\n   Distribuição de Resultados:")
        logger.info(f"      Casa: {metadata['label_distribution']['home_wins']} ({metadata['label_distribution']['home_wins']/max(metadata['total_matches'],1)*100:.1f}%)")
        logger.info(f"      Empate: {metadata['label_distribution']['draws']} ({metadata['label_distribution']['draws']/max(metadata['total_matches'],1)*100:.1f}%)")
        logger.info(f"      Fora: {metadata['label_distribution']['away_wins']} ({metadata['label_distribution']['away_wins']/max(metadata['total_matches'],1)*100:.1f}%)")
        logger.info(f"\n   Competições:")
        for comp, count in sorted(competitions.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"      {comp}: {count}")


if __name__ == '__main__':
    collector = CupDataCollector()
    
    # Coletar ~800 partidas de copas
    collector.collect_cup_matches(
        target_matches=800,
        output_file='cup_training_dataset.json'
    )
    
    logger.info("\n🎉 COLETA CONCLUÍDA!")
    logger.info("📁 Próximo passo: Executar retrain_with_cups.py para retreinar modelo")
