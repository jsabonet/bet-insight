"""
Calcula features REAIS das equipes baseado no histórico de partidas
Substitui valores genéricos por estatísticas calculadas
"""
import os
import sys
import django
from collections import defaultdict
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from django.db.models import Avg, Count, Q

class TeamStatsCalculator:
    """Calcula estatísticas reais das equipes"""
    
    def __init__(self):
        self.team_cache = {}
    
    def get_team_stats(self, team_id, before_date, league_id=None, last_n=10):
        """
        Calcula estatísticas do time baseado nas últimas N partidas
        
        Args:
            team_id: ID do time
            before_date: Data limite (não incluir partidas após essa data)
            league_id: ID da liga (opcional - filtrar por liga)
            last_n: Número de partidas a considerar
        """
        cache_key = f"{team_id}_{before_date}_{league_id}_{last_n}"
        if cache_key in self.team_cache:
            return self.team_cache[cache_key]
        
        # Buscar últimas N partidas do time ANTES da data especificada
        matches_query = Match.objects.filter(
            Q(home_team_id=team_id) | Q(away_team_id=team_id),
            match_date__lt=before_date,
            status='finished',
            home_score__isnull=False,
            away_score__isnull=False
        )
        
        if league_id:
            matches_query = matches_query.filter(league_id=league_id)
        
        matches = matches_query.order_by('-match_date')[:last_n]
        
        if not matches:
            # Sem histórico - retornar valores padrão
            stats = {
                'games_played': 0,
                'goals_scored': 0,
                'goals_conceded': 0,
                'goals_per_game': 1.5,
                'conceded_per_game': 1.5,
                'attack_strength': 1.0,
                'defense_strength': 1.0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'points': 0,
                'win_rate': 0.33,
                'clean_sheets': 0,
                'clean_sheet_rate': 0.0,
                'btts_rate': 0.5,
                'avg_total_goals': 3.0,
                'form_points': 0,
                'recent_form': 1.5,
            }
        else:
            # Calcular estatísticas
            total_scored = 0
            total_conceded = 0
            wins = 0
            draws = 0
            losses = 0
            clean_sheets = 0
            btts_count = 0
            total_goals_in_matches = 0
            form_points = 0  # Últimos 5 jogos
            
            for i, match in enumerate(matches):
                is_home = match.home_team_id == team_id
                
                if is_home:
                    scored = match.home_score
                    conceded = match.away_score
                else:
                    scored = match.away_score
                    conceded = match.home_score
                
                total_scored += scored
                total_conceded += conceded
                total_goals_in_matches += (match.home_score + match.away_score)
                
                # Resultado
                if scored > conceded:
                    wins += 1
                    if i < 5:  # Forma recente (últimos 5)
                        form_points += 3
                elif scored == conceded:
                    draws += 1
                    if i < 5:
                        form_points += 1
                else:
                    losses += 1
                
                # Clean sheet
                if conceded == 0:
                    clean_sheets += 1
                
                # BTTS
                if match.home_score > 0 and match.away_score > 0:
                    btts_count += 1
            
            games = len(matches)
            
            stats = {
                'games_played': games,
                'goals_scored': total_scored,
                'goals_conceded': total_conceded,
                'goals_per_game': total_scored / games,
                'conceded_per_game': total_conceded / games,
                'attack_strength': max(0.5, total_scored / games / 1.5),  # Normalizado por 1.5 (média)
                'defense_strength': max(0.5, total_conceded / games / 1.5),
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'points': wins * 3 + draws,
                'win_rate': wins / games,
                'clean_sheets': clean_sheets,
                'clean_sheet_rate': clean_sheets / games,
                'btts_rate': btts_count / games,
                'avg_total_goals': total_goals_in_matches / games,
                'form_points': form_points,
                'recent_form': form_points / 15.0,  # Normalizado (max 15 pontos em 5 jogos)
            }
        
        self.team_cache[cache_key] = stats
        return stats
    
    def get_h2h_stats(self, home_team_id, away_team_id, before_date, max_games=10):
        """Calcula estatísticas de confronto direto"""
        
        h2h_matches = Match.objects.filter(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_date__lt=before_date,
            status='finished',
            home_score__isnull=False,
            away_score__isnull=False
        ).order_by('-match_date')[:max_games]
        
        if not h2h_matches:
            return {
                'games': 0,
                'home_wins': 0,
                'draws': 0,
                'away_wins': 0,
                'home_win_rate': 0.33,
                'avg_goals': 2.5,
                'btts_rate': 0.5,
            }
        
        home_wins = 0
        draws = 0
        away_wins = 0
        total_goals = 0
        btts_count = 0
        
        for match in h2h_matches:
            total_goals += (match.home_score + match.away_score)
            
            if match.home_score > match.away_score:
                home_wins += 1
            elif match.home_score == match.away_score:
                draws += 1
            else:
                away_wins += 1
            
            if match.home_score > 0 and match.away_score > 0:
                btts_count += 1
        
        games = len(h2h_matches)
        
        return {
            'games': games,
            'home_wins': home_wins,
            'draws': draws,
            'away_wins': away_wins,
            'home_win_rate': home_wins / games if games > 0 else 0.33,
            'avg_goals': total_goals / games if games > 0 else 2.5,
            'btts_rate': btts_count / games if games > 0 else 0.5,
        }


