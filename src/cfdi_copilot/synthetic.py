"""Synthetic CFDI generator. Never use real taxpayer data in this repo."""

from __future__ import annotations

import random
import string
from decimal import Decimal
from typing import Any

from cfdi_copilot.models import CENT

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_PRODUCTS = [
    ("43211503", "Laptop de prueba"),
    ("81112101", "Servicio de soporte técnico (ficticio)"),
    ("80111600", "Consultoría de software (ficticia)"),
    ("44121600", "Papelería de oficina"),
]


def fake_rfc(rng: random.Random, persona_moral: bool = True) -> str:
    letters = "".join(rng.choices(_LETTERS, k=3 if persona_moral else 4))
    date = f"{rng.randint(80, 99):02d}{rng.randint(1, 12):02d}{rng.randint(1, 28):02d}"
    homoclave = "".join(rng.choices(string.ascii_uppercase + string.digits, k=3))
    return letters + date + homoclave


def fake_comprobante(seed: int) -> dict[str, Any]:
    """Return a raw dict (as it would come from parsed XML or an LLM) for Comprobante."""
    rng = random.Random(seed)
    conceptos = []
    subtotal = Decimal("0")
    iva = Decimal("0")
    for _ in range(rng.randint(1, 4)):
        clave, desc = rng.choice(_PRODUCTS)
        cantidad = Decimal(rng.randint(1, 5))
        valor = Decimal(rng.randint(100, 20000)) + Decimal(rng.randint(0, 99)) / 100
        importe = (cantidad * valor).quantize(CENT)
        subtotal += importe
        iva += (importe * Decimal("0.16")).quantize(CENT)
        conceptos.append(
            {
                "ClaveProdServ": clave,
                "Cantidad": str(cantidad),
                "Descripcion": desc,
                "ValorUnitario": str(valor),
            }
        )
    return {
        "Serie": "SYN",
        "Folio": str(seed),
        "TipoDeComprobante": "I",
        "LugarExpedicion": f"{rng.randint(1000, 99999):05d}",
        "Emisor": {
            "Rfc": fake_rfc(rng),
            "Nombre": "EMPRESA SINTETICA SA DE CV",
            "RegimenFiscal": "601",
        },
        "Receptor": {
            "Rfc": fake_rfc(rng, persona_moral=False),
            "Nombre": "PERSONA FICTICIA",
            "DomicilioFiscalReceptor": f"{rng.randint(1000, 99999):05d}",
            "RegimenFiscalReceptor": "612",
            "UsoCFDI": "G03",
        },
        "Conceptos": conceptos,
        "SubTotal": str(subtotal),
        "Total": str(subtotal + iva),
    }
