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
   `disclosure` obrigatório, incluído na imagem exportada.
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
4. Escolher um candidato → **Criar**.
   O campo **Valor da aposta** aceita qualquer valor em meticais a partir de
   **MT 5** e é aplicado 1:1 na imagem (sem multiplicadores). Depois de escrever
   o valor, premir **Aplicar** para validar e gravar no snapshot; o botão fica
   desativado enquanto o valor não mudar. Também é possível ajustar o valor de
   um snapshot já criado.
5. **Aprovar** o snapshot (obrigatório antes de exportar).
6. **Exportar imagem** (1080 px de largura, `html-to-image` → PNG) e copiar a
   legenda sugerida. Se existir um valor por aplicar, a exportação pede primeiro
   **Aplicar**.
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
| `POST`/`PATCH` | `.../tickets/<id>/stake/` | Valida e grava o valor da aposta (MT) no snapshot |
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
  "stake_amount": 10
}
```

`stake_amount` (valor da aposta **em meticais**, aplicado 1:1 no bilhete) aceita
qualquer valor a partir de **5** e fica gravado no snapshot; `stake_units`
continua aceite como alias por compatibilidade e o serializer devolve ambos
(`stake_units` e `stake_amount`) mais `potential_return` já calculado. O endpoint
`tickets/<id>/stake/` permite ajustar o valor de um snapshot já criado.

Respostas de erro usadas pela UI: `400` (modo inválido, valor de aposta abaixo
do mínimo, exportar antes de aprovar, aprovar descartado), `403` (não admin),
`404` (snapshot inexistente ou `id` não numérico).

---

## 🧱 Modelo `SocialProofTicket`

Snapshot **imutável**: mantém as pernas, odds e códigos mesmo que os `DailyBet`
de origem sejam regenerados ou apagados.

- `kind`, `status` (`candidate` → `approved` → `exported`, ou `discarded`)
- `ticket_code` (9 dígitos, começa sempre por `7`), `reserve_code` (`BW7` + 7
  caracteres). Ambos derivam do `snapshot_hash`, pelo que o mesmo snapshot gera
  sempre os mesmos códigos.
- `legs` (JSON: `fixture_id`, `match`, `league`, `kickoff`, `market`,
  `market_label`, `pick`, `odd`, `probability`, `result`, `final_score`)
- `total_odd`, `combined_probability`, `stake_units`/`stake_amount` (valor em MT)
  e `potential_return` (valor × odd total)
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
`verified_ticket` e `daily_hits`), geração de simulação sem confirmação extra,
valor da aposta (persistência e mínimo de MT 5), idempotência do
`generate`, bloqueio de exportação antes da aprovação,
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
