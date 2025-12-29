import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Phone, Mail, Calendar, Star, TrendingUp, Award } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';

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
                <div className="w-20 h-20 bg-primary-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">
                  {user?.username?.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{user?.username}</h2>
                  <p className="text-sm text-gray-600">{user?.email}</p>
                  {user?.is_premium && (
                    <span className="inline-flex items-center gap-1 mt-2 px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded-full">
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
                className={`mb-4 p-4 rounded-lg ${
                  message.type === 'success'
                    ? 'bg-green-50 text-green-700'
                    : 'bg-red-50 text-red-700'
                }`}
              >
                {message.text}
              </div>
            )}

            {editing ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nome de Usuário
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Telefone (Notificações)
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="tel"
                      name="phone_number"
                      value={formData.phone_number}
                      onChange={handleChange}
                      className="input-field pl-10"
                      placeholder="+258 84 123 4567"
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
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
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Mail className="w-5 h-5 text-gray-600" />
                  <div>
                    <p className="text-sm text-gray-600">Email</p>
                    <p className="font-medium text-gray-900">{user?.email}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Phone className="w-5 h-5 text-gray-600" />
                  <div>
                    <p className="text-sm text-gray-600">Telefone</p>
                    <p className="font-medium text-gray-900">
                      {user?.phone_number || 'Não configurado'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Calendar className="w-5 h-5 text-gray-600" />
                  <div>
                    <p className="text-sm text-gray-600">Membro desde</p>
                    <p className="font-medium text-gray-900">{memberSince}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Stats Card */}
          <div className="card animate-slide-up">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Estatísticas</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-primary-600" />
                    <span className="text-sm text-gray-600">Análises Hoje</span>
                  </div>
                  <span className="font-bold text-gray-900">
                    {user?.analyses_count_today || 0}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-blue-600" />
                    <span className="text-sm text-gray-600">Total de Análises</span>
                  </div>
                  <span className="font-bold text-gray-900">
                    {user?.total_analyses || 0}
                  </span>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">Limite Diário</span>
                    <span className="text-sm font-medium text-gray-900">
                      {user?.analyses_count_today || 0} / {user?.is_premium ? 100 : 5}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all"
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
          className="w-full btn-secondary text-red-600 hover:bg-red-50 active:scale-95"
        >
          Sair da Conta
        </button>
      </div>

      <BottomNav />
    </div>
  );
}
