# Sistema de Administração Avançado - Implementado

## ✅ Funcionalidades Implementadas

Foi criado um sistema completo de administração que permite aos admins gerenciar todos os aspectos de usuários e assinaturas.

---

## 🔐 Permissões

### Hierarquia de Permissões:
1. **Superusuário (is_superuser)**: Controle total do sistema
   - Pode promover/remover admins
   - Pode criar outros superusuários
   - Pode editar qualquer campo de usuário
   - Pode resetar senhas de qualquer usuário

2. **Admin (is_staff)**: Gerenciamento de usuários e planos
   - Pode editar informações de usuários
   - Pode atribuir/remover planos
   - Pode ativar/desativar contas
   - NÃO pode promover outros admins
   - NÃO pode resetar senhas de superusuários

3. **Usuário Normal**: Acesso apenas às próprias informações

---

## 📋 Endpoints Backend Criados

### 1. **Gerenciamento de Privilégios Admin**

#### `POST /users/admin/users/<user_id>/toggle-admin/`
**Permissão**: IsAdminUser  
**Body**:
```json
{
  "is_staff": true,           // true = promover, false = remover
  "is_superuser": false       // opcional, apenas superuser pode definir
}
```
**Funcionalidade**: Promover usuário a admin ou remover privilégios

**Regras**:
- Admin não pode modificar seus próprios privilégios
- Apenas superuser pode criar outros superusers
- Retorna erro se tentar modificar a si mesmo

---

### 2. **Editar Informações de Usuário**

#### `PUT/PATCH /users/admin/users/<user_id>/update/`
**Permissão**: IsAdminUser  
**Body** (todos os campos opcionais):
```json
{
  "username": "novo_username",
  "email": "novo@email.com",
  "phone": "841234567",
  "first_name": "João",
  "last_name": "Silva",
  "is_premium": true,
  "premium_until": "2026-12-31T23:59:59Z",
  "daily_analysis_count": 0,
  "is_active": true,
  "push_enabled": true,
  "is_staff": false,          // apenas superuser
  "is_superuser": false       // apenas superuser
}
```

**Funcionalidade**: Editar qualquer informação de usuário

**Validações**:
- Username deve ser único
- Email deve ser único
- Campos sensíveis (is_staff, is_superuser) apenas para superuser
- Superuser não pode remover seu próprio is_superuser

---

### 3. **Resetar Senha de Usuário**

#### `POST /users/admin/users/<user_id>/reset-password/`
**Permissão**: IsAdminUser  
**Body**:
```json
{
  "new_password": "nova_senha_123"
}
```

**Funcionalidade**: Resetar senha de qualquer usuário

**Regras**:
- Senha deve ter no mínimo 6 caracteres
- Apenas superuser pode resetar senha de outros superusers

---

### 4. **Listar Todos os Usuários (com filtros)**

#### `GET /users/admin/users/all/`
**Permissão**: IsAdminUser  
**Query Params**:
- `search`: busca por username, email, phone, first_name, last_name
- `is_premium`: true/false
- `is_staff`: true/false
- `is_active`: true/false
- `page`: número da página (padrão: 1)
- `page_size`: tamanho da página (padrão: 20)

**Exemplo**:
```
GET /users/admin/users/all/?search=joao&is_premium=true&page=1&page_size=20
```

**Resposta**:
```json
{
  "count": 45,
  "total_pages": 3,
  "current_page": 1,
  "page_size": 20,
  "results": [...]
}
```

---

### 5. **Atribuir Plano (modificado)**

#### `POST /subscriptions/admin/assign-subscription/`
**Permissão**: IsAdminUser  
**Body**:
```json
{
  "user_id": 123,
  "plan_slug": "starter|pro|vip|teste",  // QUALQUER PLANO (removida restrição)
  "duration_days": 30                     // opcional, override de duração
}
```