def extract_features_from_match(match, calculator):
    """Extrai features REAIS de uma partida usando histórico"""
    
    # Calcular estatísticas dos times
    home_stats = calculator.get_team_stats(
        match.home_team_id,
        match.match_date,
        match.league_id,
        last_n=10
    )
    
    away_stats = calculator.get_team_stats(
        match.away_team_id,
        match.match_date,
        match.league_id,
        last_n=10
    )
    
    # Calcular H2H
    h2h = calculator.get_h2h_stats(
        match.home_team_id,
        match.away_team_id,
        match.match_date,
        max_games=5
    )
    
    # Determinar se é copa
    is_cup = 'cup' in match.league.name.lower() if match.league else False
    
    # Construir features
    features = {
        # STRENGTH - CALCULADO COM BASE REAL
        'strength.home_attack_strength': home_stats['attack_strength'],
        'strength.away_attack_strength': away_stats['attack_strength'],
        'strength.home_defense_strength': home_stats['defense_strength'],
        'strength.away_defense_strength': away_stats['defense_strength'],
        'strength.home_goals_per_game': home_stats['goals_per_game'],
        'strength.away_goals_per_game': away_stats['goals_per_game'],
        'strength.home_conceded_per_game': home_stats['conceded_per_game'],
        'strength.away_conceded_per_game': away_stats['conceded_per_game'],
        'strength.home_advantage_factor': 1.2,
        'strength.strength_differential': home_stats['attack_strength'] - away_stats['attack_strength'],
        
        # FORM - CALCULADO COM BASE REAL
        'form.home_recent_points': home_stats['form_points'],
        'form.away_recent_points': away_stats['form_points'],
        'form.home_momentum': 0,  # TODO: calcular tendência
        'form.away_momentum': 0,
        'form.form_differential': home_stats['recent_form'] - away_stats['recent_form'],
        'form.home_weighted_form': home_stats['recent_form'],
        'form.away_weighted_form': away_stats['recent_form'],
        
        # H2H - CALCULADO COM BASE REAL
        'h2h.h2h_games': h2h['games'],
        'h2h.h2h_home_wins': h2h['home_wins'],
        'h2h.h2h_away_wins': h2h['away_wins'],
        'h2h.h2h_draws': h2h['draws'],
        'h2h.h2h_home_win_rate': h2h['home_win_rate'],
        'h2h.h2h_avg_goals': h2h['avg_goals'],
        'h2h.h2h_btts_rate': h2h['btts_rate'],
        
        # STATISTICS - CALCULADO COM BASE REAL
        'statistics.home_clean_sheet_rate': home_stats['clean_sheet_rate'],
        'statistics.away_clean_sheet_rate': away_stats['clean_sheet_rate'],
        'statistics.home_cards_per_game': 2.0,  # TODO: adicionar se disponível
        'statistics.away_cards_per_game': 2.0,
        
        # COMPETITION
        'competition.is_cup_competition': is_cup,
        'competition.is_knockout_stage': False,
        'competition.knockout_adjustment_factor': 0.9 if is_cup else 1.0,
        
        # MARKET - Probabilidades estimadas (melhorar depois)
        'market.market_home_prob': 0.40 + (home_stats['win_rate'] - away_stats['win_rate']) * 0.2,
        'market.market_draw_prob': 0.30,
        'market.market_away_prob': 0.30 + (away_stats['win_rate'] - home_stats['win_rate']) * 0.2,
        'market.bookmaker_margin': 0.05,
        
        # CONTEXT
        'context.home_rest_days': 7,
        'context.away_rest_days': 7,
        'context.rest_advantage': 0,
        'context.home_is_fatigued': False,
        'context.away_is_fatigued': False,
        'context.fatigue_impact': 0.0,
        
        # ELO - Aproximação baseada em performance
        'elo.home_elo': 1400 + home_stats['win_rate'] * 200,
        'elo.away_elo': 1400 + away_stats['win_rate'] * 200,
        'elo.elo_differential': (home_stats['win_rate'] - away_stats['win_rate']) * 200,
        
        # WEATHER
        'weather.temperature': 20.0,
        'weather.has_rain': False,
        'weather.has_snow': False,
        'weather.has_wind': False,
        'weather.weather_impact': 0.0,
        'weather.goal_impact': 0.0,
        
        # MATCH IMPORTANCE
        'match_importance.home_importance': 5,
        'match_importance.away_importance': 5,
        'match_importance.match_importance': 5.0,
        'match_importance.is_derby': False,
        
        # MOTIVATION
        'motivation.home_motivation': 5.0,
        'motivation.away_motivation': 5.0,
        'motivation.motivation_differential': 0.0,
    }
    
    return features


# Teste rápido
if __name__ == '__main__':
    print("="*80)
    print("TESTE: EXTRAÇÃO DE FEATURES REAIS")
    print("="*80)
    print()
    
    calculator = TeamStatsCalculator()
    
    # Pegar uma partida de exemplo
    test_match = Match.objects.filter(
        status='finished',
        home_score__isnull=False,
        away_score__isnull=False
    ).select_related('home_team', 'away_team', 'league').first()
    
    if test_match:
        print(f"Partida de teste:")
        print(f"  {test_match.home_team.name} vs {test_match.away_team.name}")
        print(f"  Data: {test_match.match_date}")
        print(f"  Liga: {test_match.league.name if test_match.league else 'N/A'}")
        print(f"  Resultado: {test_match.home_score}-{test_match.away_score}")
        print()
        
        features = extract_features_from_match(test_match, calculator)
        
        print("Features extraídas:")
        print("-" * 80)
        
        # Mostrar features agrupadas
        categories = {}
        for key, value in features.items():
            cat = key.split('.')[0]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((key, value))
        
        for cat, items in sorted(categories.items()):
            print(f"\n[{cat.upper()}]")
            for key, value in items[:5]:  # Mostrar primeiros 5
                print(f"  {key:45s} = {value}")
            if len(items) > 5:
                print(f"  ... e mais {len(items) - 5} features")
        
        print()
        print("="*80)
        print("Extração bem-sucedida! ✅")
        print("="*80)
    else:
        print("Nenhuma partida encontrada para teste")
