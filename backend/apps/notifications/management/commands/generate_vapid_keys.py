import base64

from django.core.management.base import BaseCommand
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


class Command(BaseCommand):
    help = 'Gera um par de chaves VAPID para Web Push.'

    def handle(self, *args, **options):
        private_key = ec.generate_private_key(ec.SECP256R1())
        private_der = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )
        public_key = base64.urlsafe_b64encode(public_bytes).rstrip(b'=').decode('ascii')
        private_key_b64url = base64.urlsafe_b64encode(private_der).rstrip(b'=').decode('ascii')

        self.stdout.write(f'WEBPUSH_VAPID_PUBLIC_KEY={public_key}')
        self.stdout.write(f'WEBPUSH_VAPID_PRIVATE_KEY={private_key_b64url}')
        self.stdout.write('Guarde a chave privada num gestor de segredos; não a publique nem a versione.')