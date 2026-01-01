import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  Search, 
  Filter,
  ArrowLeft,
  Shield,
  Edit,
  Trash2,
  MoreVertical,
  UserCheck,
  UserX,
  RefreshCw,
  CreditCard
} from 'lucide-react';
import Header from '../../components/Header';
import LoadingMascot from '../../components/LoadingMascot';
import BottomNav from '../../components/BottomNav';
import UserAvatar from '../../components/UserAvatar';
import EditUserModal from '../../components/EditUserModal';
import ManageSubscriptionModal from '../../components/ManageSubscriptionModal';
import { adminAPI } from '../../services/api';

export default function AdminUsers() {
  const { user, refreshProfile } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // all, premium, free
  const [message, setMessage] = useState({ type: '', text: '' });
  const [editingUser, setEditingUser] = useState(null);
  const [managingSubscription, setManagingSubscription] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);

  useEffect(() => {
    if (!user?.is_staff && !user?.is_superuser) {
      navigate('/');
      return;
    }
    loadUsers();
  }, [user, navigate, filterType, searchTerm]);

  const loadUsers = async () => {
    try {
      const params = {};
      if (filterType !== 'all') params.type = filterType;
      if (searchTerm) params.search = searchTerm;
      
      const response = await adminAPI.getUsers(params);
      // Handle paginated response or direct array
      const userData = response.data.results || response.data;
      setUsers(Array.isArray(userData) ? userData : []);
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
      setMessage({ type: 'error', text: 'Erro ao carregar usuários' });
    } finally {
      setLoading(false);
    }
  };

  const togglePremium = async (userId, currentStatus) => {
    setMessage({ type: '', text: '' });
    try {
      const response = await adminAPI.togglePremium(userId);
      setMessage({ type: 'success', text: response.data.message });
      loadUsers();
    } catch (error) {
      console.error('Erro ao alterar premium:', error);
      setMessage({ type: 'error', text: 'Erro ao alterar status premium' });
    }
  };

  const resetDailyLimit = async (userId) => {
    setMessage({ type: '', text: '' });
    try {
      const response = await adminAPI.resetDailyLimit(userId);
      setMessage({ type: 'success', text: response.data.message });
      loadUsers();
    } catch (error) {
      console.error('Erro ao resetar limite:', error);
      setMessage({ type: 'error', text: 'Erro ao resetar limite diário' });
    }
  };

  const deleteUser = async (userId) => {
    if (!window.confirm('Tem certeza que deseja excluir este usuário? Esta ação não pode ser desfeita.')) {
      return;
    }
    
    setMessage({ type: '', text: '' });
    try {
      const response = await adminAPI.deleteUser(userId);
      setMessage({ type: 'success', text: response.data.message });
      loadUsers();
    } catch (error) {
      console.error('Erro ao deletar usuário:', error);
      setMessage({ type: 'error', text: error.response?.data?.message || 'Erro ao deletar usuário' });
    }
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setShowEditModal(true);
  };

  const handleManageSubscription = (user) => {
    setManagingSubscription(user);
    setShowSubscriptionModal(true);
  };

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
    
    // Auto-clear message after 5 seconds
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  if (loading) {
    return (
      <div className="page-container">
        <Header title="Usuários" />
        <div className="page-content">
          <LoadingMascot message="Carregando usuários..." />
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header title="Gerenciar Usuários" subtitle={`${users.length} usuários`} />
      
      <div className="page-content">
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-6 btn-ghost"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar
        </button>

        {/* Message Alert */}
        {message.text && (
          <div
            className={`mb-6 p-4 rounded-xl border animate-slide-up ${
              message.type === 'success'
                ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800/50'
                : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800/50'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Search and Filter */}
        <div className="space-y-3 mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Buscar por nome ou email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10"
            />
          </div>

          <div className="flex gap-2 overflow-x-auto pb-2">
            {['all', 'premium', 'free'].map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-4 py-2 rounded-xl font-medium whitespace-nowrap transition-all ${
                  filterType === type
                    ? 'bg-primary-600 dark:bg-primary-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                {type === 'all' ? 'Todos' : type === 'premium' ? 'Premium' : 'Gratuito'}
              </button>
            ))}
          </div>
        </div>

        {/* Users List */}
        <div className="space-y-3">
          {users.map((u) => (
            <div key={u.id} className="card animate-slide-up">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <UserAvatar user={u} size="md" showBadge={true} />
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-bold text-gray-900 dark:text-gray-100">
                        {u.username}
                      </h3>
                      {u.is_premium && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-yellow-400 to-yellow-500 text-yellow-900 text-xs font-semibold rounded-full">
                          <Shield className="w-3 h-3 fill-current" />
                          Premium
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{u.email}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 mb-3 text-sm">
                <div>
                  <p className="text-gray-600 dark:text-gray-400">Telefone</p>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {u.phone || 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 dark:text-gray-400">Análises</p>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {u.total_analyses}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 dark:text-gray-400">Hoje</p>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {u.daily_analysis_count || 0}
                  </p>
                </div>
              </div>

              <div className="flex gap-2 pt-3 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => handleEditUser(u)}
                  className="flex-1 px-3 py-2 rounded-xl text-sm font-medium transition-all flex items-center justify-center gap-1 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30"
                  title="Editar usuário"
                >
                  <Edit className="w-4 h-4" />
                  Editar
                </button>

                <button
                  onClick={() => handleManageSubscription(u)}
                  className="flex-1 px-3 py-2 rounded-xl text-sm font-medium transition-all flex items-center justify-center gap-1 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/30"
                  title="Gerenciar assinatura"
                >
                  <CreditCard className="w-4 h-4" />
                  Plano
                </button>
                
                <button
                  onClick={() => resetDailyLimit(u.id)}
                  className="px-3 py-2 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-xl text-sm font-medium hover:bg-green-100 dark:hover:bg-green-900/30 transition-all"
                  title="Resetar limite diário"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
                
                <button
                  onClick={() => deleteUser(u.id)}
                  className="px-3 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl text-sm font-medium hover:bg-red-100 dark:hover:bg-red-900/30 transition-all"
                  title="Deletar usuário"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}

          {users.length === 0 && !loading && (
            <div className="card text-center py-12">
              <p className="text-gray-600 dark:text-gray-400">
                Nenhum usuário encontrado
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <EditUserModal
        user={editingUser}
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setEditingUser(null);
        }}
        onSuccess={handleModalSuccess}
      />

      <ManageSubscriptionModal
        user={managingSubscription}
        isOpen={showSubscriptionModal}
        onClose={() => {
          setShowSubscriptionModal(false);
          setManagingSubscription(null);
        }}
        onSuccess={handleModalSuccess}
      />

      <BottomNav />
    </div>
  );
}
