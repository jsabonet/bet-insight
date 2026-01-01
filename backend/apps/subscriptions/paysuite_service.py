"""
Serviço de Integração com PaySuite
PlacarCerto Mozambique - Processamento de Pagamentos M-Pesa e e-Mola
"""

import requests
import hashlib
import json
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PaySuiteService:
    """
    Cliente para API PaySuite
    Documentação: https://docs.paysuite.co.mz/
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'PAYSUITE_API_KEY', '')
        self.webhook_secret = getattr(settings, 'PAYSUITE_API_SECRET', '')
        self.private_key = getattr(settings, 'PAYSUITE_PRIVATE_KEY', '')
        self.base_url = getattr(settings, 'PAYSUITE_BASE_URL', 'https://paysuite.tech/api/v1')
        self.webhook_url = getattr(settings, 'PAYSUITE_WEBHOOK_URL', '')
        self.environment = getattr(settings, 'PAYSUITE_ENVIRONMENT', 'production')
        self.mode = getattr(settings, 'PAYSUITE_MODE', '').lower()  # 'token' | 'private_key' | '' (auto)
    
    def _get_headers(self):
        """Retorna headers para requisição PaySuite"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    def create_payment(self, phone_number, amount, reference, description='Assinatura Premium', method=None, return_url=None):
        """
        Cria uma solicitação de pagamento via PaySuite
        
        Args:
            phone_number (str, opcional): Número de telefone (+258...). 
                Se None, usuário preencherá na página externa.
            amount (Decimal): Valor em MZN
            reference (str): Referência única da transação
            description (str): Descrição do pagamento
            method (str): mpesa, emola, card, transfer
        
        Returns:
            dict: Resposta da API com status, transaction_id e checkout_url
        """
        
        # MODO DE TESTE: Retornar sucesso simulado se em ambiente de desenvolvimento
        if self.environment == 'sandbox' and not self.mode:
            logger.warning("⚠️ MODO DE TESTE ATIVADO - Simulando pagamento PaySuite")
            logger.info(f"💰 Pagamento simulado: {amount} MZN")
            logger.info(f"📝 Referência: {reference}")
            logger.info(f"📄 Descrição: {description}")
            
            return {
                'success': True,
                'transaction_id': reference,
                'paysuite_reference': reference,
                'checkout_url': 'https://paysuite.tech/checkout/test-' + reference,
                'status': 'pending',
                'message': '✅ Pagamento simulado com sucesso (TESTE)',
                'raw_response': {
                    'test_mode': True,
                    'amount': float(amount),
                    'reference': reference
                }
            }
        
        try:
            logger.info(f"Iniciando pagamento PaySuite: {reference} - {amount} MZN")
            logger.info(f"Ambiente: {self.environment} | Modo: {self.mode or 'auto'}")

            # Payload base (sem telefone para checkout externo)
            token_payload = {
                'amount': float(amount),
                'reference': reference,
                'description': description,
            }
            if method:
                token_payload['method'] = method
            if return_url:
                token_payload['return_url'] = return_url
            if self.webhook_url:
                token_payload['callback_url'] = self.webhook_url
                
            # Adicionar telefone APENAS se fornecido (para pagamento direto mobile)
            if phone_number and method in ['mpesa', 'emola']:
                # Formatar para 258XXXXXXXXX
                clean_phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
                if not clean_phone.startswith('258'):
                    clean_phone = '258' + clean_phone
                token_payload['msisdn'] = clean_phone
            token_headers = self._get_headers()

            token_url = f"{self.base_url}/payments"
            logger.info(f"Tentando PaySuite Token URL: {token_url}")
            logger.info(f"Headers: {json.dumps({k: v for k, v in token_headers.items() if k != 'Authorization'}, indent=2)}")
            logger.info(f"Payload: {json.dumps(token_payload, indent=2)}")

            response = None
            data = None
            try:
                response = requests.post(token_url, headers=token_headers, json=token_payload, timeout=30)
                logger.info(f"HTTP Status: {response.status_code}")
                logger.info(f"Response Text (trunc): {response.text[:300]}")
                data = response.json()
                logger.info(f"Response JSON: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                logger.warning("Resposta não-JSON no fluxo Token. Tentando fluxo Private Key...")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Falha no fluxo Token: {str(e)} | Tentando fluxo Private Key...")

            # Se falhou ou não sucesso, tentar fluxo Private Key (checkout link)
            if not data or not data.get('success', False):
                if self.private_key:
                    link_payload = {
                        'private_key': self.private_key,
                        'currency': 'MZN',
                        'callback_url': self.webhook_url or '',
                        'is_test': 0 if self.environment == 'production' else 1,
                        'amount': float(amount),
                        'purpose': description,
                    }
                    link_url = f"{self.base_url}/request"
                    logger.info(f"Tentando PaySuite Link URL: {link_url}")
                    logger.info(f"Payload: {json.dumps({k: v for k, v in link_payload.items() if k != 'private_key'}, indent=2)}")
                    try:
                        response = requests.post(link_url, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, json=link_payload, timeout=30)
                        logger.info(f"HTTP Status: {response.status_code}")
                        logger.info(f"Response Text (trunc): {response.text[:300]}")
                        data = response.json()
                        logger.info(f"Response JSON: {json.dumps(data, indent=2)}")
                    except json.JSONDecodeError:
                        logger.error("Resposta inválida (não-JSON) no fluxo Private Key.")
                        data = None
                    except requests.exceptions.RequestException as e:
                        logger.error(f"Falha no fluxo Private Key: {str(e)}")
                        data = None
            
            # Log da resposta bruta
            # Se ainda não temos dados válidos
            if not data:
                return {
                    'success': False,
                    'error': 'API PaySuite indisponível ou endpoint desconhecido',
                    'message': 'Falha ao integrar com PaySuite. Confirme o endpoint correto ou credenciais.'
                }
            
            # Verificar resposta segundo documentação oficial (paysuite.tech)
            # Esperado: { "status": "success", "data": { "id": "uuid", "checkout_url": "...", "status": "pending" } }
            status_field = data.get('status')
            data_field = data.get('data') if isinstance(data.get('data'), dict) else {}

            if status_field == 'success' and data_field.get('id'):
                provider_id = data_field.get('id')
                checkout_url = data_field.get('checkout_url', '')
                # Mantemos nossa referência interna como transaction_id
                return {
                    'success': True,
                    'transaction_id': reference,
                    'paysuite_reference': provider_id,
                    'checkout_url': checkout_url,
                    'status': data_field.get('status', 'pending'),
                    'message': data.get('message', 'Pagamento iniciado com sucesso'),
                    'raw_response': data
                }
            else:
                # Erro retornado pela API
                error_msg = data.get('message', data.get('error', 'Erro ao criar pagamento'))
                logger.error(f"PaySuite Error: {data.get('status')} - {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'message': error_msg
                }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao criar pagamento PaySuite: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Erro ao processar pagamento. Tente novamente.'
            }
        except Exception as e:
            logger.error(f"Erro inesperado PaySuite: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Erro interno. Contate o suporte.'
            }
    
    def check_payment_status(self, transaction_or_provider_id):
        """
        Verifica status de um pagamento
        
        Args:
            transaction_id (str): ID da transação
        
        Returns:
            dict: Status atualizado do pagamento
        """
        # MODO DE TESTE: em sandbox, não chamar PaySuite; simular "completed"
        if self.environment == 'sandbox' and not self.mode:
            logger.warning("⚠️ MODO DE TESTE - Simulando status PaySuite como 'completed'")
            return {
                'success': True,
                'status': 'completed',
                'paid_at': None,
                'amount': None,
                'raw_response': {
                    'test_mode': True,
                    'transaction_id': transaction_or_provider_id,
                    'status': 'completed'
                }
            }

        # Em modo private_key, normalmente o status vem apenas via webhook
        if self.mode == 'private_key':
            logger.info("Verificação de status: modo private_key usa apenas webhook; retornando status local.")
            return {
                'success': False,
                'error': 'Status verificado via webhook'
            }

        # Em modo token (padrão), consultar o UUID do provider
        try:
            response = requests.get(
                f"{self.base_url}/payments/{transaction_or_provider_id}",
                headers=self._get_headers(),
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Formato esperado: { "status": "success", "data": { "status": "paid", "transaction": {"status": "completed", "paid_at": ...} } }
            data_field = data.get('data') if isinstance(data.get('data'), dict) else {}
            paid = data_field.get('status') == 'paid'
            transaction_info = data_field.get('transaction') if isinstance(data_field.get('transaction'), dict) else {}
            completed = transaction_info.get('status') == 'completed'

            mapped_status = 'completed' if paid or completed else ('failed' if data_field.get('status') == 'failed' else 'pending')

            return {
                'success': True,
                'status': mapped_status,
                'paid_at': transaction_info.get('paid_at'),
                'amount': data_field.get('amount'),
                'raw_response': data
            }

        except Exception as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_webhook_signature(self, payload_body, signature):
        """
        Verifica assinatura do webhook PaySuite usando HMAC SHA256
        
        Args:
            payload_body (str): Body raw da requisição
            signature (str): Assinatura recebida no header X-Paysuite-Signature
        
        Returns:
            bool: True se assinatura é válida
        """
        import hmac
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def process_webhook(self, payload, signature=None):
        """
        Processa callback do PaySuite
        
        Args:
            payload (dict): Dados do webhook
            signature (str): Assinatura para validação
        
        Returns:
            dict: Dados processados do pagamento
        """
        # Validar assinatura se fornecida
        if signature and not self.verify_webhook_signature(payload, signature):
            logger.warning("Assinatura inválida no webhook PaySuite")
            return {
                'success': False,
                'error': 'Invalid signature'
            }
        
        # Suporta formato oficial: { event: 'payment.success'|'payment.failed', data: { id, amount, reference, transaction: {...} } }
        event = payload.get('event')
        data_field = payload.get('data') if isinstance(payload.get('data'), dict) else {}
        reference = data_field.get('reference') or payload.get('reference')
        status = None
        if event == 'payment.success':
            status = 'completed'
        elif event == 'payment.failed':
            status = 'failed'
        else:
            status = payload.get('status')  # fallback
        transaction_id = data_field.get('transaction', {}).get('transaction_id') or payload.get('transaction_id')
        
        logger.info(f"Webhook recebido - Transaction: {transaction_id}, Status: {status}")
        
        return {
            'success': True,
            'transaction_id': reference or transaction_id,
            'reference': reference,
            'status': status,
            'amount': data_field.get('amount') or payload.get('amount'),
            'paid_at': data_field.get('transaction', {}).get('paid_at') or payload.get('paid_at'),
            'phone': payload.get('phone'),
        }


# Instância global do serviço
paysuite_service = PaySuiteService()
