import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, Shield, User, Mail, Phone, Save } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function EditUserModal({ user, isOpen, onClose, onSuccess }) {
  const { user: currentUser } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone: '',
    first_name: '',
    last_name: '',
    is_active: true,
    is_staff: false,
    is_superuser: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('info');

  useEffect(() => {
    if (isOpen && user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        phone: user.phone || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        is_active: user.is_active !== undefined ? user.is_active : true,
        is_staff: user.is_staff || false,
        is_superuser: user.is_superuser || false,
      });
      setActiveTab('info');
      setError('');
    }
  }, [isOpen, user]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const { is_staff, is_superuser, ...dataToSend } = formData;
      if (currentUser?.is_superuser) {
        dataToSend.is_staff = is_staff;
        dataToSend.is_superuser = is_superuser;
      }
      await api.put(`/users/admin/users/${user.id}/update/`, dataToSend);
      onSuccess('Usuário atualizado com sucesso!');
      onClose();
    } catch (err) {
      console.error('Erro ao atualizar usuário:', err);
      console.error('Resposta do servidor:', err.response?.data);
      const errorMessage = err.response?.data?.error || 
                          JSON.stringify(err.response?.data) ||
                          'Erro ao atualizar usuário';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAdmin = async () => {
    setLoading(true);
    setError('');

    try {
      const nextIsStaff = !formData.is_staff;
      await api.post(`/users/admin/users/${user.id}/toggle-admin/`, {
        is_staff: nextIsStaff,
        is_superuser: nextIsStaff && formData.is_superuser
      });
      setFormData(prev => ({
        ...prev,
        is_staff: nextIsStaff,
        is_superuser: nextIsStaff && prev.is_superuser
      }));
      onSuccess(`Usuário ${nextIsStaff ? 'promovido a' : 'removido de'} admin!`);
    } catch (err) {
      console.error('Erro ao alterar status admin:', err);
      setError(err.response?.data?.error || 'Erro ao alterar status admin');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Editar Usuário
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {user?.email}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-all"
          >
            <X className="w-6 h-6 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 px-6">
          <button
            onClick={() => setActiveTab('info')}
            className={`px-4 py-3 font-medium text-sm transition-all border-b-2 ${
              activeTab === 'info'
                ? 'border-primary-600 dark:border-primary-400 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            Informações
          </button>
          <button
            onClick={() => setActiveTab('admin')}
            className={`px-4 py-3 font-medium text-sm transition-all border-b-2 ${
              activeTab === 'admin'
                ? 'border-primary-600 dark:border-primary-400 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            Administração
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto max-h-[60vh]">
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Tab: Informações Básicas */}
          {activeTab === 'info' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <User className="w-4 h-4 inline mr-1" />
                    Username
                  </label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="input-field"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Mail className="w-4 h-4 inline mr-1" />
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="input-field"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Primeiro Nome
                  </label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    className="input-field"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Último Nome
                  </label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    className="input-field"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <Phone className="w-4 h-4 inline mr-1" />
                  Telefone
                </label>
                <input
                  type="text"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="841234567"
                />
              </div>

              <div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                <input
                  type="checkbox"
                  id="is_active"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleChange}
                  className="w-5 h-5 text-primary-600 rounded"
                />
                <label htmlFor="is_active" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Conta Ativa (usuário pode fazer login)
                </label>
              </div>
            </div>
          )}

          {/* Tab: Administração */}
          {activeTab === 'admin' && (
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl">
                <div className="flex items-start gap-3">
                  <Shield className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
                      Privilégios de Administrador
                    </h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      Administradores podem gerenciar usuários, planos e ver estatísticas do sistema.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      Status Admin
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {formData.is_staff ? 'Usuário é administrador' : 'Usuário comum'}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={handleToggleAdmin}
                    disabled={
                      loading ||
                      user?.id === currentUser?.id ||
                      (user?.is_superuser && !currentUser?.is_superuser)
                    }
                    className={`px-4 py-2 rounded-xl font-medium transition-all disabled:cursor-not-allowed disabled:opacity-50 ${
                      formData.is_staff
                        ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-900/50'
                        : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/50'
                    }`}
                  >
                    {formData.is_staff ? 'Remover Admin' : 'Tornar Admin'}
                  </button>
                </div>

                {formData.is_staff && currentUser?.is_superuser && (
                  <div className="flex items-center gap-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl">
                    <input
                      type="checkbox"
                      id="is_superuser"
                      name="is_superuser"
                      checked={formData.is_superuser}
                      onChange={handleChange}
                      className="w-5 h-5 text-yellow-600 rounded"
                    />
                    <label htmlFor="is_superuser" className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                      <Shield className="w-4 h-4 inline mr-1" />
                      Superusuário (controle total do sistema)
                    </label>
                  </div>
                )}
              </div>

              <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl">
                <p className="text-sm text-amber-800 dark:text-amber-200">
                  ⚠️ <strong>Atenção:</strong> Administradores têm acesso a funcionalidades sensíveis.
                  Apenas promova usuários confiáveis.
                </p>
              </div>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 px-4 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-xl hover:bg-gray-200 dark:hover:bg-gray-600 transition-all"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 px-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-bold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Salvando...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Salvar Alterações
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.body
  );
}
