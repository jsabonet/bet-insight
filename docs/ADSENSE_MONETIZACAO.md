# Guia de Monetização com Google AdSense (PlacarCerto)

Este documento avalia a elegibilidade do projeto para monetização via Google AdSense e descreve um passo a passo completo — do preparo à aprovação — com estimativas de tempo.

## Avaliação de Elegibilidade

- Conteúdo principal: análises e previsões de futebol, com planos free/premium e PWA. Tecnicamente, o site é rápido, mobile-friendly e com boa UX.
- Risco de política: qualquer associação explícita a "apostas" (betting, odds, chamadas à ação para apostar, links para casas de apostas) pode fazer o AdSense reprovar. Para AdSense, páginas que facilitam ou promovem jogos de azar online costumam ser proibidas.
- Situação atual: o projeto foi rebrand para PlacarCerto. Se ainda existirem referências a "bet" (ex.: pastas, textos, CTAs), recomenda-se removê-las. O posicionamento deve ser informativo/educativo (estatísticas e insights), sem incentivar apostas ou linkar para operadores.
- Logos e marcas: verifique direitos de uso de logotipos de times/ligas. Caso não haja licença, prefira ícones genéricos ou texto para evitar riscos de direitos autorais.
- Conclusão: elegível sob condições. Se não houver incentivo direto a apostas nem links para casas de apostas, e o conteúdo for original, informativo e em conformidade com as políticas do Google, a aprovação é possível.

## Ajustes Recomendados (antes do pedido)

- Remover/neutralizar menções a apostas: evitar termos como "apostar", "odds", "bookmaker", "bet", CTAs do tipo "aposte agora".
- Não usar links externos para casas de apostas, afiliados ou landing pages de jogos de azar.
- Páginas obrigatórias: Política de Privacidade, Termos de Uso, Sobre e Contato — visíveis no rodapé e indexadas.
- Consentimento de cookies e TCF v2: usar uma CMP compatível (Cookiebot, OneTrust, etc.) para tráfego europeu e garantir coleta de consentimento.
- Conteúdo original: evitar scraping ou cópia. Sempre citar fontes públicas, sem violar direitos.
- Navegação clara: sem páginas em construção, 404s frequentes, ou conteúdos vazios.
- Densidade de anúncios: planejar posições que não obstruam o conteúdo e não causem CLS (layout shift).

## Passo a Passo de Monetização

1. Preparar o site
   - Revisar branding (PlacarCerto), remover referências remanescentes a "bet".
   - Confirmar páginas: Privacidade, Termos, Sobre, Contato.
   - Garantir HTTPS em produção e performance aceitável (Lighthouse OK, imagens otimizadas).

2. Criar conta Google AdSense
   - Acesse https://www.google.com/adsense e inscreva-se.
   - Informe domínio/aplicação e dados fiscais conforme país.

3. Verificar propriedade (código do AdSense)
   - AdSense fornecerá um snippet para inserir no `<head>` (em produção). Exemplo (substitua `ca-pub-XXXXXXXXXXXXXXX`):

   ```html
   <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
   ```

4. ads.txt
   - Crie `ads.txt` na raiz pública do site (por exemplo, `/public/ads.txt` no deploy) com a linha do seu publisher ID:
   
   ```
   google.com, pub-XXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
   ```

5. Solicitar revisão
   - Após inserir o código, acesse o painel AdSense e solicite revisão do site.
   - Não altere significativamente o layout/conteúdo durante a revisão.

6. Configurar anúncios após aprovação
   - Ative "Auto ads" para testes rápidos e deixe o AdSense posicionar automaticamente.
   - Se preferir, crie blocos de anúncio (in-article, in-feed, display) e posicione manualmente em áreas não intrusivas.

7. Consentimento de usuários
   - Implemente uma CMP (Cookiebot/OneTrust) para exibir banner de consentimento e gerar a string TCF v2.
   - Garanta que o AdSense receba o estado de consentimento adequadamente.

8. Políticas contínuas e qualidade
   - Monitore o "Ad Review Center" para bloquear categorias sensíveis.
   - Mantenha conteúdo útil e original; evite práticas de clickbait.
   - Verifique métricas de UX (CLS, LCP, INP) para não penalizar entrega de anúncios.

## Tempo Estimado

- Preparação e ajustes: 1–2 dias.
- Revisão do AdSense: 3–14 dias (varia por região e backlog).
- Total típico: 1–3 semanas até exibir anúncios em produção.

## Checklist Rápido

- [ ] Remover qualquer incentivo/link a apostas.
- [ ] Privacidade, Termos, Sobre, Contato presentes.
- [ ] HTTPS ativo, PWA e performance ok.
- [ ] Snippet AdSense no `<head>` da build de produção.
- [ ] `ads.txt` com publisher ID no domínio.
- [ ] CMP/consentimento implementado (se aplicável).
- [ ] Densidade de anúncios moderada; sem obstruir conteúdo.

## Observações Finais

- Caso a monetização com AdSense seja negada por conteúdo sensível (gambling), mantenha monetização via planos premium e considere outras redes de anúncios que aceitem conteúdos esportivos com previsões — sempre respeitando a legislação local e políticas da plataforma.
- Re-avaliações podem ser feitas após ajustes; evite alterações bruscas durante processos de revisão.