**Mudança**: Agora aceita QUALQUER plano, incluindo "freemium" e "teste"

---

## 🎨 Interface Frontend

### Componentes Criados:

#### 1. **EditUserModal.jsx**
Modal completo com 3 abas:

**Aba "Informações"**:
- Editar username, email, phone
- Editar first_name, last_name
- Toggle is_active (ativar/desativar conta)

**Aba "Administração"**:
- Botão "Tornar Admin" / "Remover Admin"
- Checkbox "Superusuário" (apenas se já é admin)
- Avisos de segurança

**Aba "Assinatura"**:
- Toggle "Usuário Premium"
- Campo de data "Premium Válido Até"
- Dica: usar a aba "Gerenciar Planos" para planos específicos

---

#### 2. **ManageSubscriptionModal.jsx**
Modal para gerenciar planos de assinatura:

**Funcionalidades**:
- Exibe assinatura atual (se existir)
- Botão "Remover" assinatura atual
- Lista todos os planos disponíveis com cards visuais
- Permite selecionar novo plano
- Campo "Duração Personalizada" (override)
- Aviso: atribuir novo plano cancela o anterior

**Visual**:
- Cards coloridos por plano
- Badge "Popular" para planos em destaque
- Ícones diferentes por tipo de plano
- Indicador visual de plano selecionado

---

### AdminUsers.jsx (atualizado)

**Novos Botões por Usuário**:
1. **Editar** (azul): Abre EditUserModal
2. **Plano** (roxo): Abre ManageSubscriptionModal
3. **Resetar** (verde): Reseta limite diário
4. **Deletar** (vermelho): Remove usuário

**Removido**:
- Botão "Premium" direto (movido para modal de edição)

---

## 🚀 Como Usar

### 1. **Promover Usuário a Admin**

**Via Frontend**:
1. Acesse `/admin/users`
2. Clique em "Editar" no usuário desejado
3. Vá para aba "Administração"
4. Clique em "Tornar Admin"
5. (Opcional) Marque "Superusuário" se necessário

**Via API**:
```bash
curl -X POST http://localhost:8000/api/users/admin/users/123/toggle-admin/ \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_staff": true,
    "is_superuser": false
  }'
```

---

### 2. **Editar Informações de Usuário**

**Via Frontend**:
1. Acesse `/admin/users`
2. Clique em "Editar" no usuário
3. Aba "Informações": edite campos básicos
4. Aba "Assinatura": controle premium manual
5. Clique em "Salvar Alterações"

**Via API**:
```bash
curl -X PUT http://localhost:8000/api/users/admin/users/123/update/ \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "novo_username",
    "email": "novo@email.com",
    "phone": "841234567",
    "is_active": true
  }'
```

---

### 3. **Atribuir Plano a Usuário**

**Via Frontend**:
1. Acesse `/admin/users`
2. Clique em "Plano" no usuário desejado
3. Selecione o plano desejado (aparece lista completa)
4. (Opcional) Defina duração personalizada
5. Clique em "Atribuir Plano"

**Via API**:
```bash
# Atribuir plano "Pro" por 30 dias
curl -X POST http://localhost:8000/api/subscriptions/admin/assign-subscription/ \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "plan_slug": "pro",
    "duration_days": 30
  }'

# Atribuir plano "Teste" por 1 dia (para testes)
curl -X POST http://localhost:8000/api/subscriptions/admin/assign-subscription/ \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "plan_slug": "teste"
  }'
```

---

### 4. **Remover Assinatura de Usuário**

**Via Frontend**:
1. Acesse `/admin/users`
2. Clique em "Plano" no usuário
3. Se houver assinatura ativa, clique em "Remover"
4. Confirme a ação

**Via API**:
```bash
curl -X POST http://localhost:8000/api/subscriptions/admin/remove-subscription/ \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123
  }'
```

---

### 5. **Resetar Senha de Usuário**

