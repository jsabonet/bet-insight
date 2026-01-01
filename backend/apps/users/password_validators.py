"""
Validadores de senha customizados para o PlacarCerto
Garante senhas fortes e seguras
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class StrongPasswordValidator:
    """
    Valida que a senha atende aos requisitos de segurança:
    - Mínimo 8 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um caractere especial
    """
    
    def validate(self, password, user=None):
        errors = []
        
        if len(password) < 8:
            errors.append(_('A senha deve ter no mínimo 8 caracteres.'))
        
        if not re.search(r'[A-Z]', password):
            errors.append(_('A senha deve conter pelo menos uma letra maiúscula (A-Z).'))
        
        if not re.search(r'[a-z]', password):
            errors.append(_('A senha deve conter pelo menos uma letra minúscula (a-z).'))
        
        if not re.search(r'[0-9]', password):
            errors.append(_('A senha deve conter pelo menos um número (0-9).'))
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'/`~]', password):
            errors.append(_('A senha deve conter pelo menos um caractere especial (!@#$%*).'))
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _(
            "Sua senha deve conter:\n"
            "• Mínimo de 8 caracteres\n"
            "• Pelo menos uma letra maiúscula (A-Z)\n"
            "• Pelo menos uma letra minúscula (a-z)\n"
            "• Pelo menos um número (0-9)\n"
            "• Pelo menos um caractere especial (!@#$%*)"
        )


class NoCommonPasswordValidator:
    """
    Valida que a senha não é uma senha comum
    """
    COMMON_PASSWORDS = [
        '12345678', 'password', 'senha123', 'admin123',
        'qwerty123', '123456789', 'password123', 'senha1234',
        'abc12345', 'Password1', 'Admin123', 'Qwerty1!',
    ]
    
    def validate(self, password, user=None):
        if password.lower() in [p.lower() for p in self.COMMON_PASSWORDS]:
            raise ValidationError(
                _('Esta senha é muito comum. Por favor, escolha uma senha mais única.'),
                code='password_too_common',
            )
    
    def get_help_text(self):
        return _('Sua senha não pode ser uma senha comum.')


class NoUserAttributePasswordValidator:
    """
    Valida que a senha não contém atributos do usuário
    """
    
    def validate(self, password, user=None):
        if not user:
            return
        
        errors = []
        
        # Verificar username
        if user.username and len(user.username) > 3:
            if user.username.lower() in password.lower():
                errors.append(_('A senha não pode conter seu nome de usuário.'))
        
        # Verificar email
        if user.email:
            email_parts = user.email.split('@')
            if len(email_parts[0]) > 3 and email_parts[0].lower() in password.lower():
                errors.append(_('A senha não pode conter partes do seu email.'))
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _('Sua senha não pode ser muito similar às suas informações pessoais.')
