import { useState, useEffect } from 'react';
import { useStats } from '../context/StatsContext';
import { useAuth } from '../context/AuthContext';
import { User, Phone, Mail, Calendar, Star, TrendingUp, Award, Bell, Lock, Shield, Trash2 } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import UserAvatar from '../components/UserAvatar';
import { authAPI } from '../services/api';

export default function ProfilePage() {
  const { user, updateUser, logout, refreshProfile } = useAuth();
  const { refreshTrigger } = useStats();
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState('profile'); // profile, notifications, security, subscription
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    phone: user?.phone || '',
  });
  const [notificationSettings, setNotificationSettings] = useState({
    push_enabled: user?.push_enabled || false,
    email_notifications: true,
    match_reminders: true,
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [stats, setStats] = useState({
    total_analyses: 0,
    success_rate: 0,
    analyses_count_today: 0,
  });

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    // Atualiza métricas ao ocorrer mudanças globais (ex.: novas análises)
    loadStats();
  }, [refreshTrigger]);

  const handleRefreshProfile = async () => {
    setLoading(true);
    try {
      await refreshProfile();
      setMessage({ type: 'success', text: 'Perfil atualizado!' });
      window.location.reload(); // Recarregar para aplicar mudanças de permissão
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao atualizar perfil' });
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await authAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await updateUser(formData);
      setMessage({ type: 'success', text: 'Perfil atualizado com sucesso!' });
      setEditing(false);
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'Erro ao atualizar perfil',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleNotificationChange = (e) => {
    const { name, checked } = e.target;
    setNotificationSettings({
      ...notificationSettings,
      [name]: checked,
    });
  };

  const handlePasswordChange = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ type: 'error', text: 'As novas senhas não coincidem!' });
      return;
    }

    if (passwordData.new_password.length < 8) {
      setMessage({ type: 'error', text: 'A senha deve ter no mínimo 8 caracteres!' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await authAPI.changePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });
      setMessage({ type: 'success', text: 'Senha alterada com sucesso!' });
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'Erro ao alterar senha',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await updateUser({ push_enabled: notificationSettings.push_enabled });
      setMessage({ type: 'success', text: 'Configurações de notificação atualizadas!' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'Erro ao atualizar configurações',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    const password = window.prompt('Digite sua senha para confirmar a exclusão da conta:');
    
    if (!password) {
      return;
    }

    if (!window.confirm('Tem certeza que deseja deletar sua conta? Esta ação não pode ser desfeita.')) {
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await authAPI.deleteAccount(password);
      setMessage({ type: 'success', text: 'Conta deletada com sucesso! Redirecionando...' });
      setTimeout(() => logout(), 2000);
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'Erro ao deletar conta. Verifique sua senha.',
      });
      setLoading(false);
    }
  };

  const memberSince = user?.date_joined
    ? new Date(user.date_joined).toLocaleDateString('pt-PT', {
        month: 'long',
        year: 'numeric',
      })
    : 'N/A';

  return (
    <div className="page-container">
      <Header title="Perfil" subtitle="Gerencie suas informações" />

      <div className="page-content">

        {/* Admin Notification Banner */}
        {(user?.is_staff || user?.is_superuser) && (
          <div className="card mb-6 animate-slide-up bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border-2 border-red-300 dark:border-red-700">
            <div className="flex items-start gap-3">
              <Shield className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-1">
                  Você é um Administrador
                </h3>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                  Você tem acesso à área administrativa. Se o botão Admin não aparecer no menu, clique no botão abaixo para atualizar.
                </p>
                <button
                  onClick={handleRefreshProfile}
                  disabled={loading}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold text-sm transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  <Shield className="w-4 h-4" />
                  {loading ? 'Atualizando...' : 'Atualizar Permissões'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* User Header Card */}
        <div className="card animate-slide-up mb-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <UserAvatar user={user} size="xl" showBadge={true} />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{user?.username}</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">{user?.email}</p>
                {stats?.is_premium && (
                  <span className="inline-flex items-center gap-1 mt-2 px-3 py-1 bg-gradient-to-r from-yellow-400 to-yellow-500 text-yellow-900 text-xs font-semibold rounded-full shadow-sm">
                    <Star className="w-3 h-3 fill-current" />
                    Premium
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Member Stats Quick View */}
          <div className="grid grid-cols-3 gap-3 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                {stats.total_analyses || 0}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Análises</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {stats.success_rate || 0}%
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Sucesso</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {stats.analyses_count_today || 0}/{stats.daily_limit ?? 3}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Hoje</p>
            </div>
          </div>
        </div>

        {/* Tabs Navigation */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2 no-scrollbar">
          <button
            onClick={() => setActiveTab('profile')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold whitespace-nowrap transition-all ${
              activeTab === 'profile'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700'
            }`}
          >
            <User className="w-4 h-4" />
            Perfil
          </button>
          <button
            onClick={() => setActiveTab('notifications')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold whitespace-nowrap transition-all ${
              activeTab === 'notifications'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700'
            }`}
          >
            <Bell className="w-4 h-4" />
            Notificações
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold whitespace-nowrap transition-all ${
              activeTab === 'security'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700'
            }`}
          >
            <Lock className="w-4 h-4" />
            Segurança
          </button>
        </div>

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

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="card animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                Informações Pessoais
              </h3>
              {!editing && (
                <button onClick={() => setEditing(true)} className="btn-secondary">
                  Editar
                </button>
              )}
            </div>

            {editing ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Nome de Usuário
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                    <input
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      className="input-field pl-10"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      className="input-field pl-10"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Telefone (Notificações)
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      className="input-field pl-10"
                      placeholder="+258 84 123 4567"
                    />
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Usado para enviar notificações de análises
                  </p>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary flex-1"
                  >
                    {loading ? 'Salvando...' : 'Salvar Alterações'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setEditing(false);
                      setFormData({
                        username: user?.username || '',
                        email: user?.email || '',
                        phone: user?.phone || '',
                      });
                      setMessage({ type: '', text: '' });
                    }}
                    className="btn-secondary flex-1"
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-transparent dark:border-gray-700/50">
                  <Mail className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Email</p>
                    <p className="font-medium text-gray-900 dark:text-gray-100">{user?.email}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-transparent dark:border-gray-700/50">
                  <Phone className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Telefone</p>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      {user?.phone || 'Não configurado'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-transparent dark:border-gray-700/50">
                  <Calendar className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Membro desde</p>
                    <p className="font-medium text-gray-900 dark:text-gray-100">{memberSince}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div className="card animate-slide-up">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6">
              Configurações de Notificações
            </h3>

            <form onSubmit={handleNotificationSubmit} className="space-y-6">
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-gray-200 dark:border-gray-700/50">
                <div className="flex items-center gap-3">
                  <Bell className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      Notificações Push
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Receba alertas no navegador
                    </p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    name="push_enabled"
                    checked={notificationSettings.push_enabled}
                    onChange={handleNotificationChange}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 dark:bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-gray-200 dark:border-gray-700/50">
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      Email de Análises
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Receba análises por email
                    </p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    name="email_notifications"
                    checked={notificationSettings.email_notifications}
                    onChange={handleNotificationChange}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 dark:bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-gray-200 dark:border-gray-700/50">
                <div className="flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-green-600 dark:text-green-400" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      Lembrete de Partidas
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Alertas antes dos jogos
                    </p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    name="match_reminders"
                    checked={notificationSettings.match_reminders}
                    onChange={handleNotificationChange}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-300 dark:bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary"
              >
                {loading ? 'Salvando...' : 'Salvar Preferências'}
              </button>
            </form>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            {/* Change Password */}
            <div className="card animate-slide-up">
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6">
                Alterar Senha
              </h3>

              <form onSubmit={handlePasswordSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Senha Atual
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                    <input
                      type="password"
                      name="current_password"
                      value={passwordData.current_password}
                      onChange={handlePasswordChange}
                      className="input-field pl-10"
                      required
                      placeholder="Digite sua senha atual"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Nova Senha
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                    <input
                      type="password"
                      name="new_password"
                      value={passwordData.new_password}
                      onChange={handlePasswordChange}
                      className="input-field pl-10"
                      required
                      placeholder="Mínimo 8 caracteres"
                      minLength={8}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Confirmar Nova Senha
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                    <input
                      type="password"
                      name="confirm_password"
                      value={passwordData.confirm_password}
                      onChange={handlePasswordChange}
                      className="input-field pl-10"
                      required
                      placeholder="Digite a nova senha novamente"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full btn-primary"
                >
                  {loading ? 'Alterando...' : 'Alterar Senha'}
                </button>
              </form>
            </div>

            {/* Delete Account */}
            <div className="card animate-slide-up border-red-200 dark:border-red-900/50">
              <div className="flex items-start gap-3 mb-4">
                <Trash2 className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="text-lg font-bold text-red-600 dark:text-red-400 mb-2">
                    Zona de Perigo
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Deletar sua conta é uma ação irreversível. Todos os seus dados, análises e configurações serão permanentemente removidos.
                  </p>
                  <button
                    onClick={handleDeleteAccount}
                    className="btn-secondary text-red-600 dark:text-red-400 border-red-300 dark:border-red-800 hover:bg-red-50 dark:hover:bg-red-900/20"
                  >
                    Deletar Minha Conta
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Logout Button */}
        <button
          onClick={logout}
          className="w-full btn-secondary text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 dark:hover:border-red-800/50 active:scale-95 mt-6"
        >
          Sair da Conta
        </button>

        <style>{`
          .no-scrollbar::-webkit-scrollbar {
            display: none;
          }
        `}</style>
      </div>

      <BottomNav />
    </div>
  );
}
