import os
import sys
from datetime import datetime
from pathlib import Path

# Ensure backend root is on sys.path
BACKEND_ROOT = str(Path(__file__).resolve().parents[1])
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.matches.services.football_api import FootballAPIService


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')
    svc = FootballAPIService()
    res = svc.get_fixtures_by_date(date_str)
    print(f"success={res.get('success')} count={res.get('count')}")
    fixtures = res.get('fixtures', [])

    def has_rennes_psg(f):
        try:
            home = f['teams']['home']['name'].lower()
            away = f['teams']['away']['name'].lower()
            def is_psg(name: str):
                return 'paris saint germain' in name or 'psg' in name or 'paris' in name
            return ('rennes' in home and is_psg(away)) or (is_psg(home) and 'rennes' in away)
        except Exception:
            return False

    found = [f for f in fixtures if has_rennes_psg(f)]
    if not found:
        print("NOT_FOUND")
        return 1

    for f in found:
        fix = f['fixture']
        league = f.get('league', {})
        teams = f.get('teams', {})
        print(f"FOUND id={fix.get('id')} league={league.get('name')} date={fix.get('date')} home={teams.get('home', {}).get('name')} away={teams.get('away', {}).get('name')}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
