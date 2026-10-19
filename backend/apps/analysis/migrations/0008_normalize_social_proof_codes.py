"""Normaliza ticket_code (9 dígitos começados por 7) e reserve_code (prefixo BW7)."""

from django.db import migrations


TICKET_CODE_PREFIX = '7'
RESERVE_CODE_PREFIX = 'BW7'


def _hash_hex(snapshot_hash: str) -> str:
    import hashlib
    import re

    raw = str(snapshot_hash or '')
    if re.fullmatch(r'[0-9a-fA-F]{16,}', raw):
        return raw.upper()
    return hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()


def forwards(apps, schema_editor):
    SocialProofTicket = apps.get_model('analysis', 'SocialProofTicket')

    for ticket in SocialProofTicket.objects.all():
        digest = _hash_hex(ticket.snapshot_hash)
        ticket_code = f'{TICKET_CODE_PREFIX}{int(digest, 16) % 10**8:08d}'
        reserve_code = f'{RESERVE_CODE_PREFIX}{digest[6:13]}'

        if ticket.ticket_code == ticket_code and ticket.reserve_code == reserve_code:
            continue

        if SocialProofTicket.objects.filter(ticket_code=ticket_code).exclude(pk=ticket.pk).exists():
            continue

        ticket.ticket_code = ticket_code
        ticket.reserve_code = reserve_code
        ticket.save(update_fields=['ticket_code', 'reserve_code'])


def backwards(apps, schema_editor):
    """Não reversível: o formato antigo não pode ser reconstruído."""


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0007_remove_socialproofticket_watermark_required'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
