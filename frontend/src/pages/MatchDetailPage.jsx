import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { matchesAPI, analysisAPI } from '../services/api';
import { ArrowLeft, TrendingUp, Target, Brain, Star, AlertCircle } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import { TeamLogo, LeagueLogo } from '../utils/logos';

export default function MatchDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [match, setMatch] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadMatchDetails();
  }, [id]);

  const loadMatchDetails = async () => {
    try {
      const response = await matchesAPI.getDetail(id);
      setMatch(response.data);
    } catch (error) {
      console.error('Erro ao carregar partida:', error);
      setError('Erro ao carregar detalhes da partida');
    } finally {
      setLoading(false);
    }
  };

  const handleRequestAnalysis = async () => {
    setError('');
    setAnalyzing(true);

    try {
      const response = await analysisAPI.requestAnalysis(id);
      setAnalysis(response.data.analysis);
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erro ao gerar análise';
      setError(errorMsg);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <Header title="Carregando..." />
        <div className="page-content text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="page-container">
        <Header title="Erro" />
        <div className="page-content">
          <p className="text-center text-gray-600">Partida não encontrada</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header title="Análise da Partida" />
      
      <div className="page-content">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 btn-ghost"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar
        </button>

        {/* Card da Partida */}
        <div className="card animate-slide-up mb-6">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center gap-2 mb-3">
              <LeagueLogo league={match.league} size="md" />
              <span className="badge badge-info">{match.league.name}</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mt-2">
              {match.home_team.name} vs {match.away_team.name}
            </h1>
            <p className="text-gray-600 mt-1">
              {new Date(match.match_date).toLocaleString('pt-PT')}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="text-center p-6 bg-gradient-to-br from-primary-50 to-primary-100 rounded-2xl">
              <div className="flex justify-center mb-3">
                <TeamLogo team={match.home_team} size="xl" />
              </div>
              <h3 className="font-bold text-lg">{match.home_team.name}</h3>
              <p className="text-sm text-gray-600 mt-1">Casa</p>
            </div>
            <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl">
              <div className="flex justify-center mb-3">
                <TeamLogo team={match.away_team} size="xl" />
              </div>
              <h3 className="font-bold text-lg">{match.away_team.name}</h3>
              <p className="text-sm text-gray-600 mt-1">Visitante</p>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {!analysis && (
            <button
              onClick={handleRequestAnalysis}
              disabled={analyzing}
              className="w-full btn-primary flex items-center justify-center gap-2"
            >
              <Brain className="w-5 h-5" />
              {analyzing ? 'Analisando com IA...' : 'Gerar Análise Inteligente'}
            </button>
          )}
        </div>

        {/* Análise */}
        {analysis && (
          <div className="space-y-4 animate-slide-up">
            {/* Predição Principal */}
            <div className="card bg-gradient-to-br from-primary-600 to-primary-700 text-white">
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-3">
                  <Target className="w-6 h-6" />
                  <h2 className="text-xl font-bold">Predição</h2>
                </div>
                <div className="text-4xl font-bold mb-2">{analysis.prediction_display}</div>
                <div className="flex items-center justify-center gap-1 text-yellow-300 text-2xl">
                  {analysis.confidence_display}
                </div>
                <p className="text-primary-100 mt-2">Confiança: {analysis.confidence}/5</p>
              </div>
            </div>

            {/* Probabilidades */}
            <div className="card">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary-600" />
                Probabilidades
              </h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="font-medium">Vitória Casa</span>
                    <span className="font-bold text-primary-600">{analysis.home_probability}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-primary-600 h-3 rounded-full transition-all"
                      style={{ width: `${analysis.home_probability}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="font-medium">Empate</span>
                    <span className="font-bold text-gray-600">{analysis.draw_probability}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-gray-600 h-3 rounded-full transition-all"
                      style={{ width: `${analysis.draw_probability}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="font-medium">Vitória Visitante</span>
                    <span className="font-bold text-blue-600">{analysis.away_probability}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 h-3 rounded-full transition-all"
                      style={{ width: `${analysis.away_probability}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Expected Goals */}
            {analysis.home_xg && analysis.away_xg && (
              <div className="card">
                <h3 className="text-lg font-bold mb-4">Expected Goals (xG)</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-primary-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">{match.home_team.name}</p>
                    <p className="text-3xl font-bold text-primary-600">{analysis.home_xg}</p>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">{match.away_team.name}</p>
                    <p className="text-3xl font-bold text-blue-600">{analysis.away_xg}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Raciocínio */}
            <div className="card">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Brain className="w-5 h-5 text-primary-600" />
                Análise Detalhada
              </h3>
              <p className="text-gray-700 leading-relaxed mb-4">{analysis.reasoning}</p>
              
              <h4 className="font-bold mb-2">Fatores Chave:</h4>
              <ul className="space-y-2">
                {analysis.key_factors.map((factor, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-primary-600 mt-1">✓</span>
                    <span className="text-gray-700">{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
