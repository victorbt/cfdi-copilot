from decimal import Decimal

import pytest
from pydantic import ValidationError

from cfdi_copilot.models import Comprobante, TipoComprobante
from cfdi_copilot.synthetic import fake_comprobante


def test_synthetic_invoice_is_valid() -> None:
    cfdi = Comprobante.model_validate(fake_comprobante(seed=1))
    assert cfdi.version == "4.0"
    assert cfdi.tipo is TipoComprobante.INGRESO
    assert cfdi.total > cfdi.subtotal


@pytest.mark.parametrize("seed", range(50))
def test_many_seeds_validate(seed: int) -> None:
    Comprobante.model_validate(fake_comprobante(seed))


def test_rfc_is_normalized_to_upper() -> None:
    raw = fake_comprobante(2)
    raw["Emisor"]["Rfc"] = raw["Emisor"]["Rfc"].lower()
    assert Comprobante.model_validate(raw).emisor.rfc.isupper()


def test_bad_rfc_fails() -> None:
    raw = fake_comprobante(3)
    raw["Emisor"]["Rfc"] = "NO-ES-RFC"
    with pytest.raises(ValidationError, match="RFC"):
        Comprobante.model_validate(raw)


def test_wrong_total_fails() -> None:
    raw = fake_comprobante(4)
    raw["Total"] = str(Decimal(raw["Total"]) + 1)
    with pytest.raises(ValidationError, match="Total"):
        Comprobante.model_validate(raw)


def test_extra_fields_are_rejected() -> None:
    raw = fake_comprobante(5)
    raw["CampoInventado"] = "x"
    with pytest.raises(ValidationError):
        Comprobante.model_validate(raw)


def test_invoice_is_immutable() -> None:
    cfdi = Comprobante.model_validate(fake_comprobante(6))
    with pytest.raises(ValidationError):
        cfdi.total = Decimal("1")  # type: ignore[misc]


def test_json_roundtrip_by_alias() -> None:
    cfdi = Comprobante.model_validate(fake_comprobante(7))
    dumped = cfdi.model_dump(mode="json", by_alias=True, exclude_none=True)
    assert "Rfc" in dumped["Emisor"]
    # computed fields (importe, iva) are dumped too, but must not break re-validation
    for c in dumped["Conceptos"]:
        c.pop("importe"), c.pop("iva")
    assert Comprobante.model_validate(dumped) == cfdi
