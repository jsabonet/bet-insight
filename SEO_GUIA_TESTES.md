# 🧪 GUIA DE TESTES - SEO PlacerCerto

## Testes Locais (Antes de Deploy)

### 1. Verificar Robots.txt
```bash
# Abrir no navegador:
http://localhost:8000/robots.txt
```

**Resultado Esperado:**
```
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
...
Sitemap: https://placarcerto.digital/sitemap.xml
```

---

### 2. Verificar Sitemap.xml
```bash
# Abrir no navegador:
http://localhost:8000/sitemap.xml
```

**Resultado Esperado:** XML com links para:
- `/sitemap-static.xml`
- `/sitemap-matches.xml`
- `/sitemap-leagues.xml`
- `/sitemap-teams.xml`
- `/sitemap-analyses.xml`

**Testar sitemap específico:**
```bash
http://localhost:8000/sitemap-matches.xml
```

---

### 3. Verificar Meta Tags na HomePage
```bash
# Abrir no navegador:
http://localhost:5173/

# No DevTools (F12), verificar no <head>:
```

**Checklist:**
- [ ] `<title>PlacerCerto - Análise Inteligente de Futebol com IA</title>`
- [ ] `<meta name="description" content="...">`
- [ ] `<meta name="keywords" content="...">`
- [ ] `<meta property="og:title" content="...">`
- [ ] `<meta property="og:image" content="...">`
- [ ] `<meta name="twitter:card" content="summary_large_image">`
- [ ] `<link rel="canonical" href="https://placarcerto.digital/">`
- [ ] `<script type="application/ld+json">` (JSON-LD)

---

### 4. Verificar JSON-LD Structured Data
```bash
# No DevTools (F12), Console:
document.querySelectorAll('script[type="application/ld+json"]').forEach(s => console.log(JSON.parse(s.textContent)))
```

**Resultado Esperado:**
```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": [...]
}
```

---

### 5. Teste de Performance (Local)
```bash
# No DevTools > Lighthouse:
- Gerar relatório
```

**Métricas Alvo:**
- Performance: > 85 (local pode ser mais baixo)
- Accessibility: > 95
- Best Practices: > 95
- SEO: 100 ⭐

---

## Testes de Produção (Após Deploy)

### 1. Google Rich Results Test
**URL:** https://search.google.com/test/rich-results

**Passos:**
1. Inserir URL: `https://placarcerto.digital/`
2. Clicar em "Test URL"
3. Aguardar análise

**Resultado Esperado:**
- ✅ Organization detected
- ✅ WebSite detected
- ✅ ItemList detected (se houver partidas)

**Testar partida específica:**
```
https://placarcerto.digital/matches/123
```
- ✅ SportsEvent detected

---

### 2. Facebook Sharing Debugger
**URL:** https://developers.facebook.com/tools/debug/

**Passos:**
1. Inserir URL: `https://placarcerto.digital/`
2. Clicar em "Debug"
3. Se necessário, clicar em "Scrape Again"

**Resultado Esperado:**
- ✅ Imagem: 1200x630px
- ✅ Título: "PlacerCerto - Análise Inteligente..."
- ✅ Descrição: "Previsões precisas..."
- ✅ Preview renderizado corretamente

---

### 3. Twitter Card Validator
**URL:** https://cards-dev.twitter.com/validator

**Passos:**
1. Inserir URL: `https://placarcerto.digital/`
2. Clicar em "Preview card"

**Resultado Esperado:**
- ✅ Card type: Summary Large Image
- ✅ Imagem exibida
- ✅ Título e descrição corretos

---

### 4. Google PageSpeed Insights
**URL:** https://pagespeed.web.dev/

**Passos:**
1. Inserir URL: `https://placarcerto.digital/`
2. Clicar em "Analyze"
3. Aguardar resultados (Mobile + Desktop)

**Métricas Alvo (Mobile):**
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 95
- SEO: 100 ⭐

**Core Web Vitals:**
- LCP (Largest Contentful Paint): < 2.5s 🟢
- FID (First Input Delay): < 100ms 🟢
- CLS (Cumulative Layout Shift): < 0.1 🟢

---

### 5. Schema.org Validator
**URL:** https://validator.schema.org/

**Passos:**
1. Inserir URL: `https://placarcerto.digital/`
2. Clicar em "Run Test"

**Resultado Esperado:**
- ✅ No errors
- ✅ Organization schema válido
- ✅ WebSite schema válido

---

### 6. Teste de Mobile-Friendliness
**URL:** https://search.google.com/test/mobile-friendly

**Passos:**
1. Inserir URL: `https://placarcerto.digital/`
2. Clicar em "Test URL"

**Resultado Esperado:**
- ✅ "Page is mobile-friendly"
- ✅ Screenshot do mobile renderizado
- ✅ Sem problemas de usabilidade

---

