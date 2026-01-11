import { useState } from 'react';
import { X, Star, Sparkles, TrendingUp, AlertCircle, Target, Brain, Trophy, Shield, Zap, CheckCircle2, AlertTriangle, BarChart3, Activity, Clock, MapPin, Copy, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { TeamLogo } from '../utils/logos';

export default function AnalysisModal({ match, analysis, onClose, metadata }) {
  const { user } = useAuth();
  const [copied, setCopied] = useState(false);

  console.log('🎭 MODAL RENDERIZANDO:', {
    hasAnalysis: !!analysis,
    hasReasoning: !!analysis?.reasoning,
    hasAnalysisField: !!analysis?.analysis,
    analysisKeys: analysis ? Object.keys(analysis) : [],
    reasoningLength: analysis?.reasoning?.length || 0,
    analysisLength: analysis?.analysis?.length || 0
  });

  if (!analysis) return null;

  // Detectar tipo de análise: objeto estruturado tem prediction_display
  const isSimpleAnalysis = !analysis.prediction_display;
  const analysisText = typeof analysis === 'string' ? analysis : analysis.analysis;
  const confidence = typeof analysis === 'string' ? 3 : (analysis.confidence || 3);

  // Função para copiar análise
  const copyAnalysis = async () => {
    const homeName = match?.home_team?.name || match?.home_team || 'Casa';
    const awayName = match?.away_team?.name || match?.away_team || 'Fora';
    const leagueName = match?.league?.name || match?.league || '';
    const matchDate = match?.date ? new Date(match.date).toLocaleDateString('pt-BR') : '';
    
    const text = `🏆 ${homeName} vs ${awayName}
${leagueName ? `🏅 ${leagueName}` : ''}
${matchDate ? `📅 ${matchDate}` : ''}
${'⭐'.repeat(confidence)} Confiança: ${confidence}/5

${isSimpleAnalysis ? `📊 ANÁLISE COMPLETA:\n\n${analysisText}` : `🎯 PREDIÇÃO: ${analysis.prediction_display}\n\n📊 PROBABILIDADES:\n🏠 ${homeName}: ${analysis.home_probability}%\n🤝 Empate: ${analysis.draw_probability}%\n✈️ ${awayName}: ${analysis.away_probability}%\n\n${analysis.reasoning || ''}`}

──────────────────────────
⚽ Via Placar Certo`.trim();
    
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Erro ao copiar:', err);
    }
  };

  // Formatar texto da análise agrupando em parágrafos
  const formatAnalysisText = (text) => {
    console.log('📝 formatAnalysisText chamado:', {
      hasText: !!text,
      textLength: text?.length || 0,
      firstChars: text?.substring(0, 100) || ''
    });
    
    if (!text) return [];
    
    const lines = text.split('\n');
    const paragraphs = [];
    let currentParagraph = [];
    
    lines.forEach(line => {
      const trimmed = line.trim();
      
      // Ignorar separadores
      if (/^[-=]+$/.test(trimmed)) return;
      
      // Se linha vazia E temos conteúdo acumulado, fechar parágrafo
      if (!trimmed) {
        if (currentParagraph.length > 0) {
          paragraphs.push(currentParagraph.join('\n'));
          currentParagraph = [];
        }
        return;
      }
      
      // Adicionar linha ao parágrafo atual
      currentParagraph.push(trimmed);
    });
    
    // Adicionar último parágrafo se houver
    if (currentParagraph.length > 0) {
      paragraphs.push(currentParagraph.join('\n'));
    }
    
    console.log('📝 formatAnalysisText resultado:', {
      totalParagraphs: paragraphs.length,
      firstParagraph: paragraphs[0]?.substring(0, 100)
    });
    
    return paragraphs;
  };

  // Processar formatação inline (negrito, itálico, números, etc)
  const formatInlineText = (text, homeTeam, awayTeam) => {
    const parts = [];
    let currentIndex = 0;
    
    // Obter nomes dos times
    const homeName = homeTeam?.name || homeTeam || '';
    const awayName = awayTeam?.name || awayTeam || '';
    
    // Padrões de formatação
    const patterns = [
      { regex: /\*\*([^*]+)\*\*/g, type: 'bold' },       // **negrito**
      { regex: /\*([^*]+)\*/g, type: 'bullet' },          // *item de lista*
      { regex: /(\d+%)/g, type: 'percent' },              // percentuais
      { regex: /(\d+\.\d+|\d+:\d+)/g, type: 'number' },   // números decimais/placar
      { regex: /(\d+\s+gol(?:s)?)/gi, type: 'number' },   // X gols
    ];
    
    // Adicionar padrões para nomes de times (escapar caracteres especiais)
    if (homeName) {
      const escapedHome = homeName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      patterns.push({ regex: new RegExp(`(${escapedHome})`, 'gi'), type: 'home_team' });
    }
    if (awayName) {
      const escapedAway = awayName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      patterns.push({ regex: new RegExp(`(${escapedAway})`, 'gi'), type: 'away_team' });
    }
    
    // Primeiro, detectar se a linha começa com * (item de lista)
    const isBullet = /^\*\s+/.test(text);
    if (isBullet) {
      text = text.replace(/^\*\s+/, ''); // Remover * inicial
    }
    
    // Processar todos os padrões
    const matches = [];
    patterns.forEach(({ regex, type }) => {
      let match;
      const r = new RegExp(regex);
      while ((match = r.exec(text)) !== null) {
        matches.push({
          index: match.index,
          length: match[0].length,
          content: match[1] || match[0],
          type,
          fullMatch: match[0]
        });
      }
    });
    
    // Ordenar por posição
    matches.sort((a, b) => a.index - b.index);
    
    // Evitar overlaps
    const validMatches = [];
    let lastEnd = 0;
    matches.forEach(match => {
      if (match.index >= lastEnd) {
        validMatches.push(match);
        lastEnd = match.index + match.length;
      }
    });
    
    // Construir partes
    let position = 0;
    validMatches.forEach(match => {
      // Texto antes do match
      if (match.index > position) {
        parts.push({ type: 'text', content: text.substring(position, match.index) });
      }
      // Match formatado
      parts.push({ type: match.type, content: match.content });
      position = match.index + match.length;
    });
    
    // Texto final
    if (position < text.length) {
      parts.push({ type: 'text', content: text.substring(position) });
    }
    
    return { parts: parts.length > 0 ? parts : [{ type: 'text', content: text }], isBullet };
  };

  const renderStars = (confidence) => {
    // Garantir que temos um número entre 1 e 5
    const stars = Math.max(1, Math.min(5, Math.round(Number(confidence) || 3)));
    
    return (
      <div className="flex items-center gap-1">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`w-5 h-5 sm:w-6 sm:h-6 transition-all ${
              i < stars
                ? 'fill-yellow-400 text-yellow-400 drop-shadow-lg'
                : 'text-white/30'
            }`}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto animate-slide-up">
        {/* Header */}
        <div className="bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 p-4 sm:p-6">
          <div className="absolute top-4 right-4 flex items-center gap-2 z-10">
            <button
              onClick={copyAnalysis}
              className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition-all hover:scale-110"
              title={copied ? 'Copiado!' : 'Copiar análise'}
            >
              {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition-all hover:scale-110"
              title="Fechar"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 sm:p-3 rounded-2xl bg-white/20 backdrop-blur-sm">
              <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-white">Análise com IA</h2>
              <p className="text-primary-100 text-xs sm:text-sm">Powered by Google Gemini</p>
            </div>
          </div>

          {match && (
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 sm:p-6 mt-4">
              <div className="flex flex-col sm:flex-row items-center justify-between text-white gap-4">
                <div className="flex-1 flex flex-col items-center gap-2">
                  <div className="w-12 h-12 sm:w-16 sm:h-16 bg-white rounded-full p-2 shadow-lg">
                    <TeamLogo 
                      team={match.home_team} 
                      size="full"
                      className="w-full h-full object-contain"
                    />
                  </div>
                  <p className="font-bold text-sm sm:text-base text-center">{match.home_team?.name || match.home_team}</p>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="px-3 py-1 sm:px-4 sm:py-2 bg-white/20 rounded-xl font-bold text-base sm:text-lg backdrop-blur-sm">VS</div>
                  {renderStars(confidence)}
                </div>
                <div className="flex-1 flex flex-col items-center gap-2">
                  <div className="w-12 h-12 sm:w-16 sm:h-16 bg-white rounded-full p-2 shadow-lg">
                    <TeamLogo 
                      team={match.away_team} 
                      size="full"
                      className="w-full h-full object-contain"
                    />
                  </div>
                  <p className="font-bold text-sm sm:text-base text-center">{match.away_team?.name || match.away_team}</p>
                </div>
              </div>
              
              {/* Informações do jogo */}
              <div className="mt-4 grid grid-cols-2 gap-2 text-xs sm:text-sm text-white/80">
                {match.league && (
                  <div className="flex items-center gap-1">
                    <Trophy className="w-3 h-3 sm:w-4 sm:h-4" />
                    <span>{match.league.name || match.league}</span>
                  </div>
                )}
                {match.date && (
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3 sm:w-4 sm:h-4" />
                    <span>{new Date(match.date).toLocaleDateString('pt-BR')}</span>
                  </div>
                )}
                {match.venue && (
                  <div className="flex items-center gap-1 col-span-2">
                    <MapPin className="w-3 h-3 sm:w-4 sm:h-4" />
                    <span>{match.venue}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4 sm:p-6">
          {/* Dados Analisados */}
          {metadata && (
            <div className="mb-6 p-4 bg-gradient-to-br from-blue-50 via-blue-100 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-2xl border-2 border-blue-200 dark:border-blue-800 shadow-lg">
              <div className="flex items-center gap-2 mb-3">
                <div className="p-2 bg-blue-500 rounded-lg">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-black text-gray-900 dark:text-white">DADOS ANALISADOS</h3>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs sm:text-sm">
                {metadata.has_predictions && (
                  <div className="flex items-center gap-1 text-green-700 dark:text-green-400">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Previsões</span>
                  </div>
                )}
                {metadata.has_statistics && (
                  <div className="flex items-center gap-1 text-green-700 dark:text-green-400">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Estatísticas</span>
                  </div>
                )}
                {metadata.has_h2h && (
                  <div className="flex items-center gap-1 text-green-700 dark:text-green-400">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>H2H ({metadata.h2h_count} jogos)</span>
                  </div>
                )}
                {metadata.has_fixture_details && (
                  <div className="flex items-center gap-1 text-green-700 dark:text-green-400">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Eventos</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Veredicto Rápido */}
          <div className="mb-6 p-4 sm:p-6 bg-gradient-to-br from-primary-50 via-primary-100 to-accent-50 dark:from-gray-700 dark:to-gray-600 rounded-2xl border-2 border-primary-300 dark:border-primary-600 shadow-lg transition-all hover:shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              {confidence >= 4 ? (
                <div className="p-2 sm:p-3 bg-green-500 rounded-full animate-pulse">
                  <Trophy className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
              ) : confidence >= 3 ? (
                <div className="p-2 sm:p-3 bg-yellow-500 rounded-full">
                  <Shield className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
              ) : (
                <div className="p-2 sm:p-3 bg-orange-500 rounded-full">
                  <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                </div>
              )}
              <div className="flex-1">
                <h3 className="text-lg sm:text-xl font-black text-gray-900 dark:text-white">
                  {confidence >= 4 ? '🔥 FORTE!' : confidence >= 3 ? '⚖️ EQUILIBRADO' : '⚠️ CAUTELA'}
                </h3>
                <p className="text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-200">
                  {confidence >= 4
                    ? 'Aposte com confiança'
                    : confidence >= 3
                    ? 'Análise moderada'
                    : 'Risco elevado'}
                </p>
              </div>
            </div>
          </div>

          {isSimpleAnalysis ? (
            <div className="space-y-4">
              {/* Análise Completa Formatada */}
              <div className="bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-4 sm:p-6 border-2 border-gray-200 dark:border-gray-600 shadow-lg">
                <div className="flex items-center gap-2 mb-4">
                  <Brain className="w-5 h-5 sm:w-6 sm:h-6 text-primary-500" />
                  <h3 className="text-lg sm:text-xl font-black text-gray-900 dark:text-white">ANÁLISE DETALHADA</h3>
                </div>
                <div className="space-y-4">
                  {formatAnalysisText(analysisText).map((paragraph, idx) => {
                    // Detectar se é um título (começa com emoji)
                    const isTitle = /^(1️⃣|2️⃣|3️⃣|4️⃣|5️⃣|📊|⚽|🎯|⚠️|💡|🔥|⭐|📈|📉|💪|🏆|📜|⚔️|💰)/.test(paragraph);
                    
                    return (
                      <div 
                        key={idx}
                        className={`leading-relaxed text-sm sm:text-base animate-fade-in ${
                          isTitle ? 'font-bold text-base sm:text-lg text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-200'
                        }`}
                        style={{ animationDelay: `${idx * 0.05}s` }}
                      >
                        {paragraph.split('\n').map((line, lidx) => {
                          const formatted = formatInlineText(line, match?.home_team, match?.away_team);
                          return (
                            <div 
                              key={lidx}
                              className={formatted.isBullet ? 'flex items-start gap-2 ml-4 mb-1' : 'mb-1'}
                            >
                              {formatted.isBullet && (
                                <span className="text-primary-500 font-bold mt-0.5">•</span>
                              )}
                              <span className="flex-1 flex items-center flex-wrap gap-1">
                                {formatted.parts.map((part, pidx) => {
                                  if (part.type === 'bold') {
                                    return <strong key={pidx} className="font-bold text-gray-900 dark:text-white">{part.content}</strong>;
                                  } else if (part.type === 'number' || part.type === 'percent') {
                                    return (
                                      <span key={pidx} className="font-bold text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-1.5 py-0.5 rounded mx-0.5">
                                        {part.content}
                                      </span>
                                    );
                                  } else if (part.type === 'home_team') {
                                    return (
                                      <span key={pidx} className="inline-flex items-center gap-1 font-semibold text-gray-900 dark:text-white">
                                        <span className="inline-block w-4 h-4 sm:w-5 sm:h-5">
                                          <TeamLogo team={match?.home_team} size="full" className="w-full h-full object-contain" />
                                        </span>
                                        {part.content}
                                      </span>
                                    );
                                  } else if (part.type === 'away_team') {
                                    return (
                                      <span key={pidx} className="inline-flex items-center gap-1 font-semibold text-gray-900 dark:text-white">
                                        <span className="inline-block w-4 h-4 sm:w-5 sm:h-5">
                                          <TeamLogo team={match?.away_team} size="full" className="w-full h-full object-contain" />
                                        </span>
                                        {part.content}
                                      </span>
                                    );
                                  } else {
                                    return <span key={pidx}>{part.content}</span>;
                                  }
                                })}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-5">
              {/* Predição Principal */}
              <div className="relative bg-gradient-to-br from-primary-500 via-primary-600 to-accent-600 text-white rounded-2xl p-8 shadow-2xl overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12"></div>
                <div className="relative text-center">
                  <div className="flex items-center justify-center gap-2 mb-4">
                    <div className="p-3 bg-white/20 rounded-full backdrop-blur-sm animate-pulse">
                      <Target className="w-7 h-7" />
                    </div>
                    <h3 className="text-2xl font-black">PREDIÇÃO</h3>
                  </div>
                  <div className="flex items-center justify-center gap-3 mb-3">
                    {analysis.prediction_team === 'home' && (
                      <div className="w-16 h-16 sm:w-20 sm:h-20 bg-white rounded-full p-2 shadow-lg">
                        <TeamLogo team={match?.home_team} size="full" className="w-full h-full object-contain" />
                      </div>
                    )}
                    {analysis.prediction_team === 'away' && (
                      <div className="w-16 h-16 sm:w-20 sm:h-20 bg-white rounded-full p-2 shadow-lg">
                        <TeamLogo team={match?.away_team} size="full" className="w-full h-full object-contain" />
                      </div>
                    )}
                    <div className="text-4xl sm:text-5xl font-black drop-shadow-lg">{analysis.prediction_display}</div>
                  </div>
                  <div className="flex items-center justify-center gap-1 text-yellow-300 text-3xl mb-2">
                    {analysis.confidence_display}
                  </div>
                </div>
              </div>

              {/* Probabilidades */}

              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-2xl p-4 sm:p-5 shadow-xl text-center transform hover:scale-105 transition-all">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <div className="w-6 h-6 sm:w-8 sm:h-8 bg-white rounded-full p-1">
                      <TeamLogo team={match?.home_team} size="full" className="w-full h-full object-contain" />
                    </div>
                    <div className="text-xs sm:text-sm font-bold opacity-90 truncate">{match?.home_team?.name || match?.home_team || 'CASA'}</div>
                  </div>
                  <div className="text-3xl sm:text-4xl font-black mb-1">{analysis.home_probability}%</div>
                  <div className="h-2 bg-white/30 rounded-full overflow-hidden">
                    <div className="h-full bg-white rounded-full transition-all duration-500" style={{ width: `${analysis.home_probability}%` }}></div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-gray-500 to-gray-600 text-white rounded-2xl p-4 sm:p-5 shadow-xl text-center transform hover:scale-105 transition-all">
                  <div className="text-xs sm:text-sm font-bold mb-1 opacity-90">🤝 EMPATE</div>
                  <div className="text-3xl sm:text-4xl font-black mb-1">{analysis.draw_probability}%</div>
                  <div className="h-2 bg-white/30 rounded-full overflow-hidden">
                    <div className="h-full bg-white rounded-full transition-all duration-500" style={{ width: `${analysis.draw_probability}%` }}></div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-4 sm:p-5 shadow-xl text-center transform hover:scale-105 transition-all">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <div className="w-6 h-6 sm:w-8 sm:h-8 bg-white rounded-full p-1">
                      <TeamLogo team={match?.away_team} size="full" className="w-full h-full object-contain" />
                    </div>
                    <div className="text-xs sm:text-sm font-bold opacity-90 truncate">{match?.away_team?.name || match?.away_team || 'FORA'}</div>
                  </div>
                  <div className="text-3xl sm:text-4xl font-black mb-1">{analysis.away_probability}%</div>
                  <div className="h-2 bg-white/30 rounded-full overflow-hidden">
                    <div className="h-full bg-white rounded-full transition-all duration-500" style={{ width: `${analysis.away_probability}%` }}></div>
                  </div>
                </div>
              </div>

              {/* Fair Odds + Value Bets + Risk */}
              {analysis.analysis_data && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* Fair Odds */}
                  {analysis.analysis_data.fair_odds && (
                    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-4 sm:p-6 border-2 border-purple-200 dark:border-indigo-700 shadow-lg">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="p-2 bg-indigo-600 rounded-lg">
                          <Target className="w-5 h-5 text-white" />
                        </div>
                        <h3 className="text-lg font-black text-gray-900 dark:text-white">ODDS JUSTAS (MODELOS)</h3>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div className="text-center">
                          <div className="font-bold text-indigo-700 dark:text-indigo-400">CASA</div>
                          <div className="text-gray-900 dark:text-white text-xl font-black">{analysis.analysis_data.fair_odds.home_win?.toFixed(2)}</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold text-indigo-700 dark:text-indigo-400">EMPATE</div>
                          <div className="text-gray-900 dark:text-white text-xl font-black">{analysis.analysis_data.fair_odds.draw?.toFixed(2)}</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold text-indigo-700 dark:text-indigo-400">FORA</div>
                          <div className="text-gray-900 dark:text-white text-xl font-black">{analysis.analysis_data.fair_odds.away_win?.toFixed(2)}</div>
                        </div>
                      </div>
                      {analysis.analysis_data.risk && (
                        <div className="mt-3 text-xs sm:text-sm">
                          <span className="inline-block px-2 py-1 rounded-lg bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300 font-semibold">
                            RISCO: {String(analysis.analysis_data.risk).toUpperCase()}
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Market Odds */}
                  {analysis.analysis_data.market_odds && (
                    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-4 sm:p-6 border-2 border-blue-200 dark:border-cyan-700 shadow-lg">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="p-2 bg-blue-600 rounded-lg">
                          <Activity className="w-5 h-5 text-white" />
                        </div>
                        <h3 className="text-lg font-black text-gray-900 dark:text-white">ODDS DE MERCADO</h3>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div className="text-center">
                          <div className="font-bold text-blue-700 dark:text-blue-400">CASA</div>
                          <div className="text-gray-900 dark:text-white text-xl font-black">{analysis.analysis_data.market_odds.home_win ? Number(analysis.analysis_data.market_odds.home_win).toFixed(2) : '—'}</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold text-blue-700 dark:text-blue-400">EMPATE</div>
                          <div className="text-gray-900 dark:text-white text-xl font-black">{analysis.analysis_data.market_odds.draw ? Number(analysis.analysis_data.market_odds.draw).toFixed(2) : '—'}</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold text-blue-700 dark:text-blue-400">FORA</div>
                          <div className="text-gray-900 dark:text-white text-xl font-black">{analysis.analysis_data.market_odds.away_win ? Number(analysis.analysis_data.market_odds.away_win).toFixed(2) : '—'}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Value Bets */}
                  {Array.isArray(analysis.analysis_data.value_bets) && analysis.analysis_data.value_bets.length > 0 && (
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-4 sm:p-6 border-2 border-green-200 dark:border-emerald-700 shadow-lg">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="p-2 bg-green-600 rounded-lg">
                          <TrendingUp className="w-5 h-5 text-white" />
                        </div>
                        <h3 className="text-lg font-black text-gray-900 dark:text-white">OPORTUNIDADES DE VALUE</h3>
                      </div>
                      <div className="space-y-3">
                        {analysis.analysis_data.value_bets.slice(0,3).map((vb, idx) => (
                          <div key={idx} className="p-3 rounded-xl bg-white dark:bg-gray-800 border border-green-100 dark:border-gray-700">
                            <div className="flex items-center justify-between">
                              <div>
                                <div className="text-sm font-bold text-gray-900 dark:text-white">{vb.market_display}</div>
                                <div className="text-xs text-gray-600 dark:text-gray-300">Odd Justa {vb.fair_odd?.toFixed(2)} vs Mercado {vb.market_odd?.toFixed(2)}</div>
                              </div>
                              <div className="text-right">
                                <div className="text-sm font-black text-green-700 dark:text-green-400">{vb.value_pct?.toFixed(1)}% value</div>
                                <div className="text-xs text-gray-600 dark:text-gray-300">{vb.stake_suggestion}</div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Análise Completa - Aberta por padrão com Formatação */}
              {analysis.reasoning && (
                <div className="bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-6 border-2 border-gray-200 dark:border-gray-600 shadow-lg">
                  <div className="flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5 sm:w-6 sm:h-6 text-primary-500" />
                    <h3 className="text-lg sm:text-xl font-black text-gray-900 dark:text-white">ANÁLISE DETALHADA</h3>
                  </div>
                  <div className="space-y-4">
                    {formatAnalysisText(analysis.reasoning).map((paragraph, idx) => {
                      // Detectar se é um título (começa com emoji ou separador)
                      const isTitle = /^(1️⃣|2️⃣|3️⃣|4️⃣|5️⃣|📊|⚽|🎯|⚠️|💡|🔥|⭐|📈|📉|💪|🏆|📜|⚔️|💰|🏠|✈️|═|─)/.test(paragraph);
                      const isSeparator = /^═+$/.test(paragraph);
                      
                      if (isSeparator) return null; // Ignorar separadores
                      
                      return (
                        <div 
                          key={idx}
                          className={`leading-relaxed text-sm sm:text-base animate-fade-in ${
                            isTitle ? 'font-bold text-base sm:text-lg text-gray-900 dark:text-white mt-2' : 'text-gray-700 dark:text-gray-200'
                          }`}
                          style={{ animationDelay: `${idx * 0.05}s` }}
                        >
                          {paragraph.split('\n').map((line, lidx) => {
                            const formatted = formatInlineText(line, match?.home_team, match?.away_team);
                            return (
                              <div 
                                key={lidx}
                                className={formatted.isBullet ? 'flex items-start gap-2 ml-4 mb-1' : 'mb-1'}
                              >
                                {formatted.isBullet && (
                                  <span className="text-primary-500 font-bold mt-0.5">•</span>
                                )}
                                <span className="flex-1 flex items-center flex-wrap gap-1">
                                  {formatted.parts.map((part, pidx) => {
                                    if (part.type === 'bold') {
                                      return <strong key={pidx} className="font-bold text-gray-900 dark:text-white">{part.content}</strong>;
                                    } else if (part.type === 'number' || part.type === 'percent') {
                                      return (
                                        <span key={pidx} className="font-bold text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-1.5 py-0.5 rounded mx-0.5">
                                          {part.content}
                                        </span>
                                      );
                                    } else if (part.type === 'home_team') {
                                      return (
                                        <span key={pidx} className="inline-flex items-center gap-1 font-semibold text-gray-900 dark:text-white">
                                          <span className="inline-block w-4 h-4 sm:w-5 sm:h-5">
                                            <TeamLogo team={match?.home_team} size="full" className="w-full h-full object-contain" />
                                          </span>
                                          {part.content}
                                        </span>
                                      );
                                    } else if (part.type === 'away_team') {
                                      return (
                                        <span key={pidx} className="inline-flex items-center gap-1 font-semibold text-gray-900 dark:text-white">
                                          <span className="inline-block w-4 h-4 sm:w-5 sm:h-5">
                                            <TeamLogo team={match?.away_team} size="full" className="w-full h-full object-contain" />
                                          </span>
                                          {part.content}
                                        </span>
                                      );
                                    } else {
                                      return <span key={pidx}>{part.content}</span>;
                                    }
                                  })}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Remaining Analyses (for free users) */}
          {user && !user.is_premium && analysis.remaining_analyses !== undefined && (
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-2xl border border-blue-200 dark:border-blue-800">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-blue-900 dark:text-blue-300">
                    Análises Restantes Hoje
                  </p>
                  <p className="text-sm text-blue-700 dark:text-blue-400 mt-1">
                    Você tem <span className="font-bold">{analysis.remaining_analyses}</span> análise
                    {analysis.remaining_analyses !== 1 ? 's' : ''} restante
                    {analysis.remaining_analyses !== 1 ? 's' : ''}.
                  </p>
                  {analysis.remaining_analyses === 0 && (
                    <button className="mt-3 w-full py-2 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-semibold hover:from-primary-700 hover:to-primary-800 transition-all">
                      Assinar Premium - Análises Ilimitadas
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Disclaimer */}
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-gray-200 dark:border-gray-600">
            <p className="text-xs text-gray-600 dark:text-gray-400 text-center">
              ⚠️ Esta análise é gerada por inteligência artificial e serve apenas como orientação.
              Aposte com responsabilidade e considere múltiplas fontes de informação.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
