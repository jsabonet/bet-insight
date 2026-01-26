"""
Script para coletar dados históricos de 5000+ partidas finalizadas
Extrai features completas + resultado real para treino de ML
"""
import os
import sys
import django
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
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


class HistoricalDataCollector:
    """Coleta dados históricos para treino de ML"""
    
    # Top ligas europeias (dados mais confiáveis)
    LEAGUES = {
        39: "Premier League",      # Inglaterra
        140: "La Liga",            # Espanha
        135: "Serie A",            # Itália
        78: "Bundesliga",          # Alemanha
        61: "Ligue 1",             # França
        94: "Primeira Liga",       # Portugal
        88: "Eredivisie",          # Holanda
        203: "Super Lig",          # Turquia
        144: "Jupiler Pro League", # Bélgica
        2: "Champions League"      # UCL (dados premium)
    }
    
    # Temporadas disponíveis (últimas 5 temporadas completas + atual)
    SEASONS = [2020, 2021, 2022, 2023, 2024]
    
    def __init__(self):
        self.api = APIFootballService()
        self.enricher = MatchDataEnricher()
        self.engineer = FeatureEngineer()
        self.collected = []
        self.errors = []
        
    def collect_all(self, target_matches=5000, output_file='training_dataset.json'):
        """
        Coleta dados históricos de múltiplas ligas/temporadas
        
        Args:
            target_matches: Número alvo de partidas (default: 5000)
            output_file: Arquivo de saída JSON
        """
        logger.info("="*80)
        logger.info("🚀 INICIANDO COLETA DE DADOS HISTÓRICOS PARA ML")
        logger.info("="*80)
        logger.info(f"📊 Target: {target_matches} partidas")
        logger.info(f"🏆 Ligas: {len(self.LEAGUES)}")
        logger.info(f"📅 Temporadas: {self.SEASONS}")
        logger.info(f"⚙️ Estratégia: Coletar de todas as ligas até atingir target")
        logger.info("="*80)
        
        total_collected = 0
        
        for league_id, league_name in self.LEAGUES.items():
            logger.info(f"\n{'='*80}")
            logger.info(f"🏆 LIGA: {league_name} (ID: {league_id})")
            logger.info(f"{'='*80}")
            
            league_collected = 0
            
            for season in self.SEASONS:
                if total_collected >= target_matches:
                    logger.info(f"✅ Target atingido ({total_collected} partidas)")
                    break
                
                logger.info(f"\n📅 Temporada {season}/{season+1}")
                
                try:
                    # Buscar fixtures finalizadas
                    fixtures = self._fetch_finished_fixtures(league_id, season)
                    
                    if not fixtures:
                        logger.warning(f"⚠️ Nenhuma fixture encontrada")
                        continue
                    
                    logger.info(f"📋 {len(fixtures)} partidas finalizadas encontradas")
                    
                    # Processar cada partida
                    for i, fixture in enumerate(fixtures):
                        if total_collected >= target_matches:
                            logger.info(f"✅ Target global atingido!")
                            break
                        
                        try:
                            match_data = self._process_fixture(fixture, league_id, season)
                            
                            if match_data:
                                self.collected.append(match_data)
                                league_collected += 1
                                total_collected += 1
                                
                                if total_collected % 100 == 0:
                                    logger.info(f"✅ Progresso: {total_collected}/{target_matches} partidas coletadas ({total_collected/target_matches*100:.1f}%)")
                                    # Salvar checkpoint
                                    self._save_checkpoint(output_file)
                        
                        except Exception as e:
                            logger.error(f"❌ Erro ao processar fixture {fixture.get('id')}: {e}")
                            self.errors.append({
                                'fixture_id': fixture.get('id'),
                                'error': str(e),
                                'league': league_name,
                                'season': season
                            })
                        
                        # Rate limiting (API-Football: 300 req/dia free tier)
                        time.sleep(0.5)
                
                except Exception as e:
                    logger.error(f"❌ Erro ao processar temporada {season}: {e}")
                    continue
            
            logger.info(f"✅ {league_name}: {league_collected} partidas coletadas")
        
        # Salvar dataset final
        self._save_dataset(output_file)
        
        logger.info("\n" + "="*80)
        logger.info("✅ COLETA FINALIZADA")
        logger.info("="*80)
        logger.info(f"📊 Total coletado: {total_collected} partidas")
        logger.info(f"❌ Erros: {len(self.errors)}")
        logger.info(f"💾 Dataset salvo em: {output_file}")
        logger.info("="*80)
        
        return self.collected
    
    def _fetch_finished_fixtures(self, league_id, season):
        """Busca fixtures finalizadas de uma liga/temporada"""
        try:
            # Buscar todas as fixtures da temporada (sem filtro status)
            fixtures = self.api._make_request('fixtures', {
                'league': league_id,
                'season': season
            }, cache_type='fixtures')
            
            if not fixtures:
                return []
            
            # Filtrar localmente por status FT (Full Time) e resultado válido
            valid_fixtures = []
            for fixture in fixtures:
                # Checar status
                status = fixture.get('fixture', {}).get('status', {}).get('short', '')
                if status not in ['FT', 'AET', 'PEN']:  # Full Time, After Extra Time, Penalties
                    continue
                
                # Checar resultado válido
                home_goals = fixture.get('goals', {}).get('home')
                away_goals = fixture.get('goals', {}).get('away')
                
                if home_goals is not None and away_goals is not None:
                    valid_fixtures.append(fixture)
            
            return valid_fixtures
        
        except Exception as e:
            logger.error(f"Erro ao buscar fixtures: {e}")
            return []
    
    def _process_fixture(self, fixture, league_id, season):
        """
        Processa uma fixture: enriquece dados + extrai features + label
        
        Returns:
            dict: {
                'fixture_id': int,
                'league': str,
                'season': int,
                'teams': {...},
                'features': {...},  # TODAS as features engineered
                'label': int,       # 0=Casa, 1=Empate, 2=Fora
                'result': {...}     # Resultado real (gols, etc.)
            }
        """
        fixture_id = fixture['fixture']['id']
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']
        
        logger.debug(f"🔄 Processando: {home_team} vs {away_team} (Fixture {fixture_id})")
        
        try:
            # 1. Enriquecer dados (API-Football)
            match_data = {'api_id': fixture_id}
            enriched = self.enricher.enrich(match_data)
            
            # 2. Feature Engineering (TODAS as features)
            features = self.engineer.engineer_all_features(enriched)
            
            # 3. Flatten features (converter nested dict em flat dict)
            flat_features = self._flatten_features(features)
            
            # 4. Extrair label (resultado real)
            home_goals = fixture['goals']['home']
            away_goals = fixture['goals']['away']
            
            if home_goals > away_goals:
                label = 0  # Casa venceu
                result_text = "home"
            elif home_goals < away_goals:
                label = 2  # Fora venceu
                result_text = "away"
            else:
                label = 1  # Empate
                result_text = "draw"
            
            # 5. Montar dataset entry
            return {
                'fixture_id': fixture_id,
                'league': self.LEAGUES.get(league_id, str(league_id)),
                'league_id': league_id,
                'season': season,
                'date': fixture['fixture']['date'],
                'teams': {
                    'home': home_team,
                    'away': away_team
                },
                'features': flat_features,
                'label': label,
                'label_text': result_text,
                'result': {
                    'home_goals': home_goals,
                    'away_goals': away_goals,
                    'total_goals': home_goals + away_goals
                }
            }
        
        except Exception as e:
            logger.error(f"Erro ao processar fixture {fixture_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _flatten_features(self, features):
        """
        Converte nested dict de features em flat dict
        
        Exemplo:
            {'strength': {'home_attack': 2.1, 'away_attack': 1.8}}
            → {'strength.home_attack': 2.1, 'strength.away_attack': 1.8}
        """
        flat = {}
        
        for category, values in features.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    # Converter booleanos para int (0/1)
                    if isinstance(value, bool):
                        value = int(value)
                    
                    # Ignorar valores None ou não numéricos complexos
                    if value is None:
                        value = 0
                    
                    flat[f"{category}.{key}"] = value
            else:
                flat[category] = values
        
        return flat
    
    def _save_checkpoint(self, output_file):
        """Salva checkpoint intermediário"""
        checkpoint_file = output_file.replace('.json', '_checkpoint.json')
        self._save_dataset(checkpoint_file)
    
    def _save_dataset(self, output_file):
        """Salva dataset em JSON"""
        output_path = Path(__file__).parent / output_file
        
        dataset = {
            'metadata': {
                'collected_at': datetime.now().isoformat(),
                'total_matches': len(self.collected),
                'total_errors': len(self.errors),
                'leagues': list(self.LEAGUES.values()),
                'seasons': self.SEASONS
            },
            'data': self.collected,
            'errors': self.errors
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Dataset salvo: {output_path}")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Coletar dados históricos para ML')
    parser.add_argument('--target', type=int, default=5000,
                       help='Número alvo de partidas (default: 5000)')
    parser.add_argument('--output', type=str, default='training_dataset.json',
                       help='Arquivo de saída (default: training_dataset.json)')
    parser.add_argument('--test', action='store_true',
                       help='Modo teste (coleta apenas 50 partidas)')
    
    args = parser.parse_args()
    
    # Modo teste
    if args.test:
        logger.info("🧪 MODO TESTE - Coletando apenas 50 partidas")
        args.target = 50
        args.output = 'training_dataset_test.json'
    
    # Coletar dados
    collector = HistoricalDataCollector()
    dataset = collector.collect_all(
        target_matches=args.target,
        output_file=args.output
    )
    
    logger.info(f"\n✅ Coleta finalizada! {len(dataset)} partidas coletadas.")


if __name__ == '__main__':
    main()
