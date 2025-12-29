"""
Serviço de integração com PaySuite API
Suporta M-Pesa, E-Mola e outros métodos de pagamento em Moçambique
"""
import requests
import hashlib
import hmac
from django.conf import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PaySuiteService:
    """Serviço para integração com PaySuite API"""
    
    def __init__(self):
        self.api_token = settings.PAYSUITE_API_TOKEN
        self.webhook_secret = settings.PAYSUITE_WEBHOOK_SECRET
        self.api_url = settings.PAYSUITE_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def create_payment(
        self,
        amount: float,
        phone_number: str,
        reference: str,
        description: str = "Assinatura Bet Insight",
        method: str = "mpesa"  # mpesa, emola, card
    ) -> Dict:
        """
        Criar uma requisição de pagamento
        
        Args:
            amount: Valor em MZN (ex: 299.00)
            phone_number: Número do cliente (ex: +258840000000 ou 840000000)
            reference: Referência única da transação
            description: Descrição do pagamento
            method: Método de pagamento (mpesa, emola, card)
        
        Returns:
            Dict com resposta da API
        """
        try:
            # Garantir formato correto do número
            if not phone_number.startswith('+258'):
                phone_number = f'+258{phone_number.lstrip("0")}'
            
            payload = {
                'amount': float(amount),
                'phone': phone_number,
                'reference': reference,
                'description': description,
                'method': method,
                'currency': 'MZN'
            }
            
            logger.info(f"Criando pagamento PaySuite: {payload}")
            
            response = requests.post(
                f'{self.api_url}/v1/payment',
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Pagamento criado com sucesso: {data}")
            return {
                'success': True,
                'payment_id': data.get('id'),
                'status': data.get('status'),
                'data': data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao criar pagamento PaySuite: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_payment_status(self, payment_id: str) -> Dict:
        """
        Verificar status de um pagamento
        
        Args:
            payment_id: ID do pagamento retornado na criação
        
        Returns:
            Dict com status do pagamento
        """
        try:
            response = requests.get(
                f'{self.api_url}/v1/payment/{payment_id}',
                headers=self.headers,
                timeout=15
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'status': data.get('status'),  # pending, completed, failed, cancelled
                'amount': data.get('amount'),
                'data': data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao verificar status do pagamento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verificar assinatura do webhook para garantir autenticidade
        
        Args:
            payload: Corpo da requisição do webhook (string)
            signature: Assinatura enviada no header X-PaySuite-Signature
        
        Returns:
            bool: True se assinatura for válida
        """
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Erro ao verificar assinatura do webhook: {e}")
            return False
    
    def process_webhook(self, webhook_data: Dict) -> Dict:
        """
        Processar dados do webhook
        
        Args:
            webhook_data: Dados recebidos do webhook
        
        Returns:
            Dict com informações processadas
        """
        try:
            payment_id = webhook_data.get('id')
            status = webhook_data.get('status')
            amount = webhook_data.get('amount')
            reference = webhook_data.get('reference')
            phone = webhook_data.get('phone')
            
            logger.info(f"Processando webhook PaySuite - Payment ID: {payment_id}, Status: {status}")
            
            return {
                'payment_id': payment_id,
                'status': status,
                'amount': amount,
                'reference': reference,
                'phone': phone,
                'raw_data': webhook_data
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}")
            return {
                'error': str(e)
            }
    
    def refund_payment(self, payment_id: str, reason: str = "Reembolso") -> Dict:
        """
        Solicitar reembolso de um pagamento
        
        Args:
            payment_id: ID do pagamento a ser reembolsado
            reason: Motivo do reembolso
        
        Returns:
            Dict com resultado do reembolso
        """
        try:
            payload = {
                'payment_id': payment_id,
                'reason': reason
            }
            
            response = requests.post(
                f'{self.api_url}/v1/payment/{payment_id}/refund',
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Reembolso processado: {data}")
            return {
                'success': True,
                'data': data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao processar reembolso: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Instância global para uso em toda aplicação
paysuite_service = PaySuiteService()
