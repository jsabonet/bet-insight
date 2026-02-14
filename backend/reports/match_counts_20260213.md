# Resumo de Partidas Localizadas (2026-02-13)

- Banco de dados (apps.matches.models.Match): 3.104 partidas no total
  - Finalizadas: 2.950
- Dataset local de Copas: 450 partidas
  - Fonte: bet-insight/backend/ml_training/cup_training_dataset.json
- Dataset local de Ligas: 850 partidas
  - Fonte: bet-insight/backend/ml_training/training_dataset_checkpoint.json

Observações:
- Os valores de dataset foram lidos dos campos metadata.total_matches dos arquivos JSON.
- As contagens do banco foram obtidas via ORM Django.