### 7. SSL/HTTPS Check
**URL:** https://www.ssllabs.com/ssltest/

**Passos:**
1. Inserir domínio: `placarcerto.digital`
2. Clicar em "Submit"
3. Aguardar análise completa

**Resultado Esperado:**
- ✅ Grade A ou A+
- ✅ Certificado válido
- ✅ TLS 1.2+ habilitado

---

### 8. Sitemap Validation
**URL:** https://www.xml-sitemaps.com/validate-xml-sitemap.html

**Passos:**
1. Inserir URL: `https://placarcerto.digital/sitemap.xml`
2. Clicar em "Validate"

**Resultado Esperado:**
- ✅ No errors
- ✅ Todas as URLs acessíveis (status 200)
- ✅ Formato XML válido

---

## Submissão aos Motores de Busca

### 1. Google Search Console

**URL:** https://search.google.com/search-console

**Passos:**
1. Adicionar propriedade: `https://placarcerto.digital`
2. Verificar propriedade (DNS, HTML tag ou Google Analytics)
3. Ir em "Sitemaps"
4. Adicionar sitemap: `https://placarcerto.digital/sitemap.xml`
5. Clicar em "Submit"

**Monitorar:**
- Cobertura: Páginas indexadas vs. não indexadas
- Core Web Vitals: URLs com problemas
- Experiência de página
- Links internos/externos

---

### 2. Bing Webmaster Tools

**URL:** https://www.bing.com/webmasters

**Passos:**
1. Adicionar site: `https://placarcerto.digital`
2. Verificar propriedade (XML file ou BingSiteAuth)
3. Ir em "Sitemaps"
4. Submeter sitemap: `https://placarcerto.digital/sitemap.xml`

---

### 3. Yandex Webmaster

**URL:** https://webmaster.yandex.com/

**Passos:**
1. Adicionar site
2. Verificar propriedade
3. Submeter sitemap

---

## Comandos Úteis (Terminal)

### Verificar status do servidor
```bash
curl http://localhost:8000/robots.txt
curl http://localhost:8000/sitemap.xml
```

### Verificar meta tags de uma página
```bash
curl -s http://localhost:5173/ | grep -E '<title>|<meta name=|<meta property='
```

### Verificar JSON-LD
```bash
curl -s http://localhost:5173/ | grep -A 50 'application/ld+json'
```

---

## Checklist Final

### Antes do Deploy:
- [ ] Servidor backend rodando sem erros
- [ ] Frontend compilando sem warnings
- [ ] Robots.txt acessível
- [ ] Sitemap.xml acessível
- [ ] Meta tags visíveis no HTML source
- [ ] JSON-LD presente no source
- [ ] Imagens OG criadas (1200x630px)
- [ ] Canonical URLs corretos

### Após Deploy:
- [ ] Robots.txt público acessível
- [ ] Sitemap.xml público acessível
- [ ] Google Rich Results Test: ✅
- [ ] Facebook Debugger: ✅
- [ ] Twitter Card Validator: ✅
- [ ] PageSpeed Insights: Score > 90
- [ ] Mobile-Friendly Test: ✅
- [ ] Sitemap submetido ao Google
- [ ] Sitemap submetido ao Bing
- [ ] Google Analytics configurado
- [ ] Google Tag Manager configurado

---

## Troubleshooting

### Problema: Sitemap retorna 404
**Solução:**
```bash
# Verificar se app 'seo' está em INSTALLED_APPS
# Verificar se django.contrib.sitemaps está instalado
python manage.py showmigrations
```

### Problema: Robots.txt não carrega
**Solução:**
```bash
# Verificar URL pattern em config/urls.py
# Testar endpoint diretamente
curl http://localhost:8000/robots.txt
```

### Problema: Meta tags não aparecem no source
**Solução:**
```bash
# Verificar se HelmetProvider está no App.jsx
# Verificar se react-helmet-async está instalado
npm list react-helmet-async
```

### Problema: JSON-LD inválido
**Solução:**
```javascript
// Validar JSON em https://jsonlint.com/
// Verificar se structuredData está sendo passado corretamente
console.log(JSON.stringify(structuredData, null, 2))
```

---

## Monitoramento Contínuo

### Semanalmente:
- [ ] Verificar Google Search Console
  - Novas páginas indexadas
  - Erros de cobertura
  - Core Web Vitals
- [ ] Verificar Bing Webmaster Tools
- [ ] Revisar keywords no Google Analytics

### Mensalmente:
- [ ] Executar PageSpeed Insights
- [ ] Verificar posições no Google (Search Console)
- [ ] Analisar tráfego orgânico (Google Analytics)
- [ ] Revisar e atualizar meta descriptions
- [ ] Adicionar novo conteúdo (blog posts)

---

**Status:** 🚀 Pronto para testes e deploy  
**Última atualização:** 23 de Janeiro de 2026
