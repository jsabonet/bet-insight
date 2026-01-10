import { Info, Users, Clock, Heart, Cloud } from 'lucide-react';

/**
 * CONTEXTO DA PARTIDA
 * Lesões, descanso, fase da temporada, H2H, clima
 * Dados do enriquecimento
 */
export default function MatchContext({ analysis, match }) {
  if (!analysis?.enriched_data) return null;

  const enriched = analysis.enriched_data;
  const { injuries, rest_context, h2h, weather } = enriched;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Info className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Contexto da Partida</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Lesões e Suspensões */}
        {injuries && (
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-3">
              <Users className="w-4 h-4 text-red-600 dark:text-red-400" />
              <h3 className="font-semibold text-gray-900 dark:text-white">Lesões & Suspensões</h3>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Casa</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {injuries.home?.length || 0}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Fora</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {injuries.away?.length || 0}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Descanso */}
        {rest_context && (
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-3">
              <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <h3 className="font-semibold text-gray-900 dark:text-white">Descanso</h3>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Casa</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {rest_context.home_days_rest} dias
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Fora</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {rest_context.away_days_rest} dias
                </div>
              </div>
            </div>

            {rest_context.advantage && rest_context.advantage !== 'neutral' && (
              <div className="mt-2 text-xs text-center">
                <span className="text-gray-600 dark:text-gray-400">Vantagem: </span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {rest_context.advantage === 'home' ? match.home_team?.name || match.home_team : match.away_team?.name || match.away_team}
                </span>
              </div>
            )}
          </div>
        )}

        {/* H2H Resumido */}
        {h2h && h2h.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-3">
              <Heart className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <h3 className="font-semibold text-gray-900 dark:text-white">Confrontos Diretos</h3>
            </div>

            <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Últimos {h2h.length} jogos
            </div>

            {h2h.slice(0, 3).map((game, index) => (
              <div key={index} className="text-xs text-gray-700 dark:text-gray-300 py-1">
                {new Date(game.utcDate).toLocaleDateString('pt-BR')}: {game.homeTeam.name} {game.score?.fullTime?.home || 0}-{game.score?.fullTime?.away || 0} {game.awayTeam.name}
              </div>
            ))}
          </div>
        )}

        {/* Clima */}
        {weather && weather.weather_impact !== 0 && (
          <div className="bg-gradient-to-br from-cyan-50 to-blue-50 dark:from-cyan-900/20 dark:to-blue-900/20 rounded-xl p-4 border-2 border-cyan-300 dark:border-cyan-700">
            <div className="flex items-center gap-2 mb-3">
              <Cloud className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
              <h3 className="font-semibold text-gray-900 dark:text-white">Condições Climáticas</h3>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400">Condição:</span>
                <span className="font-semibold text-gray-900 dark:text-white">{weather.condition}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400">Temperatura:</span>
                <span className="font-semibold text-gray-900 dark:text-white">{weather.temperature}°C</span>
              </div>
              {weather.weather_impact && (
                <div className="mt-2 pt-2 border-t border-cyan-200 dark:border-cyan-700">
                  <div className="text-xs text-cyan-600 dark:text-cyan-400">
                    ⚠️ Impacto estimado: {weather.weather_impact > 0 ? '+' : ''}{weather.weather_impact.toFixed(2)} gols
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
