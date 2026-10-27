# Web Push

As notificações usam Web Push com VAPID e assinaturas independentes por dispositivo.
O envio só é ativado quando as chaves VAPID estão configuradas.

## Configuração

1. Instale as dependências do backend com `pip install -r requirements.txt`.
2. Gere um par de chaves com `python manage.py generate_vapid_keys`.
3. Configure `WEBPUSH_VAPID_PUBLIC_KEY` no backend e `WEBPUSH_VAPID_PRIVATE_KEY` como segredo no ambiente. O frontend obtém a chave pública do endpoint autenticado de estado.
4. Defina `WEBPUSH_VAPID_SUBJECT` como um endereço de contato, por exemplo `mailto:suporte@placarcerto.digital`.
5. Execute `python manage.py migrate` e reinicie o backend, Celery Worker e Celery Beat.
6. Garanta que o Celery Beat está ativo para executar os agendamentos.

Não versione chaves privadas nem as inclua em imagens ou logs. A chave pública é retornada pelo endpoint autenticado `/api/users/push/status/`.

## Funcionamento

- O utilizador ativa push no perfil e concede permissão no navegador.
- A assinatura do navegador é guardada por usuário e endpoint/dispositivo.
- `Analysis` criada dispara uma notificação “Análise pronta”.
- A cada cinco minutos, Celery procura partidas analisadas que começam em cerca de uma hora e envia um lembrete deduplicado.
- A cada cinco minutos, Celery consulta eventos de partidas ao vivo da API-Football, limitado a partidas analisadas com utilizadores inscritos em eventos. Envia golos/penáltis, cartões amarelos/vermelhos, substituições e VAR; identifica lesão apenas quando o feed descreve essa causa. Cada evento é deduplicado por assinatura.
- A API-Football é consultada uma vez para obter partidas ao vivo e uma vez por cada partida analisada ao vivo. O consumo cresce com o número de partidas acompanhadas; confirme o limite do plano contratado.
- Quando a geração diária cria bilhetes, contas Premium com assinatura ativa e push ligado recebem um resumo único do dia, com a contagem de múltiplos e value bets e ligação para `/daily-bets`. A preferência “Bilhetes automáticos Premium” pode ser desligada no perfil.
- Quando um novo utilizador é associado a um afiliado, é enviado um alerta de referência. Quando um pagamento atribuído ao afiliado é confirmado, é enviado um alerta de comissão pendente. A comissão também gera alertas quando fica disponível e quando é marcada como paga.
- Contas administrativas ativas (`is_staff` ou `is_superuser`) com push ativado e uma assinatura de navegador ativa recebem alertas de novas vendas confirmadas e checkouts VPay pendentes há pelo menos uma hora. O Celery Beat reconcilia esses eventos a cada cinco minutos; falhas de email e push são repetidas independentemente.
- O perfil permite ativar/desativar separadamente os eventos das partidas e as notificações de afiliado. Os controlos aplicam-se a todas as assinaturas ativas da conta.
- Assinaturas expiradas (HTTP 404/410) são removidas automaticamente.
- Desativar push no perfil impede envios para todas as assinaturas daquele usuário.

Push requer contexto seguro (HTTPS em produção; `localhost` é permitido para desenvolvimento) e um navegador compatível. Sem chaves VAPID, o perfil informa que o serviço ainda não está configurado.

Para receber os alertas administrativos, configure as duas chaves VAPID no
backend, mantenha Celery Worker e Celery Beat ativos, e ative push em cada
navegador usado por uma conta administrativa. Os emails usam o backend
transacional configurado (`RESEND_API_KEY` em produção).