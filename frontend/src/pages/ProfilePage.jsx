import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Phone, Mail, Calendar, Star, TrendingUp, Award } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import UserAvatar from '../components/UserAvatar';

export default function ProfilePage() {
  const { user, updateUser, logout } = useAuth();
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    phone_number: user?.phone_number || '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

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

        <div className="grid grid-cols-1 gap-6 mb-8">
          {/* Profile Card */}
          <div className="card animate-slide-up">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-4">
                <UserAvatar user={user} size="xl" showBadge={true} />
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{user?.username}</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{user?.email}</p>
                  {user?.is_premium && (
                    <span className="inline-flex items-center gap-1 mt-2 px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 text-xs font-semibold rounded-full">
                      <Star className="w-3 h-3" />
                      Premium
                    </span>
                  )}
                </div>
              </div>
              
              {!editing && (
                <button
                  onClick={() => setEditing(true)}
                  className="btn-secondary"
                >
                  Editar
                </button>
              )}
            </div>

            {message.text && (
              <div
                className={`mb-4 p-4 rounded-xl border ${
                  message.type === 'success'
                    ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800/50'
                    : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800/50'
                }`}
              >
                {message.text}
              </div>
            )}

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
                      name="phone_number"
                      value={formData.phone_number}
                      onChange={handleChange}
                      className="input-field pl-10"
                      placeholder="+258 84 123 4567"
                    />
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Usado para enviar notificações de análises
                  </p>
                </div>

                <div className="flex gap-3">
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
                        phone_number: user?.phone_number || '',
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
              <div className="space-y-4">
                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-transparent dark:border-gray-700/50">
                  <Mail className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Email</p>
                    <p className="font-medium text-gray-900 dark:text-gray-100">{user?.email}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-transparent dark:border-gray-700/50">
                  <Phone className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Telefone</p>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      {user?.phone_number || 'Não configurado'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-transparent dark:border-gray-700/50">
                  <Calendar className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Membro desde</p>
                    <p className="font-medium text-gray-900 dark:text-gray-100">{memberSince}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Stats Card */}
          <div className="card animate-slide-up">
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">Estatísticas</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Análises Hoje</span>
                  </div>
                  <span className="font-bold text-gray-900 dark:text-gray-100">
                    {user?.analyses_count_today || 0}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Total de Análises</span>
                  </div>
                  <span className="font-bold text-gray-900 dark:text-gray-100">
                    {user?.total_analyses || 0}
                  </span>
                </div>

                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Limite Diário</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {user?.analyses_count_today || 0} / {user?.is_premium ? 100 : 5}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-primary-600 dark:bg-primary-500 h-2 rounded-full transition-all"
                      style={{
                        width: `${
                          ((user?.analyses_count_today || 0) /
                            (user?.is_premium ? 100 : 5)) *
                          100
                        }%`,
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
        </div>

        <button
          onClick={logout}
          className="w-full btn-secondary text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 dark:hover:border-red-800/50 active:scale-95"
        >
          Sair da Conta
        </button>
      </div>

      <BottomNav />
    </div>
  );
}
