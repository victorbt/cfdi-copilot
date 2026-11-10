"""CFDI 4.0 domain models (a simplified subset, enough for week 1).

Only synthetic data ever goes through these models. Field names follow the
Anexo 20 attribute names in Spanish so they map 1:1 to the XML later on.
"""

from __future__ import annotations

import re
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)

# RFC: 3 letters (persona moral) or 4 letters (persona física), 6-digit date, 3-char homoclave.
RFC_PATTERN = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")
CP_PATTERN = re.compile(r"^\d{5}$")

CENT = Decimal("0.01")


def _validate_rfc(value: str) -> str:
    value = value.strip().upper()
    if not RFC_PATTERN.fullmatch(value):
        raise ValueError(f"RFC con formato inválido: {value!r}")
    return value


Rfc = Annotated[str, AfterValidator(_validate_rfc)]
CodigoPostal = Annotated[str, Field(pattern=CP_PATTERN.pattern)]
Money = Annotated[Decimal, Field(ge=0, max_digits=18, decimal_places=6)]


class TipoComprobante(StrEnum):
    INGRESO = "I"
    EGRESO = "E"
    TRASLADO = "T"
    NOMINA = "N"
    PAGO = "P"


class Moneda(StrEnum):
    MXN = "MXN"
    USD = "USD"


class _CfdiModel(BaseModel):
    # frozen: an issued invoice is immutable. extra=forbid: fail loudly on typos.
    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)


class Emisor(_CfdiModel):
    rfc: Rfc = Field(alias="Rfc")
    nombre: str = Field(alias="Nombre", min_length=1, max_length=254)
    regimen_fiscal: str = Field(alias="RegimenFiscal", pattern=r"^\d{3}$")


class Receptor(_CfdiModel):
    rfc: Rfc = Field(alias="Rfc")
    nombre: str = Field(alias="Nombre", min_length=1, max_length=254)
    domicilio_fiscal: CodigoPostal = Field(alias="DomicilioFiscalReceptor")
    regimen_fiscal: str = Field(alias="RegimenFiscalReceptor", pattern=r"^\d{3}$")
    uso_cfdi: str = Field(alias="UsoCFDI", pattern=r"^[A-Z0-9]{3,4}$")


class Concepto(_CfdiModel):
    clave_prod_serv: str = Field(alias="ClaveProdServ", pattern=r"^\d{8}$")
    cantidad: Decimal = Field(alias="Cantidad", gt=0)
    descripcion: str = Field(alias="Descripcion", min_length=1, max_length=1000)
    valor_unitario: Money = Field(alias="ValorUnitario")
    tasa_iva: Decimal = Field(default=Decimal("0.16"), alias="TasaIVA", ge=0, le=Decimal("0.16"))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def importe(self) -> Decimal:
        return (self.cantidad * self.valor_unitario).quantize(CENT)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def iva(self) -> Decimal:
        return (self.importe * self.tasa_iva).quantize(CENT)


class Comprobante(_CfdiModel):
    """A simplified CFDI 4.0 <cfdi:Comprobante>."""

    version: str = Field(default="4.0", alias="Version", pattern=r"^4\.0$")
    serie: str | None = Field(default=None, alias="Serie", max_length=25)
    folio: str | None = Field(default=None, alias="Folio", max_length=40)
    tipo: TipoComprobante = Field(alias="TipoDeComprobante")
    moneda: Moneda = Field(default=Moneda.MXN, alias="Moneda")
    lugar_expedicion: CodigoPostal = Field(alias="LugarExpedicion")
    emisor: Emisor = Field(alias="Emisor")
    receptor: Receptor = Field(alias="Receptor")
    conceptos: list[Concepto] = Field(alias="Conceptos", min_length=1)
    subtotal: Money = Field(alias="SubTotal")
    total: Money = Field(alias="Total")

    @model_validator(mode="after")
    def _check_totals(self) -> Self:
        expected_subtotal = sum((c.importe for c in self.conceptos), Decimal("0"))
        expected_total = expected_subtotal + sum((c.iva for c in self.conceptos), Decimal("0"))
        if self.subtotal.quantize(CENT) != expected_subtotal:
            raise ValueError(f"SubTotal {self.subtotal} != suma de importes {expected_subtotal}")
        if self.total.quantize(CENT) != expected_total:
            raise ValueError(f"Total {self.total} != subtotal + IVA {expected_total}")
        return self
