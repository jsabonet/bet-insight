import { useNavigate } from 'react-router-dom';
import { Calendar, MapPin, Zap } from 'lucide-react';
import { TeamLogo, LeagueLogo } from '../utils/logos';

export default function MatchCard({ match, onAnalyze }) {
  const navigate = useNavigate();
  
  const formatDate = (dateString) => {
    // Se não houver data válida, retornar valores padrão
    if (!dateString) {
      return { day: 'A definir', time: '--:--' };
    }

    // Tentar criar a data (suporta ISO 8601 e timestamps)
    const date = new Date(dateString);
    
    // Verificar se a data é válida
    if (isNaN(date.getTime())) {
      return { day: 'Data inválida', time: '--:--' };
    }

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

  // Aceitar tanto match_date (banco de dados) quanto date (API externa)
  const matchDate = match.match_date || match.date;

  const getStatusBadge = (status, dateString) => {
    // Verificar se a partida já passou
    if (dateString) {
      const matchDateTime = new Date(dateString);
      const now = new Date();
      
      // Se a partida foi há mais de 2 horas, considerar finalizada
      const twoHoursAgo = new Date(now.getTime() - (2 * 60 * 60 * 1000));
      
      if (matchDateTime < twoHoursAgo && status !== 'FINISHED' && status !== 'FT' && !['1H', '2H', 'HT', 'ET', 'BT', 'P', 'LIVE', 'IN_PLAY'].includes(status)) {
        status = 'FINISHED';
      }
    }
    
    const badges = {
      SCHEDULED: { text: 'Agendada', className: 'badge bg-gray-100 text-gray-600 border-gray-200' },
      NS: { text: 'Agendada', className: 'badge bg-gray-100 text-gray-600 border-gray-200' },
      TBD: { text: 'Agendada', className: 'badge bg-gray-100 text-gray-600 border-gray-200' },
      LIVE: { text: 'Ao Vivo', className: 'badge bg-red-500 text-white border-red-600 animate-pulse-soft' },
      '1H': { text: 'Ao Vivo', className: 'badge bg-red-500 text-white border-red-600 animate-pulse-soft' },
      '2H': { text: 'Ao Vivo', className: 'badge bg-red-500 text-white border-red-600 animate-pulse-soft' },
      HT: { text: 'Intervalo', className: 'badge bg-orange-500 text-white border-orange-600' },
      FINISHED: { text: 'Finalizada', className: 'badge badge-success' },
      FT: { text: 'Finalizada', className: 'badge badge-success' },
      AET: { text: 'Finalizada', className: 'badge badge-success' },
      PEN: { text: 'Finalizada', className: 'badge badge-success' },
    };
    return badges[status] || badges.SCHEDULED;
  };

  const badge = getStatusBadge(match.status, matchDate);
  const { day, time } = formatDate(matchDate);

  // Aceitar múltiplos formatos de times
  const homeTeam = match.home_team || { name: match.home_team_name || 'Time Casa' };
  const awayTeam = match.away_team || { name: match.away_team_name || 'Time Visitante' };
  const league = match.league || { name: match.league_name || 'Liga' };

  return (
    <div className="match-card group animate-slide-up" onClick={() => match.id && navigate(`/match/${match.id}`)}>
      {/* Header - Liga */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-sm">
          <LeagueLogo league={league} size="sm" />
          <span className="text-gray-600 dark:text-gray-400 font-medium">{league.name || league}</span>
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
            <TeamLogo team={homeTeam} size="md" />
            <span className="font-bold text-gray-900 dark:text-gray-100 text-base">{homeTeam.name || homeTeam}</span>
          </div>
          {match.home_score !== null && match.home_score !== undefined && (
            <span className="text-2xl font-bold text-primary-600 dark:text-primary-400 ml-2">
              {match.home_score}
            </span>
          )}
        </div>

        <div className="flex items-center justify-center my-2">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>
          <span className="px-3 py-1 text-gray-700 dark:text-gray-300 text-sm font-bold">VS</span>
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent"></div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1">
            <TeamLogo team={awayTeam} size="md" />
            <span className="font-bold text-gray-900 dark:text-gray-100 text-base">{awayTeam.name || awayTeam}</span>
          </div>
          {match.away_score !== null && match.away_score !== undefined && (
            <span className="text-2xl font-bold text-blue-600 dark:text-blue-400 ml-2">
              {match.away_score}
            </span>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <Calendar className="w-4 h-4" />
          <span className="font-medium">{day}</span>
          <span className="text-gray-400 dark:text-gray-600">•</span>
          <span>{time}</span>
        </div>

        <button 
          onClick={(e) => {
            e.stopPropagation();
            if (onAnalyze && match.id) {
              onAnalyze(match.id);
            } else if (match.id) {
              navigate(`/match/${match.id}`);
            }
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
