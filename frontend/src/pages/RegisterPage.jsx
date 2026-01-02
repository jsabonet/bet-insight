import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserPlus, Check } from 'lucide-react';
import Logo from '../components/Logo';
import PasswordStrengthInput from '../components/PasswordStrengthInput';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    phone: '',
    date_of_birth: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [passwordsMatch, setPasswordsMatch] = useState(true);
  const [ageError, setAgeError] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    // Check password match in real-time
    if (name === 'password2') {
      setPasswordsMatch(value === formData.password);
    } else if (name === 'password') {
      setPasswordsMatch(formData.password2 === value);
    }
    
    // Validar idade ao digitar data de nascimento
    if (name === 'date_of_birth' && value) {
      const birthDate = new Date(value);
      const today = new Date();
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      
      if (age < 18) {
        setAgeError('Você deve ter pelo menos 18 anos para se cadastrar.');
      } else {
        setAgeError('');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.password2) {
      setError('As senhas não coincidem');
      return;
    }

    if (!formData.date_of_birth) {
      setError('A data de nascimento é obrigatória');
      return;
    }

    if (ageError) {
      setError(ageError);
      return;
    }

    if (!termsAccepted) {
      setError('Você deve aceitar os Termos de Serviço e Política de Privacidade');
      return;
    }

    setLoading(true);

    try {
      await register(formData);
      navigate('/');
    } catch (err) {
      const errors = err.response?.data;
      if (errors) {
        const errorMsg = Object.values(errors).flat().join(', ');
        setError(errorMsg);
      } else {
        setError('Erro ao criar conta. Tente novamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 dark:from-primary-900 dark:to-gray-900 px-4 py-12 relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/5 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-white/5 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/3 rounded-full blur-3xl"></div>
      </div>

      <div className="max-w-md w-full relative z-10">
        <div className="text-center mb-8 animate-slide-up">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-white/20 rounded-full blur-xl"></div>
              <Logo variant="happy" size="xl" showText={false} />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-lg">PlacarCerto</h1>
          <p className="text-primary-100 dark:text-primary-300 text-lg">Junte-se e comece a ganhar com IA</p>
        </div>

        <div className="card shadow-2xl animate-slide-up" style={{ animationDelay: '100ms' }}>
          <h2 className="text-2xl font-bold text-center mb-6 text-gray-900 dark:text-gray-100">Criar Conta</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Usuário *
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="input-field"
                required
                placeholder="Ex: joao_silva"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email *
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="input-field"
                required
                placeholder="seu@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Telefone
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="input-field"
                placeholder="+258 84 XXX XXXX"
              />
            </div>

            <PasswordStrengthInput
              value={formData.password}
              onChange={handleChange}
              name="password"
              label="Senha"
              placeholder="Crie uma senha forte"
              required={true}
              showStrength={true}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirmar Senha <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  type="password"
                  name="password2"
                  value={formData.password2}
                  onChange={handleChange}
                  className={`input-field ${
                    formData.password2 && passwordsMatch
                      ? 'border-green-500 dark:border-green-400 focus:ring-green-500'
                      : formData.password2 && !passwordsMatch
                      ? 'border-red-500 dark:border-red-400 focus:ring-red-500'
                      : ''
                  }`}
                  required
                  placeholder="Digite a senha novamente"
                />
                {formData.password2 && passwordsMatch && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <Check className="w-5 h-5 text-green-600 dark:text-green-400" />
                  </div>
                )}
              </div>
              
              {formData.password2 && !passwordsMatch && (
                <p className="mt-1 text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                  <span className="font-medium">✗</span> As senhas não coincidem
                </p>
              )}
              
              {formData.password2 && passwordsMatch && (
                <p className="mt-1 text-xs text-green-600 dark:text-green-400 flex items-center gap-1">
                  <Check className="w-3 h-3" />
                  <span className="font-medium">As senhas coincidem</span>
                </p>
              )}
            </div>

            {/* Date of Birth */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Data de Nascimento <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                name="date_of_birth"
                value={formData.date_of_birth}
                onChange={handleChange}
                max={new Date(new Date().setFullYear(new Date().getFullYear() - 18)).toISOString().split('T')[0]}
                className={`input-field ${
                  ageError
                    ? 'border-red-500 dark:border-red-400 focus:ring-red-500'
                    : formData.date_of_birth && !ageError
                    ? 'border-green-500 dark:border-green-400 focus:ring-green-500'
                    : ''
                }`}
                required
                placeholder="DD/MM/AAAA"
              />
              
              {ageError && (
                <p className="mt-1 text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                  <span className="font-medium">✗</span> {ageError}
                </p>
              )}
              
              {formData.date_of_birth && !ageError && (
                <p className="mt-1 text-xs text-green-600 dark:text-green-400 flex items-center gap-1">
                  <Check className="w-3 h-3" />
                  <span className="font-medium">Idade verificada: 18+</span>
                </p>
              )}
              
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Você deve ter pelo menos 18 anos para se cadastrar.
              </p>
            </div>

            {/* Terms Acceptance */}
            <div className="space-y-3 pt-2">
              <label className="flex items-start gap-3 cursor-pointer group">
                <div className="relative flex items-center justify-center mt-0.5">
                  <input
                    type="checkbox"
                    checked={termsAccepted}
                    onChange={(e) => setTermsAccepted(e.target.checked)}
                    className="w-5 h-5 text-primary-600 border-2 border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 cursor-pointer"
                    required
                  />
                </div>
                <span className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed group-hover:text-gray-900 dark:group-hover:text-gray-100 transition-colors">
                  Li e aceito os{' '}
                  <Link
                    to="/terms"
                    target="_blank"
                    className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-semibold underline"
                  >
                    Termos de Serviço
                  </Link>
                  {' '}e a{' '}
                  <Link
                    to="/privacy"
                    target="_blank"
                    className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-semibold underline"
                  >
                    Política de Privacidade
                  </Link>
                  .
                </span>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading || ageError || !formData.date_of_birth || !termsAccepted || !passwordsMatch}
              className="w-full bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Criando conta...</span>
                </>
              ) : (
                <>
                  <UserPlus className="w-5 h-5" />
                  <span>Criar Conta</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600 dark:text-gray-400">
              Já tem uma conta?{' '}
              <Link to="/login" className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium">
                Faça login
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
