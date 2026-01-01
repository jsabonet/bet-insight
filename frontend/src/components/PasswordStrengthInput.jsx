import { useState, useEffect } from 'react';
import { Check, X, Eye, EyeOff, Shield, AlertCircle } from 'lucide-react';

export default function PasswordStrengthInput({ 
  value, 
  onChange, 
  name = "password",
  label = "Senha",
  placeholder = "Digite sua senha",
  required = true,
  showStrength = true,
  className = ""
}) {
  const [showPassword, setShowPassword] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [requirements, setRequirements] = useState({
    minLength: false,
    hasUpperCase: false,
    hasLowerCase: false,
    hasNumber: false,
    hasSpecial: false,
  });

  useEffect(() => {
    if (value) {
      setRequirements({
        minLength: value.length >= 8,
        hasUpperCase: /[A-Z]/.test(value),
        hasLowerCase: /[a-z]/.test(value),
        hasNumber: /[0-9]/.test(value),
        hasSpecial: /[!@#$%^&*(),.?":{}|<>_\-+=[\]\\;'/`~]/.test(value),
      });
    } else {
      setRequirements({
        minLength: false,
        hasUpperCase: false,
        hasLowerCase: false,
        hasNumber: false,
        hasSpecial: false,
      });
    }
  }, [value]);

  const getPasswordStrength = () => {
    const validRequirements = Object.values(requirements).filter(Boolean).length;
    
    if (validRequirements === 0) return { level: 0, text: '', color: '' };
    if (validRequirements <= 2) return { level: 1, text: 'Fraca', color: 'red' };
    if (validRequirements === 3) return { level: 2, text: 'Média', color: 'yellow' };
    if (validRequirements === 4) return { level: 3, text: 'Boa', color: 'blue' };
    return { level: 4, text: 'Forte', color: 'green' };
  };

  const strength = getPasswordStrength();
  const allRequirementsMet = Object.values(requirements).every(Boolean);

  const RequirementItem = ({ met, text }) => (
    <div className={`flex items-center gap-2 text-sm transition-all ${
      met 
        ? 'text-green-700 dark:text-green-400' 
        : 'text-gray-600 dark:text-gray-400'
    }`}>
      {met ? (
        <Check className="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0" />
      ) : (
        <X className="w-4 h-4 text-gray-400 dark:text-gray-600 flex-shrink-0" />
      )}
      <span className={met ? 'font-medium' : ''}>{text}</span>
    </div>
  );

  return (
    <div className={className}>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      
      <div className="relative">
        <input
          type={showPassword ? "text" : "password"}
          name={name}
          value={value}
          onChange={onChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className={`input-field pr-10 ${
            value && allRequirementsMet 
              ? 'border-green-500 dark:border-green-400 focus:ring-green-500' 
              : value 
              ? 'border-yellow-500 dark:border-yellow-400 focus:ring-yellow-500' 
              : ''
          }`}
          required={required}
          placeholder={placeholder}
          autoComplete="new-password"
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
          tabIndex={-1}
        >
          {showPassword ? (
            <EyeOff className="w-5 h-5" />
          ) : (
            <Eye className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Password Strength Indicator */}
      {showStrength && value && (
        <div className="mt-2">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
              Força da senha:
            </span>
            <span className={`text-xs font-bold ${
              strength.color === 'green' ? 'text-green-600 dark:text-green-400' :
              strength.color === 'blue' ? 'text-blue-600 dark:text-blue-400' :
              strength.color === 'yellow' ? 'text-yellow-600 dark:text-yellow-400' :
              'text-red-600 dark:text-red-400'
            }`}>
              {strength.text}
            </span>
          </div>
          
          {/* Strength Bar */}
          <div className="flex gap-1 h-1.5 mb-3">
            {[1, 2, 3, 4].map((level) => (
              <div
                key={level}
                className={`flex-1 rounded-full transition-all ${
                  level <= strength.level
                    ? strength.color === 'green' ? 'bg-green-500 dark:bg-green-400' :
                      strength.color === 'blue' ? 'bg-blue-500 dark:bg-blue-400' :
                      strength.color === 'yellow' ? 'bg-yellow-500 dark:bg-yellow-400' :
                      'bg-red-500 dark:bg-red-400'
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Requirements List */}
      {(isFocused || value) && (
        <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl animate-slide-up">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-4 h-4 text-primary-600 dark:text-primary-400" />
            <span className="text-xs font-semibold text-gray-700 dark:text-gray-300">
              Requisitos da Senha
            </span>
          </div>
          
          <div className="space-y-1.5">
            <RequirementItem 
              met={requirements.minLength} 
              text="Mínimo de 8 caracteres" 
            />
            <RequirementItem 
              met={requirements.hasUpperCase} 
              text="Pelo menos uma letra maiúscula (A-Z)" 
            />
            <RequirementItem 
              met={requirements.hasLowerCase} 
              text="Pelo menos uma letra minúscula (a-z)" 
            />
            <RequirementItem 
              met={requirements.hasNumber} 
              text="Pelo menos um número (0-9)" 
            />
            <RequirementItem 
              met={requirements.hasSpecial} 
              text="Pelo menos um caractere especial (!@#$%*)" 
            />
          </div>

          {allRequirementsMet && (
            <div className="mt-3 pt-3 border-t border-green-200 dark:border-green-800 flex items-center gap-2 text-green-700 dark:text-green-400">
              <Check className="w-4 h-4 font-bold" />
              <span className="text-xs font-semibold">
                ✓ Senha forte! Você está protegido.
              </span>
            </div>
          )}
        </div>
      )}

      {/* Warning if not all requirements met and field touched */}
      {value && !allRequirementsMet && !isFocused && (
        <div className="mt-2 flex items-start gap-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-yellow-700 dark:text-yellow-300">
            Sua senha não atende a todos os requisitos de segurança. 
            Por favor, torne-a mais forte.
          </p>
        </div>
      )}
    </div>
  );
}
