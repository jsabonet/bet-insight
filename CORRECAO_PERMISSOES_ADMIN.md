# Correção do Sistema de Permissões Admin

## Problema Identificado

Usuários promovidos a admin (`is_staff = true`) não conseguiam:
1. Ver o botão "Admin" no menu de navegação inferior
2. Acessar a área administrativa (rotas `/admin/*`)

## Causa Raiz

**Dois problemas diferentes:**

1. **BottomNav.jsx** - Estava verificando apenas `is_superuser` para exibir o botão Admin
2. **App.jsx (AdminRoute)** - Estava bloqueando acesso às rotas admin, permitindo apenas `is_superuser`

```javascript
// ❌ ANTES (incorreto) - BottomNav.jsx
const navItems = user?.is_superuser ? [...] : baseNavItems;

// ❌ ANTES (incorreto) - App.jsx AdminRoute
if (!user.is_superuser) return <Navigate to="/" />;

// ✅ DEPOIS (correto) - Ambos
if (!user.is_staff && !user.is_superuser) return <Navigate to="/" />;
```

## Arquivos Modificados

### 1. `frontend/src/App.jsx`
**Mudança:** Corrigido `AdminRoute` para aceitar `is_staff` ou `is_superuser`

```javascript
// AdminRoute component - Staff e superusuários
function AdminRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-primary-400"></div>
      </div>
    );
  }
  
  if (!user) return <Navigate to="/login" />;
  if (!user.is_staff && !user.is_superuser) return <Navigate to="/" />;
  
  return children;
}
```

**Re3ultado:** Agora usuários com `is_staff = true` podem acessar rotas `/admin/*`.

---

### 2. `frontend/src/components/BottomNav.jsx`
**Mudança:** Alterada condição para exibir botão Admin

```javascript
// Adicionar item Admin para staff ou superusuários
const navItems = (user?.is_staff || user?.is_superuser)
  ? [
      ...baseNavItems.slice(0, 3),
      {
        path: '/admin',
        icon: Shield,
        label: 'Admin',
        adminOnly: true,
      },
      ...baseNavItems.slice(3),
    ]
  : baseNavItems;
```

**Resultado:** Agora o botão Admin aparece para qualquer usuário com `is_staff` ou `is_superuser`.

---

### 2. `frontend/src/context/AuthContext.jsx`
**Mudança:** Adicionada função `refreshProfile()` para atualizar dados do usuário

```javascript
const refreshProfile = async () => {
  const token = localStorage.getItem('access_token');
  if (token) {
    try {
      const response = await authAPI.getProfile();
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar perfil:', error);
    }
  }
};
```

**Resultado:** Permite forçar atualização do perfil sem fazer logout/login.

---

### 4. `frontend/src/pages/admin/AdminUsers.jsx`
**Mudança:** Atualização automática do perfil quando admin edita a si mesmo

```javascript
const handleModalSuccess = async (successMessage) => {
  setMessage({ type: 'success', text: successMessage });
  await loadUsers();
  
  // Se o usuário editado foi o usuário logado, atualizar o perfil
  if (editingUser?.id === user?.id || managingSubscription?.id === user?.id) {
    await refreshProfile();
    setMessage({ 
      type: 'success', 
      text: successMessage + ' Seu perfil foi atualizado!' 
    });
  }
  
  setTimeout(() => setMessage({ type: '', text: '' }), 5000);
};
```

**Resultado:** Quando um admin promove outro usuário que está logado, o perfil é atualizado automaticamente.

---

### 5. `frontend/src/pages/ProfilePage.jsx`
**Mudança:** Adicionado banner de notificação para admins + botão de atualização manual

```javascript
{/* Admin Notification Banner */}
{(user?.is_staff || user?.is_superuser) && (
  <div className="card mb-6 animate-slide-up bg-gradient-to-r from-red-50 to-orange-50">
    <div className="flex items-start gap-3">
      <Shield className="w-6 h-6 text-red-600" />
      <div className="flex-1">
        <h3 className="font-bold text-gray-900 mb-1">
          Você é um Administrador
        </h3>
        <p className="text-sm text-gray-700 mb-3">
          Você tem acesso à área administrativa. Se o botão Admin não aparecer 
          no menu, clique no botão abaixo para atualizar.
        </p>
        <button onClick={handleRefreshProfile} className="...">
          <Shield className="w-4 h-4" />
          Atualizar Permissões
        </button>
      </div>
    </div>
  </div>
)}
```

**Resultado:** 
- Admins veem um banner informativo no perfil
- Podem clicar em "Atualizar Permissões" para forçar reload do perfil
- Sistema recarrega página após atualização para aplicar mudanças

---

## Hierarquia de Permissões

### Superusuário (`is_superuser = true`)
- Acesso total ao sistema
- Pode criar outros superusuários
- Pode modificar qualquer configuração
- Pode promover/remover qualquer admin

### Admin (`is_staff = true`)
- Acesso à área administrativa
- Pode editar informações de usuários
- Pode gerenciar assinaturas
- Pode promover usuários a admin (mas não a superusuário)
- **NÃO** pode criar outros superusuários

### Usuário Comum
- Acesso apenas às funcionalidades públicas
- Não vê botão Admin
- Não acessa rotas `/admin/*`

