# Seletor da Recomendação Única a partir das Top 3

**Estado:** primeira versão implementada; ganho de acerto ainda não validado.
**Escopo principal:** centralizar a regra de seleção da estratégia `multiple`, usada na recomendação estruturada, no fallback do modal e na geração automática de `DailyBet`. As top 3 não mudam e o Gemini continua desativado. A estratégia `value` fica fora deste escopo.

## Objetivo e invariantes

O seletor deve escolher no máximo uma candidata entre as top 3 já produzidas pelo `DecisionEngine`. Não pode criar uma quarta opção, alterar probabilidades, odds ou scores das candidatas, nem reordenar/substituir as top 3 exibidas.

A implementação deve substituir as regras concorrentes de escolha final por uma regra compartilhada. Não deve acrescentar filtros de elegibilidade, thresholds ou uma nova camada de segurança em runtime. Os filtros de segurança e elegibilidade que já existem continuam nos seus pontos atuais; a regra melhorada ordena apenas as candidatas que cada fluxo já considera elegíveis.

O Gemini permanece desativado. O `AIAnalyzer` fallback deve explicar a seleção já feita, não tomar uma decisão independente. A recomendação estruturada, o texto explicativo do modal e a seleção principal do `DailyBet` devem apontar para a mesma candidata elegível no fluxo `multiple`.

Não há promessa de acerto em uma partida específica. A meta é verificar se uma regra de seleção melhora uma métrica definida em partidas futuras não usadas no ajuste.

## Comportamento anterior

O fluxo tem decisões distintas:

1. `DecisionEngine` e `MarketSelector` geram e ordenam `top_bets`.
2. `DecisionEngine._generate_recommendation()` gera uma recomendação estruturada por prioridades próprias.
3. Com Gemini desativado, `AIAnalyzer._fallback_explanation()` escolhe a aposta descrita no texto do modal.

Antes da alteração, o fallback:

- Estratégia `multiple`: considera elegíveis as opções com odd entre 1,30 e 1,50 e probabilidade de pelo menos 65%. Ordena lexicograficamente por `contextual_fit`, depois `score` e depois probabilidade. Assim, `contextual_fit` domina os outros valores, ainda que sua vantagem seja pequena. Se nenhuma opção passar, o código usa `top_bets[0]` como alternativa.
- Estratégia `value`: usa `top_bets[0]`, sem nova comparação entre as três. Essa regra não foi alterada.

Logo, a escolha escrita pelo fallback podia diferir de `decision_data['recommendation']`, e a seleção do `DailyBetGenerator` seguia outra ordenação. No fluxo `multiple`, essas escolhas passaram a usar o mesmo ranking integrado; a regra de `value` permanece inalterada.

## Objetivo por estratégia e regra ativa

O critério depende do objetivo declarado:

- `multiple`: maximizar a probabilidade de acerto da seleção principal, respeitando os filtros de elegibilidade já adotados pelo fluxo que chama o seletor. A regra ativa usa `ranking_score` como aproximação combinada; ainda não foi comprovado que aumenta a taxa de acerto.
- `DailyBet` em `multiple`: usar a candidata principal primeiro e conservar a possibilidade de usar a candidata distinta seguinte conforme a política atual de alternativas. A composição final dos bilhetes pode mudar e deve ser avaliada como resultado separado.
- `value`: maximizar retorno esperado por unidade seria um objetivo separado; não faz parte desta implementação.

Probabilidades usadas aqui são as probabilidades existentes do sistema. Não se retreinam nem se recalibram os modelos principais nesta implementação.

## Dados para avaliação histórica

A análise individual persiste `analysis_data`, que pode incluir `top_bets`, `recommendation`, `market_odds`, `features_summary` e `context_analysis`. Cada candidata pode conter mercado, posição, probabilidade, odd, odd justa, EV, score, `selection_score`, `context_score`, `contextual_fit` e padrões de apoio.

Para cada análise, associar o snapshot ao resultado final da partida e liquidar cada mercado individualmente usando as regras de mercado existentes. A validação atual de `Analysis` registra principalmente o acerto 1X2; ela não basta para saber se cada mercado alternativo das top 3 acertou. Os resultados das candidatas devem ser reavaliados pelo placar final.

Antes de ajustar qualquer seletor, executar uma auditoria e informar:

- Quantas partidas finalizadas têm snapshot completo das top 3 e placar disponível.
- Quantas têm probabilidade, odd, EV, contexto e estratégia identificáveis.
- Quantas candidatas podem ser liquidadas sem ambiguidade; pushes, cancelamentos e mercados sem suporte devem ser tratados separadamente.
- Quantas observações são duplicatas do mesmo fixture por análises de usuários diferentes. A avaliação deve evitar contar o mesmo jogo várias vezes.

