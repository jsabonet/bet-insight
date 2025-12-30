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
  UserX
} from 'lucide-react';
import Header from '../../components/Header';
import LoadingMascot from '../../components/LoadingMascot';
import BottomNav from '../../components/BottomNav';
import UserAvatar from '../../components/UserAvatar';

export default function AdminUsers() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // all, premium, free

  useEffect(() => {
    if (!user?.is_staff && !user?.is_superuser) {
      navigate('/');
      return;
    }
    loadUsers();
  }, [user, navigate]);

  const loadUsers = async () => {
    try {
      // TODO: Implementar chamada à API
      // Simulando dados
      setUsers([
        {
          id: 1,
          username: 'joao',
          email: 'joao@example.com',
          phone: '+258 84 123 4567',
          is_premium: false,
          total_analyses: 45,
          created_at: '2024-11-15',
        },
        {
          id: 2,
          username: 'maria',
          email: 'maria@example.com',
          phone: '+258 85 987 6543',
          is_premium: true,
          total_analyses: 234,
          created_at: '2024-10-20',
        },
      ]);
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(u => {
    const matchesSearch = 
      u.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = 
      filterType === 'all' ||
      (filterType === 'premium' && u.is_premium) ||
      (filterType === 'free' && !u.is_premium);
    
    return matchesSearch && matchesFilter;
  });

  const togglePremium = async (userId, currentStatus) => {
    // TODO: Implementar chamada à API
    console.log('Toggle premium:', userId, !currentStatus);
  };

  const deleteUser = async (userId) => {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) return;
    // TODO: Implementar chamada à API
    console.log('Delete user:', userId);
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
      <Header title="Gerenciar Usuários" subtitle={`${filteredUsers.length} usuários`} />
      
      <div className="page-content">
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-6 btn-ghost"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar
        </button>

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
          {filteredUsers.map((u) => (
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
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 text-xs font-semibold rounded-full">
                          <Shield className="w-3 h-3" />
                          Premium
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{u.email}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-3 text-sm">
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
              </div>

              <div className="flex gap-2 pt-3 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => togglePremium(u.id, u.is_premium)}
                  className={`flex-1 px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                    u.is_premium
                      ? 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                      : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                  }`}
                >
                  {u.is_premium ? (
                    <>
                      <UserX className="w-4 h-4 inline mr-1" />
                      Remover Premium
                    </>
                  ) : (
                    <>
                      <UserCheck className="w-4 h-4 inline mr-1" />
                      Tornar Premium
                    </>
                  )}
                </button>
                <button
                  onClick={() => deleteUser(u.id)}
                  className="px-3 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl text-sm font-medium hover:bg-red-100 dark:hover:bg-red-900/30 transition-all"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}

          {filteredUsers.length === 0 && (
            <div className="card text-center py-12">
              <p className="text-gray-600 dark:text-gray-400">
                Nenhum usuário encontrado
              </p>
            </div>
          )}
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