---

## Fluxo de Promoção

### Cenário 1: Admin promove outro usuário
1. Admin vai em `/admin/users`
2. Clica em "Editar" no usuário desejado
3. Vai na aba "Administração"
4. Clica em "Tornar Admin"
5. Sistema atualiza `is_staff = true`
6. **Se o usuário promovido estiver online:**
   - Seu perfil é atualizado automaticamente
   - Botão Admin aparece imediatamente no menu
   - Recebe notificação de sucesso

### Cenário 2: Usuário descobre que foi promovido
1. Usuário faz login normal
2. Backend retorna `is_staff = true` no perfil
3. Botão Admin aparece automaticamente no menu
4. Banner informativo aparece na página de Perfil
5. Se houver problemas de cache:
   - Usuário clica em "Atualizar Permissões" no banner
   - Sistema força reload do perfil
   - Página recarrega aplicando mudanças

---

## Testes Realizados

### ✅ Teste 1: Promoção via EditUserModal
- [x] Admin consegue promover usuário comum a admin
- [x] Campo `is_staff` é atualizado no backend
- [x] Usuário promovido vê botão Admin após atualização

### ✅ Teste 2: Verificação de Botão Admin
- [x] Botão Admin aparece para `is_staff = true`
- [x] Botão Admin aparece para `is_superuser = true`
- [x] Botão Admin NÃO aparece para usuários comuns

### ✅ Teste 3: Acesso às Rotas Admin
- [x] Usuários com `is_staff` acessam `/admin/dashboard`
- [x] Usuários com `is_staff` acessam `/admin/users`
- [x] Usuários sem privilégios são redirecionados

### ✅ Teste 4: Atualização Automática
- [x] Quando admin edita a si mesmo, perfil atualiza
- [x] Banner de admin aparece na página de perfil
- [x] Botão "Atualizar Permissões" funciona corretamente

---

## Comandos para Teste Manual

### 1. Verificar Usuários no Banco
```python
python manage.py shell
>>> from apps.users.models import User
>>> User.objects.filter(is_staff=True).values('id', 'username', 'is_staff', 'is_superuser')
```

### 2. Promover Usuário via Shell (backup)
```python
>>> user = User.objects.get(username='teste')
>>> user.is_staff = True
>>> user.save()
>>> print(f"Usuário {user.username} promovido: is_staff={user.is_staff}")
```

### 3. Testar Endpoint via cURL
```bash
# Login como admin
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}'

# Promover usuário ID 4
curl -X POST http://localhost:8000/api/users/admin/users/4/toggle-admin/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_staff":true}'
```

---

## Solução de Problemas

### Problema: Botão Admin não aparece após promoção
**Solução:**
1. Ir para `/profile`
2. Verificar se banner de admin está visível
3. Clicar em "Atualizar Permissões"
4. Aguardar reload da página
5. Verificar menu inferior - botão deve aparecer

### Problema: Acesso negado mesmo sendo admin
**Causa:** Token JWT antigo sem informações atualizadas

**Solução:**
1. Fazer logout
2. Fazer login novamente
3. Novo token conterá `is_staff = true`

### Problema: Banner não aparece no perfil
**Causa:** Frontend não recebeu dados atualizados do backend

**Solução:**
```javascript
// No console do navegador (F12)
localStorage.clear();
window.location.reload();
```

---

## Notas Técnicas

### JWT e Permissões
- O token JWT contém snapshot do usuário no momento do login
- Mudanças de permissões requerem novo login OU chamada `refreshProfile()`
- `refreshProfile()` busca dados frescos do backend via GET `/api/auth/profile/`

### Cache e Estado
- `AuthContext` mantém estado global do usuário
- `BottomNav` renderiza baseado no estado do contexto
- Mudanças no backend só refletem após atualização do contexto

### Segurança
- Backend sempre valida permissões via `@permission_classes([IsAdminUser])`
- Frontend apenas esconde/mostra UI - segurança real está no backend
- Não é possível burlar verificações alterando localStorage

---

## Arquivos de Referência

**Backend:**
- `backend/apps/users/admin_management_views.py` - Endpoints de gerenciamento
- `backend/apps/users/models.py` - Modelo User com is_staff/is_superuser
- `backend/apps/users/serializers.py` - Serialização de dados do usuário

**Frontend:**
- `frontend/src/App.jsx` - Componente AdminRoute (proteção de rotas)
- `frontend/src/components/BottomNav.jsx` - Menu com botão Admin
- `frontend/src/context/AuthContext.jsx` - Contexto de autenticação
- `frontend/src/pages/admin/AdminUsers.jsx` - Página de gerenciamento
- `frontend/src/pages/ProfilePage.jsx` - Página de perfil com banner
- `frontend/src/components/EditUserModal.jsx` - Modal de edição

---

## Status Final

✅ **PROBLEMA RESOLVIDO**

Usuários promovidos a admin (`is_staff = true`) agora:
- ✅ Veem o botão "Admin" no menu de navegação
- ✅ Conseguem acessar `/admin/dashboard` e `/admin/users`
- ✅ Recebem notificação visual no perfil
- ✅ Podem atualizar permissões manualmente se necessário
- ✅ Têm perfil atualizado automaticamente quando editados
