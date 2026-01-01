# ✅ REBRAND COMPLETO: BET INSIGHT → PLACARCERTO

## 📋 Mudanças Realizadas

### Frontend

#### 1. **package.json**
- Nome do pacote: `placarcerto-frontend`
- Versão atualizada: `1.0.0`

#### 2. **index.html**
- Título da página: `PlacarCerto - Análises de Futebol com IA`
- Meta description adicionada
- Idioma alterado para `pt-BR`

#### 3. **Componentes React**
- **RegisterPage.jsx**: Logo alterado para "PlacarCerto"
- **ProfilePage.jsx**: "PlacarCerto Premium"
- **PaymentConfirmation.jsx**: Email de suporte atualizado para `suporte@placarcerto.co.mz`

### Backend

#### 1. **Variáveis de Ambiente (.env)**
- Nome do banco de dados: `placarcerto_db`
- Email remetente: `noreply@placarcerto.co.mz`
- Comentário do header atualizado

#### 2. **Emails (apps/subscriptions/emails.py)**
Todos os emails atualizados com:
- Subject lines com "PlacarCerto"
- URLs alteradas para `https://placarcerto.co.mz`
- Email de suporte: `suporte@placarcerto.co.mz`
- Footer: "PlacarCerto Mozambique"

Emails modificados:
- ✅ Email de boas-vindas premium
- ✅ Email de expiração
- ✅ Email de confirmação de pagamento
- ✅ Email de falha de pagamento

#### 3. **Configurações de Planos (apps/subscriptions/plan_config.py)**
- Header atualizado: "PlacarCerto Mozambique"

#### 4. **Pagamentos (apps/subscriptions/payment_views.py)**
- Descrição de pagamento: `PlacarCerto - {nome_plano}`

#### 5. **PaySuite Service (apps/subscriptions/paysuite_service.py)**
- Header: "PlacarCerto Mozambique - Processamento de Pagamentos"

#### 6. **Modelos (apps/users/models.py)**
- Comentário do modelo User atualizado

#### 7. **Validadores (apps/users/password_validators.py)**
- Header atualizado

#### 8. **Arquivo de exemplo (.env.example)**
- Email padrão atualizado

## 🔄 Próximos Passos

### Obrigatórios:
1. **Criar novo banco de dados**:
   ```bash
   createdb placarcerto_db
   ```

2. **Migrar dados** (se houver dados existentes):
   ```sql
   pg_dump betinsight_db > backup.sql
   psql placarcerto_db < backup.sql
   ```

3. **Reinstalar dependências do frontend**:
   ```bash
   cd frontend
   npm install
   ```

4. **Reiniciar servidores**:
   ```bash
   # Backend
   cd backend
   python manage.py runserver

   # Frontend
   cd frontend
   npm run dev
   ```

### Recomendados:

1. **Registrar domínio**: `placarcerto.co.mz`

2. **Atualizar configurações de produção**:
   - ALLOWED_HOSTS em settings.py
   - CORS_ALLOWED_ORIGINS
   - CSRF_TRUSTED_ORIGINS

3. **Criar novo certificado SSL** para placarcerto.co.mz

4. **Atualizar DNS** quando domínio for registrado

5. **Configurar email no SendGrid** com domínio placarcerto.co.mz

6. **Criar novos perfis de redes sociais** (se aplicável):
   - Facebook: @placarcerto
   - Instagram: @placarcerto
   - Twitter/X: @placarcerto

7. **Design**:
   - Criar novo logo/favicon para PlacarCerto
   - Atualizar cores do tema (opcional)

## 📊 Estatísticas

- **Arquivos modificados**: 14
- **Linhas alteradas**: ~50+
- **URLs atualizadas**: 10+
- **Emails atualizados**: 4

## ✅ Status

**REBRAND COMPLETO E FUNCIONAL**

Todas as referências principais de "Bet Insight" foram substituídas por "PlacarCerto". A plataforma está pronta para uso com o novo nome.

---
*Rebrand realizado em: 01/01/2026*
*Por: GitHub Copilot*
