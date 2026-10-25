from unittest.mock import patch
from datetime import timedelta
from types import SimpleNamespace

from django.core.cache import cache
from django.test import SimpleTestCase
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.test import APIRequestFactory

from .views import HOME_MAX_ODDS_CHECKS, MatchViewSet, _filter_home_matches


class MatchDetailPerformanceTests(SimpleTestCase):
	def setUp(self):
		cache.clear()
		self.factory = APIRequestFactory()

	def tearDown(self):
		cache.clear()

	def test_api_detail_returns_core_without_loading_enrichment(self):
		fixture = {'fixture': {'id': 77}}
		with (
			patch('apps.matches.views._cached_api_result', return_value={'success': True, **fixture}),
			patch.object(MatchViewSet, '_format_api_matches', return_value=[{'id': 77}]),
			patch('apps.matches.views.FootballAPIService') as api_service,
		):
			response = MatchViewSet.as_view(
				{'get': 'api_detail'}, permission_classes=[AllowAny],
			)(
				self.factory.get('/api/matches/api_detail/', {'id': 77})
			)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['match']['id'], 77)
		self.assertTrue(response.data['enrichment_pending'])
		api_service.return_value.get_fixture_events.assert_not_called()
		api_service.return_value.get_head_to_head.assert_not_called()

	def test_live_score_refreshes_and_persists_only_current_fixture_state(self):
		match = SimpleNamespace(
			id=50,
			api_football_id=77,
			home_score=0,
			away_score=0,
			status='scheduled',
			save=lambda **_kwargs: None,
		)
		fixture = {
			'fixture': {'status': {'short': '1H', 'elapsed': 24}},
			'goals': {'home': 1, 'away': 0},
		}
		with (
			patch.object(MatchViewSet, 'get_object', return_value=match),
			patch('apps.matches.views._cached_api_result', return_value={'success': True, 'fixture': fixture}) as cached_result,
			patch('apps.matches.views.FootballAPIService'),
		):
			response = MatchViewSet.as_view(
				{'get': 'live_score'}, permission_classes=[AllowAny],
			)(
				self.factory.get('/api/matches/50/live_score/'),
				pk='50',
			)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['home_score'], 1)
		self.assertEqual(response.data['away_score'], 0)
		self.assertEqual(response.data['status'], '1H')
		self.assertEqual(response.data['elapsed'], 24)
		self.assertEqual(match.status, 'live')
		cached_result.assert_called_once()
		self.assertEqual(cached_result.call_args.args[:2], ('match_live_score:v1:77', 30))

	def test_live_score_rejects_fixtures_without_external_id(self):
		match = SimpleNamespace(api_football_id=None)
		with (
			patch.object(MatchViewSet, 'get_object', return_value=match),
			patch('apps.matches.views._cached_api_result') as cached_result,
		):
			response = MatchViewSet.as_view(
				{'get': 'live_score'}, permission_classes=[AllowAny],
			)(
				self.factory.get('/api/matches/50/live_score/'),
				pk='50',
			)

		self.assertEqual(response.status_code, 404)
		cached_result.assert_not_called()

	def test_history_enrichment_keeps_h2h_and_team_forms_separate(self):
		fixture = {
			'teams': {'home': {'id': 1}, 'away': {'id': 2}},
			'league': {'id': 3, 'season': 2026},
		}
		with (
			patch(
				'apps.matches.views._cached_api_result',
				side_effect=lambda _key, _timeout, fetch: fetch(),
			),
			patch('apps.matches.views.FootballAPIService') as api_service,
		):
			service = api_service.return_value
			service.get_fixture_by_id.return_value = {'success': True, 'fixture': fixture}
			service.get_head_to_head.return_value = {'success': True, 'matches': ['h2h-match']}
			service.get_team_last_matches.side_effect = [
				{'success': True, 'matches': ['home-match']},
				{'success': True, 'matches': ['away-match']},
			]
			response = MatchViewSet.as_view(
				{'get': 'api_detail_enrichment'}, permission_classes=[AllowAny],
			)(
				self.factory.get(
					'/api/matches/api_detail_enrichment/',
					{'id': 77, 'group': 'history'},
				)
			)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['enrichment']['h2h'], ['h2h-match'])
		self.assertEqual(response.data['enrichment']['home_last_matches'], ['home-match'])
		self.assertEqual(response.data['enrichment']['away_last_matches'], ['away-match'])
		self.assertNotIn('matches', response.data['enrichment'])
		self.assertEqual(service.get_team_last_matches.call_args_list[0].kwargs['season'], 2026)

	def test_statistical_preview_returns_cached_fixture_payload(self):
		cached = {'success': True, 'analysis_data': {'cached': True}}
		cache.set('statistical_preview:v2:77:pregame', cached, 60)
		request = self.factory.post(
			'/api/matches/statistical_preview/',
			{
				'home_team': 'Home',
				'away_team': 'Away',
				'api_football_id': 77,
				'match_status': 'scheduled',
			},
			format='json',
		)

		response = MatchViewSet.as_view(
			{'post': 'statistical_preview'}, permission_classes=[AllowAny],
		)(request)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data, cached)

	def test_home_only_returns_future_priority_matches_with_1x2_odds(self):
		future_kickoff = (timezone.now() + timedelta(hours=2)).isoformat()
		past_kickoff = (timezone.now() - timedelta(hours=1)).isoformat()
		fixtures = [
			{'fixture': {'id': 101, 'date': future_kickoff, 'status': {'short': 'NS'}}, 'league': {'id': 39, 'name': 'Premier League', 'country': 'England'}},
			{'fixture': {'id': 102, 'date': future_kickoff, 'status': {'short': 'NS'}}, 'league': {'id': 39, 'name': 'Premier League', 'country': 'England'}},
			{'fixture': {'id': 103, 'date': future_kickoff, 'status': {'short': 'NS'}}, 'league': {'id': 9999, 'name': 'Unknown League', 'country': 'Unknown'}},
			{'fixture': {'id': 104, 'date': past_kickoff, 'status': {'short': 'FT'}}, 'league': {'id': 39, 'name': 'Premier League', 'country': 'England'}},
		]
		odds = {'home_win': 2.1, 'draw': 3.2, 'away_win': 3.4}

		def format_fixtures(items):
			return [
				{
					'id': fixture['fixture']['id'],
					'league': fixture['league'],
					'match_date': fixture['fixture']['date'],
					'status': fixture['fixture']['status']['short'],
				}
				for fixture in items
			]

		with (
			patch('apps.matches.views.FootballAPIService') as football_api,
			patch('apps.analysis.services.api_football_service.APIFootballService.fetch_odds', side_effect=lambda fixture_id: odds if fixture_id == 101 else {}),
			patch.object(MatchViewSet, '_format_api_matches', side_effect=format_fixtures),
		):
			football_api.return_value.get_fixtures_by_date.side_effect = [
				{'success': True, 'fixtures': fixtures},
				{'success': True, 'fixtures': []},
				{'success': True, 'fixtures': []},
			]
			response = MatchViewSet.as_view(
				{'get': 'from_api'}, permission_classes=[AllowAny],
				)(self.factory.get('/api/matches/from_api/', {'date': timezone.localdate().isoformat()}))

		self.assertEqual(response.status_code, 200)
		self.assertEqual([match['id'] for match in response.data['matches']], [101])
		self.assertTrue(response.data['matches'][0]['has_market_odds'])
		self.assertEqual(response.data['matches'][0]['market_odds']['home_win'], 2.1)

	def test_home_search_applies_quality_filter_to_api_results(self):
		eligible = {
			'id': 101,
			'home_team': {'name': 'Costa do Sol'},
			'away_team': {'name': 'Ferroviário'},
			'league': {'id': 39, 'name': 'Premier League', 'country': 'England'},
		}
		with (
			patch('apps.matches.views.FootballAPIService') as football_api,
			patch.object(MatchViewSet, '_format_api_matches', return_value=[]),
			patch('apps.matches.views._filter_home_matches', return_value=[eligible]) as quality_filter,
		):
			football_api.return_value.get_fixtures_by_date.return_value = {'success': True, 'fixtures': [{'fixture': {'id': 101}}]}
			response = MatchViewSet.as_view(
				{'get': 'search'}, permission_classes=[AllowAny],
			)(self.factory.get('/api/matches/search/', {'q': 'Costa do Sol'}))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['matches'], [eligible])
		quality_filter.assert_called_once_with([])

	def test_home_prioritizes_global_leagues_over_mozambique(self):
		kickoff = (timezone.now() + timedelta(hours=2)).isoformat()
		matches = [
			{'id': 201, 'league': {'id': 9991, 'country': 'Mozambique'}, 'status': 'NS', 'match_date': kickoff},
			{'id': 202, 'league': {'id': 39, 'country': 'England'}, 'status': 'NS', 'match_date': kickoff},
		]
		with patch(
			'apps.analysis.services.api_football_service.APIFootballService.fetch_odds',
			return_value={'home_win': 2.1, 'draw': 3.2, 'away_win': 3.4},
		):
			eligible = _filter_home_matches(matches)

		self.assertEqual([match['id'] for match in eligible], [202, 201])
		self.assertEqual(eligible[0]['league_priority'], 1)
		self.assertEqual(eligible[1]['league_priority'], 3)

	def test_home_checks_distinct_competitions_before_repeat_fixtures(self):
		kickoff = (timezone.now() + timedelta(hours=2)).isoformat()
		league_ids = (39, 140, 135, 78, 61, 2, 3, 848, 12, 20, 94, 88, 71, 128, 325)
		matches = [
			{
				'id': 300 + index,
				'league': {'id': league_id, 'name': f'League {league_id}', 'country': 'Country'},
				'status': 'NS',
				'match_date': kickoff,
			}
			for index, league_id in enumerate(league_ids * 10)
		]
		with patch(
			'apps.analysis.services.api_football_service.APIFootballService.fetch_odds',
			return_value={'home_win': 2.1, 'draw': 3.2, 'away_win': 3.4},
		) as fetch_odds:
			eligible = _filter_home_matches(matches)

		self.assertEqual(fetch_odds.call_count, HOME_MAX_ODDS_CHECKS)
		self.assertEqual(len(eligible), HOME_MAX_ODDS_CHECKS)
		self.assertEqual(len({match['league']['id'] for match in eligible}), len(league_ids))
		self.assertIn(12, {match['league']['id'] for match in eligible})
		self.assertIn(20, {match['league']['id'] for match in eligible})

	def test_home_stops_after_api_network_error_and_uses_last_good_cache(self):
		date = timezone.localdate().isoformat()
		cache.set(f'matches_api:home:v2:{date}:last-good', {
			'date': date,
			'count': 1,
			'matches': [{
				'id': 401,
				'status': 'NS',
				'match_date': (timezone.now() + timedelta(hours=3)).isoformat(),
				'league': {'id': 39, 'name': 'Premier League'},
				'has_market_odds': True,
			}],
			'source': 'api-football',
		}, 3600)
		with patch('apps.matches.views.FootballAPIService') as football_api:
			football_api.return_value.get_fixtures_by_date.return_value = {
				'success': False,
				'error': 'Erro de rede',
				'error_code': 'NETWORK_ERROR',
				'http_status': 503,
			}
			response = MatchViewSet.as_view(
				{'get': 'from_api'}, permission_classes=[AllowAny],
			)(self.factory.get('/api/matches/from_api/', {'date': date}))

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.data['stale'])
		self.assertEqual([match['id'] for match in response.data['matches']], [401])
		self.assertEqual(football_api.return_value.get_fixtures_by_date.call_count, 1)

	def test_home_returns_service_unavailable_without_cache_on_api_failure(self):
		date = timezone.localdate().isoformat()
		with patch('apps.matches.views.FootballAPIService') as football_api:
			football_api.return_value.get_fixtures_by_date.return_value = {
				'success': False,
				'error': 'Erro de rede',
				'error_code': 'NETWORK_ERROR',
				'http_status': 503,
			}
			response = MatchViewSet.as_view(
				{'get': 'from_api'}, permission_classes=[AllowAny],
			)(self.factory.get('/api/matches/from_api/', {'date': date}))

		self.assertEqual(response.status_code, 503)
		self.assertEqual(response.data['source'], 'api-football-unavailable')
		self.assertEqual(football_api.return_value.get_fixtures_by_date.call_count, 1)
