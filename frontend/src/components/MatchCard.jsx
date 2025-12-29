import { useNavigate } from 'react-router-dom';
import { Calendar, MapPin, Zap } from 'lucide-react';

export default function MatchCard({ match, onAnalyze }) {
  const navigate = useNavigate();
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const dateStr = date.toLocaleDateString('pt-PT');
    const todayStr = today.toLocaleDateString('pt-PT');
    const tomorrowStr = tomorrow.toLocaleDateString('pt-PT');

    let dayLabel = dateStr;
    if (dateStr === todayStr) dayLabel = 'Hoje';
    else if (dateStr === tomorrowStr) dayLabel = 'Amanhã';
    else {
      dayLabel = new Intl.DateTimeFormat('pt-PT', { day: '2-digit', month: 'short' }).format(date);
    }

    return {
      day: dayLabel,
      time: date.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
    };
  };

  const getStatusBadge = (status) => {
    const badges = {
      SCHEDULED: { text: 'Agendada', className: 'badge bg-gray-100 text-gray-600 border-gray-200' },
      LIVE: { text: 'Ao Vivo', className: 'badge bg-red-500 text-white border-red-600 animate-pulse-soft' },
      FINISHED: { text: 'Finalizada', className: 'badge badge-success' },
    };
    return badges[status] || badges.SCHEDULED;
  };

  const badge = getStatusBadge(match.status);
  const { day, time } = formatDate(match.match_date);

  return (
    <div className="match-card group animate-slide-up" onClick={() => navigate(`/match/${match.id}`)}>
      {/* Header - Liga */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-sm">
          <MapPin className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600 font-medium">{match.league.name}</span>
        </div>
        <span className={badge.className}>
          {match.status === 'LIVE' && <span className="w-2 h-2 bg-white rounded-full animate-pulse mr-1.5"></span>}
          {badge.text}
        </span>
      </div>

      {/* Times */}
      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center text-xl border border-primary-200">
              {match.home_team.logo ? (
                <img src={match.home_team.logo} alt="" className="w-6 h-6" />
              ) : (
                '🏠'
              )}
            </div>
            <span className="font-bold text-gray-900 text-base">{match.home_team.name}</span>
          </div>
          {match.home_score !== null && (
            <span className="text-2xl font-bold text-primary-600 ml-2">
              {match.home_score}
            </span>
          )}
        </div>

        <div className="flex items-center justify-center">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
          <span className="px-3 text-gray-400 text-xs font-semibold">VS</span>
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center text-xl border border-blue-200">
              {match.away_team.logo ? (
                <img src={match.away_team.logo} alt="" className="w-6 h-6" />
              ) : (
                '✈️'
              )}
            </div>
            <span className="font-bold text-gray-900 text-base">{match.away_team.name}</span>
          </div>
          {match.away_score !== null && (
            <span className="text-2xl font-bold text-blue-600 ml-2">
              {match.away_score}
            </span>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="w-4 h-4" />
          <span className="font-medium">{day}</span>
          <span className="text-gray-400">•</span>
          <span>{time}</span>
        </div>

        <button 
          onClick={(e) => {
            e.stopPropagation();
            if (onAnalyze) onAnalyze(match.id);
            else navigate(`/match/${match.id}`);
          }}
          className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl text-sm font-semibold hover:from-primary-700 hover:to-primary-800 transition-all group-hover:scale-105 shadow-md shadow-primary-600/30 active:scale-95"
        >
          <Zap className="w-4 h-4" />
          Analisar
        </button>
      </div>
    </div>
  );
}
