import os
import sys
from pathlib import Path

BACKEND_ROOT = str(Path(__file__).resolve().parents[1])
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from apps.matches.views import MatchViewSet


def main():
    factory = APIRequestFactory()
    # Allow overriding strategy via CLI arg (default: value)
    strategy = sys.argv[1] if len(sys.argv) > 1 else 'value'
    payload = {
        'home_team': 'Rennes',
        'away_team': 'Paris Saint Germain',
        'league': 'Ligue 1',
        'date': '2026-02-13T18:00:00Z',
        'api_id': 1387895,
        'strategy': strategy,
        'skip_ai': True
    }

    request = factory.post('/api/matches/quick_analyze/', payload, format='json')
    # Authenticate with a test superuser to bypass any global auth constraints
    User = get_user_model()
    user, _ = User.objects.get_or_create(username='test_quick_user', defaults={'is_staff': True, 'is_superuser': True})
    force_authenticate(request, user=user)

    view = MatchViewSet.as_view({'post': 'quick_analyze'})
    response = view(request)

    print('status:', response.status_code)
    data = response.data
    print('has top_bets:', bool(data.get('top_bets')))
    if data.get('top_bets'):
        for b in data['top_bets'][:3]:
            print(f"#{b['rank']} {b['market_display']} prob={b['probability']*100:.1f}% odd={b['market_odd']} ev={b['ev_pct']:+.1f}%")
    print('has context_analysis:', bool(data.get('context_analysis')))


if __name__ == '__main__':
    main()