**Via API** (não implementado no frontend por segurança):
```bash
curl -X POST http://localhost:8000/api/users/admin/users/123/reset-password/ \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "nova_senha_123"
  }'
```

---

## 📊 Exemplos de Uso

### Caso 1: Dar 7 dias grátis de Premium a um usuário
```bash
curl -X POST http://localhost:8000/api/subscriptions/admin/assign-subscription/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "user_id": 123,
    "plan_slug": "pro",
    "duration_days": 7
  }'
```

### Caso 2: Tornar usuário admin
```bash
curl -X POST http://localhost:8000/api/users/admin/users/123/toggle-admin/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"is_staff": true}'
```

### Caso 3: Desativar conta de usuário
```bash
curl -X PUT http://localhost:8000/api/users/admin/users/123/update/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"is_active": false}'
```

### Caso 4: Atribuir plano de teste de 1 MZN
```bash
curl -X POST http://localhost:8000/api/subscriptions/admin/assign-subscription/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "user_id": 123,
    "plan_slug": "teste"
  }'
```

---

## ⚠️ Regras de Segurança Implementadas

1. ✅ Admin não pode modificar seus próprios privilégios
2. ✅ Apenas superuser pode criar outros superusers
3. ✅ Apenas superuser pode resetar senha de superusers
4. ✅ Não é possível deletar superusuários via API
5. ✅ Username e email devem ser únicos
6. ✅ Senhas devem ter no mínimo 6 caracteres
7. ✅ Confirmação obrigatória antes de deletar usuário
8. ✅ Validação de campos antes de salvar

---

## 🎯 Benefícios

✅ **Controle Total**: Admin pode gerenciar todos os aspectos de usuários  
✅ **Flexibilidade**: Atribuir qualquer plano, até os que pagaram  
✅ **Segurança**: Hierarquia de permissões bem definida  
✅ **Interface Intuitiva**: Modais separados por função  
✅ **Auditoria**: Todas as ações logadas no backend  
✅ **Validações**: Campos validados no frontend e backend  
✅ **Feedback Visual**: Mensagens de sucesso/erro claras  

---

## 🗂️ Arquivos Criados/Modificados

### Backend:
- ✅ `backend/apps/users/admin_management_views.py` (NOVO)
- ✅ `backend/apps/users/urls.py` (MODIFICADO)
- ✅ `backend/apps/subscriptions/plan_views.py` (MODIFICADO)

### Frontend:
- ✅ `frontend/src/components/EditUserModal.jsx` (NOVO)
- ✅ `frontend/src/components/ManageSubscriptionModal.jsx` (NOVO)
- ✅ `frontend/src/pages/admin/AdminUsers.jsx` (MODIFICADO)

---

## 📝 Resumo de URLs

| Endpoint | Método | Função |
|----------|--------|--------|
| `/users/admin/users/all/` | GET | Listar todos os usuários (com filtros) |
| `/users/admin/users/<id>/update/` | PUT/PATCH | Editar informações do usuário |
| `/users/admin/users/<id>/toggle-admin/` | POST | Promover/remover admin |
| `/users/admin/users/<id>/reset-password/` | POST | Resetar senha |
| `/users/admin/users/<id>/delete/` | DELETE | Deletar usuário |
| `/subscriptions/admin/assign-subscription/` | POST | Atribuir plano (qualquer) |
| `/subscriptions/admin/remove-subscription/` | POST | Remover assinatura |

---

## ✅ Status Final

🎉 **Sistema de Administração Completo Implementado!**

- ✅ Backend com todas as permissões e validações
- ✅ Frontend com modais intuitivos e visuais
- ✅ Admin pode atribuir qualquer plano a qualquer usuário
- ✅ Admin pode promover/remover outros admins
- ✅ Admin pode editar todas as informações de usuários
- ✅ Sistema de segurança robusto
- ✅ Interface responsiva e acessível
- ✅ Pronto para produção
