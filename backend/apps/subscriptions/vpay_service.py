"""
Serviço de integração com VPay Moçambique.

Fluxo implementado (server-to-server, via checkout hospedado):
  1. Autenticação  -> POST /v1/auth/token (client_id + client_secret)
  2. Criar pedido  -> POST /v1/orders (customer + items; total calculado no servidor)
  3. Checkout      -> URL hospedado retornado pela API ou https://checkout.vpay.co.mz/{orderId}
  4. Confirmação   -> GET /v1/orders/{order_id}/status e/ou webhook verificado (HMAC-SHA256)

Referência oficial:
  https://vpay.co.mz/docs/api-reference
  https://vpay.co.mz/docs/authentication
  https://vpay.co.mz/docs/api-reference/polling
  https://vpay.co.mz/docs/webhooks

SEGURANÇA: este módulo nunca regista (log) o access_token, refresh_token ou
client_secret. O token é mantido apenas em memória e renovado quando expira.
"""
import time
import hmac
import hashlib
import threading
from decimal import Decimal, InvalidOperation
from typing import Dict, Optional

import requests
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class VPayServiceError(Exception):
    """Erro controlado na comunicação com a VPay."""


class VPayService:
    """Cliente para a API VPay Moçambique."""

    # Valores de status devolvidos pela VPay (conforme polling/webhook).
    STATUS_PAID = 'paid'
    STATUS_PENDING = 'pending'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_EXPIRED = 'expired'

    def __init__(self):
        self.base_url = (getattr(settings, 'VPAY_BASE_URL', 'https://api.vpay.co.mz') or '').rstrip('/')
        self.client_id = getattr(settings, 'VPAY_CLIENT_ID', '') or ''
        self.client_secret = getattr(settings, 'VPAY_CLIENT_SECRET', '') or ''
        self.application_id = getattr(settings, 'VPAY_APPLICATION_ID', '') or ''
        self.checkout_base_url = (getattr(settings, 'VPAY_CHECKOUT_BASE_URL', 'https://checkout.vpay.co.mz') or '').rstrip('/')
        self.webhook_secret = getattr(settings, 'VPAY_WEBHOOK_SECRET', '') or ''
        self.timeout = float(getattr(settings, 'VPAY_TIMEOUT', 30))
        self.auth_token_path = getattr(settings, 'VPAY_AUTH_TOKEN_PATH', '/v1/auth/token')

        # Cache de token em memória (nunca persistido). Protegido por lock para
        # evitar pedidos de token concorrentes.
        self._token_lock = threading.Lock()
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    @staticmethod
    def _extract_data(response_json: Dict) -> Dict:
        """Extrai o objeto 'data' da resposta, aceitando também chaves no topo."""
        if not isinstance(response_json, dict):
            return {}
        data = response_json.get('data')
        if isinstance(data, dict):
            return data
        return response_json

    # ------------------------------------------------------------------
    # Autenticação
    # ------------------------------------------------------------------
    def _request_access_token(self) -> Dict:
        """Pede um access token via POST /v1/auth/token. Nunca regista o segredo."""
        url = f'{self.base_url}{self.auth_token_path}'
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        logger.info('A obter access token VPay (credenciais omitidas do log).')
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _get_access_token(self) -> str:
        """
        Devolve um access token válido, renovando-o quando necessário.

        Guarda o token apenas em memória e nunca o escreve em logs.
        """
        now = time.time()
        if self._access_token and now < self._token_expires_at:
            return self._access_token

        with self._token_lock:
            # Revalidar dentro do lock (outra thread pode ter renovado).
            if self._access_token and time.time() < self._token_expires_at:
                return self._access_token

            data = self._request_access_token()
            data_obj = self._extract_data(data)

            access_token = data_obj.get('access_token') or data.get('access_token')
            if not access_token:
                raise VPayServiceError('Resposta de autenticação sem access_token.')

            # expires_in em segundos; fallback conservador de 1 hora.
            try:
                expires_in = int(data_obj.get('expires_in', data.get('expires_in', 3600)))
            except (TypeError, ValueError):
                expires_in = 3600
            if expires_in <= 0:
                expires_in = 3600

            # Margem de segurança de 60s para nunca usar um token prestes a expirar.
            self._access_token = access_token
            self._token_expires_at = now + max(expires_in - 60, 30)

        return self._access_token

    def _headers(self, token: str) -> Dict:
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    # ------------------------------------------------------------------
    # Pedidos
    # ------------------------------------------------------------------
    def create_order(
        self,
        *,
        customer: Dict,
        items: list,
        merchant_order_reference: str,
        currency: str = 'MZN',
    ) -> Dict:
        """
        Cria um pedido na VPay (POST /v1/orders).

        O total é calculado no servidor a partir de `items` (quantidade * preço),
        que deve ser validado pelo chamador antes de invocar este método.

        Returns:
            dict com {success, order_id, checkout_url, status, raw_response, error}
        """
        if not self._is_configured():
            return {'success': False, 'error': 'VPay não configurada (VPAY_CLIENT_ID/VPAY_CLIENT_SECRET).'}

        token = self._get_access_token()

        # Total calculado no servidor (nunca confiar em valores do cliente).
        total = Decimal('0')
        normalized_items = []
        for item in items:
            try:
                quantity = int(item.get('quantity', 1))
                price = Decimal(str(item.get('price', '0')))
            except (InvalidOperation, TypeError, ValueError) as exc:
                raise VPayServiceError(f'Item inválido: {exc}') from exc
            if quantity <= 0 or price < 0:
                raise VPayServiceError('Quantidade/preço de item inválido.')
            total += price * quantity
            normalized_items.append({**item, 'quantity': quantity, 'price': float(price)})

        payload = {
            'source': {'source': 'api'},
            'customer': customer,
            'items': normalized_items,
            # Serviço digital (assinatura): sem entrega/endereço.
            'shippingAddressDisabled': True,
            'deliveryInfoDisabled': True,
            'currency': currency,
        }
        if self.application_id:
            payload['metadata'] = payload.get('metadata') or {}
            payload['metadata']['applicationId'] = self.application_id
        if merchant_order_reference:
            payload['metadata'] = payload.get('metadata') or {}
            payload['metadata']['merchantOrderReference'] = merchant_order_reference

        logger.info(
            'A criar pedido VPay: ref=%s total=%s %s itens=%s',
            merchant_order_reference, total, currency, len(normalized_items),
        )

        try:
            response = requests.post(
                f'{self.base_url}/v1/orders',
                json=payload,
                headers=self._headers(token),
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as exc:
            # Não repetir uma operação financeira ambígua: devolver erro e deixar
            # o chamador consultar o estado antes de nova tentativa.
            return {'success': False, 'error': 'Timeout ao contactar a VPay.', 'ambiguous': True}
        except requests.exceptions.RequestException as exc:
            return {'success': False, 'error': f'Falha de rede ao contactar a VPay: {exc}'}

        try:
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as exc:
            return {'success': False, 'error': f'Erro HTTP {response.status_code} ao criar pedido.'}
        except ValueError:
            return {'success': False, 'error': 'Resposta inválida (não-JSON) ao criar pedido.'}

        data_obj = self._extract_data(data)
        order_id = (
            data_obj.get('orderId')
            or data_obj.get('order_id')
            or data_obj.get('id')
            or data.get('orderId')
            or data.get('id')
        )

        if not order_id:
            return {'success': False, 'error': 'Resposta sem orderId.', 'raw_response': data}

        checkout_url = (
            data_obj.get('checkout')
            or data_obj.get('checkout_url')
            or data.get('checkout')
            or data.get('checkout_url')
            or f'{self.checkout_base_url}/{order_id}'
        )

        return {
            'success': True,
            'order_id': str(order_id),
            'checkout_url': checkout_url,
            'status': data_obj.get('status', self.STATUS_PENDING),
            'raw_response': data,
        }

    # ------------------------------------------------------------------
    # Consulta de estado
    # ------------------------------------------------------------------
    def get_order_status(self, order_id: str) -> Dict:
        """Consulta o estado de um pedido (GET /v1/orders/{order_id}/status)."""
        if not self._is_configured():
            return {'success': False, 'error': 'VPay não configurada.'}

        token = self._get_access_token()
        try:
            response = requests.get(
                f'{self.base_url}/v1/orders/{order_id}/status',
                headers=self._headers(token),
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Timeout ao consultar o estado do pedido.'}
        except requests.exceptions.RequestException as exc:
            return {'success': False, 'error': f'Falha de rede ao consultar o estado: {exc}'}

        try:
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException:
            return {'success': False, 'error': f'Erro HTTP {response.status_code} ao consultar o estado.'}
        except ValueError:
            return {'success': False, 'error': 'Resposta inválida (não-JSON) ao consultar o estado.'}

        data_obj = self._extract_data(data)
        status_value = data_obj.get('status') or data.get('status')
        return {
            'success': True,
            'status': status_value,
            'amount': data_obj.get('amount'),
            'transaction_id': data_obj.get('transactionId') or data_obj.get('transaction_id'),
            'last_updated': data_obj.get('lastUpdated') or data_obj.get('last_updated'),
            'raw_response': data,
        }

    # ------------------------------------------------------------------
    # Webhook
    # ------------------------------------------------------------------
    def verify_webhook_signature(self, raw_body: bytes, signature: str) -> bool:
        """
        Verifica a assinatura HMAC-SHA256 do webhook.

        A assinatura tem o formato `sha256=<hex>` e é calculada sobre os bytes
        exatos do corpo HTTP (antes de converter para JSON).
        """
        if not self.webhook_secret or not signature:
            return False
        if not signature.startswith('sha256='):
            return False

        received = signature[len('sha256='):]
        try:
            expected = hmac.new(
                self.webhook_secret.encode('utf-8'),
                raw_body,
                hashlib.sha256,
            ).hexdigest()
        except Exception:
            return False

        return hmac.compare_digest(expected, received)

    def parse_webhook(self, payload: Dict) -> Dict:
        """
        Extrai os campos relevantes de um webhook VPay.

        Evento documentado: `payment.confirmed` (status `paid`).
        """
        if not isinstance(payload, dict):
            return {'success': False, 'error': 'Payload inválido.'}

        event = payload.get('event') or ''
        order_id = payload.get('orderId') or payload.get('sourceId')
        status_value = payload.get('status')
        transaction_reference = payload.get('transactionReference')
        customer = payload.get('customer') if isinstance(payload.get('customer'), dict) else {}

        return {
            'success': True,
            'event': event,
            'order_id': order_id,
            'status': status_value,
            'amount': payload.get('amount'),
            'currency': payload.get('currency'),
            'transaction_id': payload.get('transactionId'),
            'transaction_reference': transaction_reference,
            'payment_method': payload.get('paymentMethod'),
            'customer': customer,
            'raw_data': payload,
        }


# Instância global para uso na aplicação.
vpay_service = VPayService()
