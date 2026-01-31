"""
Popula o campo stats_cache das partidas finalizadas
Chama a API UMA VEZ e salva os dados no banco
Depois, o treinamento ML usa só o banco sem chamar API
"""

import os
import sys
import django
import logging
from datetime import datetime
from time import sleep

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.api_football_service import APIFootballService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class StatsCachePopulator:
    """Popula stats_cache das partidas finalizadas"""
    
    def __init__(self):
        self.api = APIFootballService()
        self.stats_populated = 0
        self.stats_failed = 0
    
    def populate_match(self, match):
        """Popula stats_cache de uma partida"""
        try:
            stats_cache = {}
            
            # 1. Standings (tabela da liga)
            if match.league and match.league.api_football_id:
                try:
                    # Extrair season da data da partida
                    # Ligas europeias: Ago-Mai (ex: 2024/25 = season 2024)
                    # Se partida é Jan-Jun, temporada começou no ano anterior
                    season = match.match_date.year
                    if match.match_date.month <= 6:  # Jan-Jun = temporada anterior
                        season -= 1
                    
                    standings_data = self.api.fetch_standings(
                        league_id=match.league.api_football_id,
                        season=season
                    )
                    
                    if standings_data:
                        # Encontrar posições dos times
                        home_standing = None
                        away_standing = None
                        
                        for team_data in standings_data:
                            # team_data pode ser dict ou lista, verificar tipo
                            if isinstance(team_data, dict):
                                team_id = team_data.get('team', {}).get('id')
                                if team_id == match.home_team.api_football_id:
                                    home_standing = team_data
                                elif team_id == match.away_team.api_football_id:
                                    away_standing = team_data
                        
                        stats_cache['standings'] = {
                            'home': home_standing,
                            'away': away_standing
                        }
                        
                        # Log seguro
                        home_rank = home_standing.get('rank', 'N/A') if isinstance(home_standing, dict) else 'N/A'
                        away_rank = away_standing.get('rank', 'N/A') if isinstance(away_standing, dict) else 'N/A'
                        logger.info(f"      ✅ Standings: Casa {home_rank}º, Fora {away_rank}º")
                    
                    sleep(0.5)  # Rate limiting
                
                except Exception as e:
                    logger.warning(f"      ⚠️ Erro ao buscar standings: {e}")
            
            # 2. Team Statistics (médias de gols)
            try:
                season = match.match_date.year
                if match.match_date.month < 7:
                    season -= 1
                
                # Home team stats
                home_stats = self.api.fetch_team_statistics(
                    team_id=match.home_team.api_football_id,
                    league_id=match.league.api_football_id,
                    season=season
                )
                
                if home_stats:
                    stats_cache['home_stats'] = {
                        'goals_avg': home_stats.get('goals', {}).get('for', {}).get('average', {}).get('total', 1.5),
                        'goals_against_avg': home_stats.get('goals', {}).get('against', {}).get('average', {}).get('total', 1.5)
                    }
                    logger.info(f"      ✅ Home Stats: {stats_cache['home_stats']['goals_avg']} gols/jogo")
                
                sleep(0.5)
                
                # Away team stats
                away_stats = self.api.fetch_team_statistics(
                    team_id=match.away_team.api_football_id,
                    league_id=match.league.api_football_id,
                    season=season
                )
                
                if away_stats:
                    stats_cache['away_stats'] = {
                        'goals_avg': away_stats.get('goals', {}).get('for', {}).get('average', {}).get('total', 1.5),
                        'goals_against_avg': away_stats.get('goals', {}).get('against', {}).get('average', {}).get('total', 1.5)
                    }
                    logger.info(f"      ✅ Away Stats: {stats_cache['away_stats']['goals_avg']} gols/jogo")
                
                sleep(0.5)
                
            except Exception as e:
                logger.warning(f"      ⚠️ Erro ao buscar team stats: {e}")
            
            # 3. H2H (histórico de confrontos)
            try:
                h2h_data = self.api.fetch_h2h(
                    team1_id=match.home_team.api_football_id,
                    team2_id=match.away_team.api_football_id,
                    last=10
                )
                
                if h2h_data:
                    # Calcular estatísticas H2H
                    home_wins = 0
                    draws = 0
                    away_wins = 0
                    
                    for h2h_match in h2h_data:
                        teams = h2h_match.get('teams', {})
                        home_id = teams.get('home', {}).get('id')
                        home_score = h2h_match.get('goals', {}).get('home')
                        away_score = h2h_match.get('goals', {}).get('away')
                        
                        if home_score is not None and away_score is not None:
                            # Verificar quem ganhou (do ponto de vista do nosso time casa)
                            if home_id == match.home_team.api_football_id:
                                if home_score > away_score:
                                    home_wins += 1
                                elif away_score > home_score:
                                    away_wins += 1
                                else:
                                    draws += 1
                            else:
                                # Jogo invertido
                                if away_score > home_score:
                                    home_wins += 1
                                elif home_score > away_score:
                                    away_wins += 1
                                else:
                                    draws += 1
                    
                    stats_cache['h2h'] = {
                        'home_wins': home_wins,
                        'draws': draws,
                        'away_wins': away_wins,
                        'total': len(h2h_data)
                    }
                    logger.info(f"      ✅ H2H: {home_wins}V-{draws}E-{away_wins}D em {len(h2h_data)} jogos")
                
                sleep(0.5)
                
            except Exception as e:
                logger.warning(f"      ⚠️ Erro ao buscar H2H: {e}")
            
            # 4. Odds (se disponível - muitas partidas antigas não têm)
            try:
                odds_data = self.api.fetch_odds(fixture_id=match.api_football_id)
                
                if odds_data:
                    stats_cache['odds'] = odds_data
                    logger.info(f"      ✅ Odds: {odds_data.get('home', 'N/A')}-{odds_data.get('draw', 'N/A')}-{odds_data.get('away', 'N/A')}")
                
                sleep(0.5)
                
            except Exception as e:
                logger.warning(f"      ⚠️ Erro ao buscar odds: {e}")
            
            # Salvar no banco
            if stats_cache:
                from django.utils import timezone
                match.stats_cache = stats_cache
                match.last_stats_update = timezone.now()
                match.save(update_fields=['stats_cache', 'last_stats_update'])
                self.stats_populated += 1
                logger.info(f"      💾 Stats cache salvo ({len(stats_cache)} campos)")
                return True
            else:
                self.stats_failed += 1
                logger.warning(f"      ⚠️ Nenhum dado coletado")
                return False
        
        except Exception as e:
            logger.error(f"      ❌ Erro geral: {e}")
            self.stats_failed += 1
            return False
    
    def populate_all(self, limit=None, skip_existing=True):
        """Popula stats_cache de todas as partidas finalizadas"""
        logger.info("="*80)
        logger.info("🚀 POPULANDO STATS_CACHE DAS PARTIDAS FINALIZADAS")
        logger.info("="*80)
        
        # Buscar partidas finalizadas
        query = Match.objects.filter(
            status='finished',
            home_score__isnull=False,
            away_score__isnull=False,
            api_football_id__isnull=False
        ).select_related('league', 'home_team', 'away_team')
        
        if skip_existing:
            query = query.filter(stats_cache__isnull=True)
            logger.info("📋 Buscando partidas SEM stats_cache")
        
        query = query.order_by('-match_date')
        
        if limit:
            query = query[:limit]
        
        matches = list(query)
        total = len(matches)
        
        logger.info(f"📊 Total de partidas para popular: {total}")
        
        if total == 0:
            logger.info("✅ Todas as partidas já têm stats_cache!")
            return
        
        logger.info("="*80)
        
        for i, match in enumerate(matches, 1):
            logger.info(f"\n[{i}/{total}] {match.home_team.name} vs {match.away_team.name}")
            logger.info(f"   📅 {match.match_date.strftime('%Y-%m-%d')} - {match.league.name}")
            logger.info(f"   🆔 Fixture ID: {match.api_football_id}")
            
            success = self.populate_match(match)
            
            if i % 10 == 0:
                logger.info(f"\n📊 Progresso: {i}/{total} - ✅ {self.stats_populated} populados, ❌ {self.stats_failed} falhados")
            
            # Rate limiting mais conservador
            sleep(1)
        
        logger.info("\n" + "="*80)
        logger.info("✅ POPULAÇÃO CONCLUÍDA!")
        logger.info(f"📊 Estatísticas:")
        logger.info(f"   ✅ Populados com sucesso: {self.stats_populated}")
        logger.info(f"   ❌ Falhados: {self.stats_failed}")
        logger.info(f"   📊 Taxa de sucesso: {(self.stats_populated/total*100):.1f}%")
        logger.info("="*80)


def main():
    populator = StatsCachePopulator()
    
    # Começar com 100 partidas para testar
    # Depois pode aumentar para todas
    populator.populate_all(limit=100, skip_existing=True)


if __name__ == '__main__':
    main()
