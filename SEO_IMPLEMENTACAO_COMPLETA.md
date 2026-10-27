# SEO do PlacerCerto

## Estado atual

- O frontend define título, descrição, canonical, Open Graph, Twitter Cards e
  dados JSON-LD via `react-helmet-async`.
- O canonical gerado automaticamente usa o caminho da página no domínio
  canónico e ignora query strings e fragmentos.
- A landing page descreve o produto sem métricas de utilizadores, volume de
  análises ou taxa de acerto que não estejam verificadas.
- O sitemap inclui apenas as rotas públicas existentes: `/`, `/about`, `/faq`,
  `/terms`, `/privacy` e `/affiliate/terms`.
- `robots.txt` aponta para o sitemap usando `FRONTEND_URL` e exclui endpoints
  da API e páginas da aplicação que exigem autenticação.
- A imagem social `frontend/public/og-image.png` existe em 1200 x 630. Os
  metadados Schema.org usam o logo existente em `frontend/public/logo-email.png`.
- O manifest PWA usa idioma `pt-MZ` e não declara ícones ou capturas de ecrã
  que não estejam presentes em `frontend/public/`.

## Limitações conhecidas

O frontend é uma SPA sem renderização no servidor nem pré-renderização. O
`index.html` contém os metadados estáticos da landing page; metadados
específicos de outras rotas só são aplicados depois da execução do JavaScript.
Alguns robôs de pesquisa conseguem renderizar JavaScript, mas pré-visualizadores
de redes sociais e outros crawlers podem não o fazer. Para SEO consistente por
página, a próxima melhoria arquitetural é adicionar pré-renderização ou SSR às
páginas públicas.

As páginas de partidas e áreas de utilizador exigem autenticação e, por isso,
não são publicadas no sitemap. Só devem ser adicionadas se passarem a ter uma
versão pública e indexável.

## Verificação local

```powershell
cd backend
python manage.py test apps.seo --keepdb
cd ..\frontend
npm run build
```

Após deploy, confirme que `/robots.txt`, `/sitemap.xml`, `/og-image.png` e
`/logo-email.png` respondem com sucesso no domínio público. Submeta o sitemap
no Google Search Console e no Bing Webmaster Tools e acompanhe indexação,
impressões e cliques; alterações no código não garantem posições de pesquisa.
