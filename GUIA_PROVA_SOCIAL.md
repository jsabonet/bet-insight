# Guia — Prova Social (Bilhetes para Redes Sociais)

Página **exclusiva de admin** que monta um bilhete válido a partir de partidas
**já realizadas**, pronto para captura de tela e publicação nas redes sociais.

- Rota frontend: `/admin/social-proof`
- Entrada no painel: card **Prova Social** em `/admin`
- Prefixo API: `/api/daily-bets/admin/social-proof/`
- Código: `apps/analysis/services/social_proof_builder.py`,
  `apps/analysis/services/match_result_sync.py`,
  `frontend/src/pages/admin/AdminSocialProof.jsx`

---

## ⚠️ Regras de conformidade (obrigatórias)

Estas regras estão implementadas no backend e **não** são apenas sugestões de UI.

1. **Nunca apresentar um bilhete pós-jogo como previsão.** Todo o snapshot de
   prova social é uma simulação montada depois de os resultados serem
   conhecidos, com aviso obrigatório.
2. **Simulação leva sempre aviso.** `kind=simulation` cria o snapshot com um
   `disclosure` obrigatório, e a API exige `confirm_simulation: true` no corpo
   do pedido.
3. **Aviso de jogo responsável** no rodapé da imagem (18+).
4. **Validação estrita.** Um bilhete só é considerado ganho quando *todas* as
   seleções têm resultado confirmado. Falta de resultado, jogo adiado ou
   mercado não suportado mantêm o bilhete **pendente** em vez de o inventar.

---

## 🎯 O modo único

| `kind` | O que é | Pode ser publicado como "acertámos"? |
|---|---|---|
| `simulation` | Bilhete composto **depois** de os resultados serem conhecidos, para demonstração | ❌ Nunca; leva aviso |

O único modo disponível é a simulação pós-jogo, usada apenas para demonstração
de produto e comunicação — nunca como previsão.

---

## 🔄 Fluxo automático (fim do dia)

Em `config/celery.py` (`CELERY_TIMEZONE = Africa/Maputo`):

| Tarefa | Horário | Papel |
|---|---|---|
| `analysis.sync_match_results` | 20:00 | Resultados das partidas da tarde |
| `analysis.sync_match_results` (`-late`) | 22:00 | Resultados das partidas da noite |
| `analysis.sync_match_results` (`-final`) | 23:30 | Fecho do dia + settle dos bilhetes |

Cada corrida regista uma `TaskExecution` (`sync_match_results`) visível no
admin de tarefas.

As tarefas **sincronizam resultados e liquidam bilhetes**, mas **não publicam
nada**: a aprovação e a captura de tela continuam a ser um ato manual do admin.

---

## 🖱️ Fluxo manual (UI)

1. Abrir `/admin/social-proof`.
2. Escolher a data (padrão: **ontem**, porque os resultados só ficam completos
   no dia seguinte).
3. Premir **Gerar candidatos**. Se não houver resultados sincronizados,
   usar **Sincronizar resultados** (chama o endpoint de sync) e repetir.
4. Escolher um candidato → **Criar snapshot**.
5. **Aprovar** o snapshot (obrigatório antes de exportar).
6. **Exportar imagem** (1080 px de largura, `html-to-image` → PNG) e copiar a
   legenda sugerida.
7. Publicar manualmente. O snapshot fica como `exported` com contagem de
   exportações e autor.

Snapshots **descartados** não podem ser aprovados; snapshots já exportados
podem ser reexportados (incrementa `export_count`).

---

## 🔌 Endpoints (todos `IsAdminUser`)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `.../candidates/?date=&kind=` | Lista candidatos para a data/modo |
| `GET` | `.../tickets/?date=&kind=&status=&limit=` | Histórico de snapshots |
| `GET` | `.../tickets/<id>/` | Detalhe do snapshot |
| `POST` | `.../generate/` | Cria (ou devolve) o snapshot; idempotente por `snapshot_hash` |
| `POST` | `.../tickets/<id>/approve/` | Aprova |
| `POST` | `.../tickets/<id>/export/` | Marca como exportado (exige `approved`/`exported`) |
| `POST` | `.../tickets/<id>/discard/` | Descarta |
| `POST` | `.../sync-results/` | Força sincronização de resultados + settle |

Corpo típico de `generate/`:

```json
{
  "date": "2026-01-15",
  "kind": "simulation",
  "snapshot_hash": "opcional — fixa um candidato específico",
  "confirm_simulation": true
}
```

Respostas de erro usadas pela UI: `400` (modo inválido, simulação sem
confirmação, exportar antes de aprovar, aprovar descartado), `403` (não admin),
`404` (snapshot inexistente ou `id` não numérico).

---

## 🧱 Modelo `SocialProofTicket`

Snapshot **imutável**: mantém as pernas, odds e códigos mesmo que os `DailyBet`
de origem sejam regenerados ou apagados.

- `kind`, `status` (`candidate` → `approved` → `exported`, ou `discarded`)
- `ticket_code`, `reserve_code`
- `legs` (JSON: `fixture_id`, `match`, `league`, `kickoff`, `market`,
  `market_label`, `pick`, `odd`, `probability`, `result`, `final_score`)
- `total_odd`, `combined_probability`, `stake_units`
- `disclosure`
- `snapshot_hash` (idempotência), `meta`
- `created_by`, `approved_by`, `last_exported_by`, `export_count`

Gestão em `/admin/` (Django admin) com ações **Aprovar** e **Descartar**; não é
possível criar snapshots manualmente pelo admin do Django.

---

## 🧪 Testes

```bash
cd backend
python manage.py test apps.analysis
```

Cobrem: permissões (anónimo/não admin), modos inválidos (incluindo os antigos
`verified_ticket` e `daily_hits`), obrigatoriedade da confirmação de simulação,
idempotência do `generate`, bloqueio de exportação antes da aprovação,
aprovação/exportação, descarte e validação estrita de `DailyBet`
(resultado ausente, jogo em curso, mercado não suportado).

---

## 📌 Limitações conhecidas

- Os resultados vêm da API-Football; sem sincronização não há candidatos.
- Bilhetes antigos podem ter o *fixture id* no campo `match_id`; o código tenta
  `fixture_id` → `api_fixture_id` → `match_id` (bilhetes novos gravam
  `api_fixture_id`).
- A imagem é gerada no browser (PNG a 1080 px); não há geração server-side.
- Mercados sem avaliação automática mantêm o bilhete pendente — é intencional.
