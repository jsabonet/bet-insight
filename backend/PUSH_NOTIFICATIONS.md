# Web Push

As notificações usam Web Push com VAPID e assinaturas independentes por dispositivo.
O envio só é ativado quando as chaves VAPID estão configuradas.

## Configuração

1. Instale as dependências do backend com `pip install -r requirements.txt`.
2. Gere um par de chaves com `python manage.py generate_vapid_keys`.
3. Configure `WEBPUSH_VAPID_PUBLIC_KEY` no backend e `WEBPUSH_VAPID_PRIVATE_KEY` como segredo no ambiente. O frontend obtém a chave pública do endpoint autenticado de estado.
4. Defina `WEBPUSH_VAPID_SUBJECT` como um endereço de contato, por exemplo `mailto:suporte@placarcerto.digital`.
5. Execute `python manage.py migrate` e reinicie o backend, Celery Worker e Celery Beat.
6. Garanta que o agendamento `send-analyzed-match-reminders` foi sincronizado. Em produção, execute `python manage.py sync_match_preview_schedule` após a migração.

Não versione chaves privadas nem as inclua em imagens ou logs. A chave pública é retornada pelo endpoint autenticado `/api/users/push/status/`.

## Funcionamento

- O utilizador ativa push no perfil e concede permissão no navegador.
- A assinatura do navegador é guardada por usuário e endpoint/dispositivo.
- `Analysis` criada dispara uma notificação “Análise pronta”.
- A cada cinco minutos, Celery procura partidas analisadas que começam em cerca de uma hora e envia um lembrete deduplicado.
- Assinaturas expiradas (HTTP 404/410) são removidas automaticamente.
- Desativar push no perfil impede envios para todas as assinaturas daquele usuário.

Push requer contexto seguro (HTTPS em produção; `localhost` é permitido para desenvolvimento) e um navegador compatível. Sem chaves VAPID, o perfil informa que o serviço ainda não está configurado.