O `HybridAnalysisOrchestrator` agora persiste `strategy` e `multiple_selection` em `analysis_data` para novas análises. Registros antigos podem não conter esses campos; não inferir silenciosamente a estratégia ao analisá-los.

**Auditoria do banco local em 31/10/2026:** havia 92 análises, 83 com top 3, mas nenhuma com placar final local disponível para liquidar essas candidatas. Havia 52 resultados em seleções de `DailyBet`, porém sem as alternativas rejeitadas da top 3. Esses dados não permitem comparar a taxa de acerto da regra antiga com a atual. A implementação é uma correção de consistência/ranking, não uma melhoria de acerto comprovada.

Somente dados conhecidos no momento da análise podem ser usados como atributos do seletor. Não reconstruir contexto histórico com dados atuais de times ou ligas.

## Regra implementada

O seletor recebe as candidatas elegíveis após os filtros que cada fluxo já aplica e os atributos disponíveis na data da análise. Os atributos podem incluir:

- Da candidata: mercado/família, probabilidade existente, odd, EV, score, ranking e suporte contextual.
- Da partida: liga/competição, forma, xG, força, lesões, fadiga, motivação, H2H, clima, padrões contextuais, divergência entre modelos e disponibilidade dos dados.

O critério ativo usa o score que o DecisionEngine já calcula para `multiple`, sem adicionar pesos ou filtros:

- Primeiro: `ranking_score`; se ausente, `score`; se também ausente, `selection_score`.
- Desempate: `contextual_fit` e depois probabilidade.

O `ranking_score` já inclui o score de seleção contextual/probabilístico e os fatores comuns de confiança/risco; em `multiple`, o EV é ignorado conforme a lógica existente. Portanto, o contexto continua influenciando a escolha, mas `contextual_fit` deixa de sobrepor lexicograficamente todo o score.

A ordenação compartilhada não acrescenta elegibilidade: ela recebe candidatas depois dos filtros existentes. A seleção continua heurística e não pode ser chamada de mais precisa até ser comparada com resultados reais fora da amostra.

## Impacto no DailyBet

O `DailyBetGenerator._generate_multiple_tickets()` lê `multiple_result.analysis_data['top_bets']`, aplica filtros de partida e de candidata que já possui. Antes da alteração, ordenava as opções elegíveis por `contextual_fit`, `score` e probabilidade. Pode manter até duas opções de mercados/grupos distintos por partida: a primeira é a principal e a segunda é uma alternativa para a carteira de bilhetes.

**Impacto:** a alteração afeta diretamente a geração automática `multiple`. Após seus filtros, o gerador usa o mesmo ranking score-first do modal. Isso pode mudar a candidata principal e a alternativa distinta mantida e, consequentemente, a composição dos bilhetes. A política atual de até duas alternativas distintas continua valendo.

## Validação de eficácia pendente

1. Garantir que análises finalizadas tenham placar final e snapshot das candidatas.
2. Separar por data e fixture: comparar o ranking antigo e o atual em partidas posteriores, sem usar os resultados de teste para mudar a regra.
3. Medir acerto e cobertura da seleção principal `multiple` e, separadamente, taxa de bilhetes vencedores, retorno e cobertura dos bilhetes completos.
4. Analisar resultados por mercado, liga e contexto apenas quando houver amostra suficiente.
5. Se o score integrado não superar o anterior fora da amostra, revisar com esses resultados; não afirmar melhoria de acerto antes disso.

## Contrato de saída

O resultado preserva `top_bets`, inclui `strategy` e `multiple_selection` em novas análises e expõe a recomendação estruturada correspondente. O fallback explica a seleção do DecisionEngine. O `DailyBetGenerator` aplica seus filtros de partida e usa o mesmo ranking nas candidatas elegíveis; quando os conjuntos elegíveis diferem, o primeiro candidato também pode diferir. Testes devem garantir que:

- A seleção única pertence às top 3 recebidas.
- A seleção respeita os filtros da estratégia.
- A seleção principal do modal e do `DailyBetGenerator` é consistente para `multiple` quando recebem o mesmo conjunto elegível.
- Sem candidata elegível, não se inventa uma recomendação.
- O texto do modal e a recomendação estruturada identificam a mesma candidata.
- As top 3 originais permanecem inalteradas.

## Arquivos de referência

- `backend/apps/analysis/services/decision_engine.py`: criação de `top_bets` e recomendação estruturada.
- `backend/apps/analysis/services/ai_analyzer.py`: regra atual de seleção no fallback.
- `backend/apps/analysis/services/analysis_orchestrator.py`: montagem de `analysis_data` e chamada do fallback.
- `backend/apps/analysis/models.py`: persistência e validação de análises.
- `backend/apps/analysis/services/match_result_sync.py`: liquidação de mercados pelo resultado real.
