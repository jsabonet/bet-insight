# Informações pendentes para confirmar a integração VPay

## Contexto

O sistema só deve marcar uma encomenda como paga depois de confirmar o pagamento
no servidor, por uma resposta válida da VPay. O redirecionamento do cliente de
volta ao site, por si só, não confirma que o pagamento foi concluído.

Para implementar ou validar esse fluxo sem assumir detalhes da API, são
necessárias as confirmações abaixo diretamente da VPay.

## O que solicitar à VPay

1. **Host/base URL confirmado**
   - Host oficial da API para o ambiente que será utilizado.
   - Versão da API e indicação clara se o endereço é de produção ou sandbox.
   - Se houver sandbox, host e instruções para usá-lo sem criar cobranças reais.

2. **Exemplo de resposta ao criar um pedido**
   - Exemplo sem credenciais, tokens, dados pessoais ou outros segredos.
   - Incluir, se possível, o status HTTP, o corpo JSON e os campos que identificam
     o pedido e o URL de checkout.

3. **Exemplo de resposta ao consultar o estado de um pedido**
   - Exemplo sem credenciais, tokens, dados pessoais ou outros segredos.
   - Incluir, se possível, o status HTTP, o corpo JSON, os estados possíveis e
     qual campo representa a confirmação definitiva do pagamento.

## Respostas a preencher

Preencher esta secção somente com exemplos sanitizados fornecidos ou
confirmados pela VPay. Substituir valores reais identificáveis por marcadores.

### Host e ambiente

- **Ambiente:**
- **Host/base URL confirmado:**
- **Versão da API:**
- **Sandbox disponível:** sim / não / por confirmar

### Criação de pedido

- **Método e endpoint:**
- **Status HTTP:**
- **Resposta de exemplo:**

```json
{}
```

### Consulta do pedido

- **Método e endpoint:**
- **Status HTTP:**
- **Resposta de exemplo:**

```json
{}
```

- **Estado que confirma pagamento:**
- **Estados não pagos e respetivo significado:**

## Segurança

- **Não partilhar Client Secret, tokens de acesso, chaves ou segredos de webhook**
  no chat, neste documento, em exemplos, logs ou commits.
- Remover ou substituir também nomes, emails, telefones, identificadores de
  clientes e quaisquer dados pessoais antes de partilhar exemplos.
- Não usar exemplos incompletos ou não confirmados para tratar uma encomenda
  como paga.
- Até a VPay confirmar o host e o formato das respostas, não presumir endpoints,
  nomes de campos ou estados da API.
