"""
Sistema de notificações por email
Bet Insight Mozambique
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_subscription_activated_email(user, subscription):
    """
    Envia email de boas-vindas ao premium
    """
    try:
        plan_name = subscription.get_plan_display()
        daily_limit = subscription.get_daily_limit()
        end_date = subscription.end_date.strftime('%d/%m/%Y')
        
        subject = f'🎉 Bem-vindo ao PlacarCerto Premium!'
        
        message = f"""
Olá {user.username}!

Parabéns! Sua assinatura {plan_name} foi ativada com sucesso!

✅ Benefícios ativados:
• {daily_limit} análises por dia
• Acesso completo a estatísticas
• Análises detalhadas com IA
• Notificações em tempo real
• Suporte prioritário

📅 Sua assinatura é válida até: {end_date}

Comece agora a fazer suas análises premium!
👉 https://placarcerto.co.mz

Obrigado por escolher PlacarCerto!

---
PlacarCerto Mozambique
https://placarcerto.co.mz
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f'Email de ativação enviado para {user.email}')
        return True
        
    except Exception as e:
        logger.error(f'Erro ao enviar email de ativação: {str(e)}')
        return False


def send_subscription_expired_email(user, subscription):
    """
    Envia email de expiração de assinatura
    """
    try:
        plan_name = subscription.get_plan_display()
        
        subject = '⏰ Sua assinatura PlacarCerto expirou'
        
        message = f"""
Olá {user.username},

Sua assinatura {plan_name} expirou.

Você agora tem acesso ao plano gratuito com 5 análises por dia.

💎 Renove sua assinatura premium e tenha:
• Até 150 análises por dia
• Acesso completo a estatísticas
• Análises detalhadas com IA
• Suporte prioritário

👉 Renovar agora: https://placarcerto.co.mz/pricing

Sentimos sua falta!

---
PlacarCerto Mozambique
https://placarcerto.co.mz
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f'Email de expiração enviado para {user.email}')
        return True
        
    except Exception as e:
        logger.error(f'Erro ao enviar email de expiração: {str(e)}')
        return False


def send_payment_confirmed_email(user, payment, subscription):
    """
    Envia email de confirmação de pagamento
    """
    try:
        plan_name = subscription.get_plan_display()
        amount = payment.amount
        transaction_id = payment.transaction_id
        
        subject = '✅ Pagamento confirmado - PlacarCerto'
        
        message = f"""
Olá {user.username}!

Seu pagamento foi confirmado com sucesso!

💰 Detalhes do pagamento:
• Plano: {plan_name}
• Valor: {amount} MZN
• Transação: {transaction_id}

Sua assinatura premium está ativa!

👉 Acessar plataforma: https://placarcerto.co.mz

Obrigado!

---
PlacarCerto Mozambique
https://placarcerto.co.mz
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f'Email de confirmação de pagamento enviado para {user.email}')
        return True
        
    except Exception as e:
        logger.error(f'Erro ao enviar email de confirmação: {str(e)}')
        return False


def send_payment_failed_email(user, payment):
    """
    Envia email de falha no pagamento
    """
    try:
        transaction_id = payment.transaction_id
        
        subject = '❌ Falha no pagamento - PlacarCerto'
        
        message = f"""
Olá {user.username},

Infelizmente seu pagamento não foi confirmado.

🔍 Transação: {transaction_id}

Por favor, tente novamente ou entre em contato com o suporte.

👉 Tentar novamente: https://placarcerto.co.mz/pricing
📧 Suporte: suporte@placarcerto.co.mz

---
PlacarCerto Mozambique
https://placarcerto.co.mz
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f'Email de falha de pagamento enviado para {user.email}')
        return True
        
    except Exception as e:
        logger.error(f'Erro ao enviar email de falha: {str(e)}')
        return False
