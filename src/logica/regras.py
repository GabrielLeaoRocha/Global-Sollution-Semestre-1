"""Regras logicas de classificacao do status operacional da missao.

Aplica portas logicas AND/OR/NOT (Fase 2 — decisao.py) combinadas com
o motor de decisao em camadas (Fase 3 — decision_engine.py).
"""

from typing import Any

from src.config import (
    COMUNICACAO_CRITICA,
    RADIACAO_CRITICA,
    RESERVA_ALERTA,
    RESERVA_CRITICA,
    SEV_ALERTA,
    SEV_CRITICO,
    SEV_NORMAL,
)


def avaliar_ciclo(registro: dict[str, Any]) -> dict[str, Any]:
    """Classifica o status operacional de um ciclo aplicando regras booleanas.

    Variaveis booleanas (estilo Fase 2):
        SV = suporte_vida ativo
        EN = energia ativo
        CO = comunicacao ativa
        LAB = laboratorio ativo
        RB = reserva < 20%        (reserva baixa)
        RA = reserva < 50%        (reserva em alerta)
        RD = radiacao > 80        (radiacao perigosa)
        CB = qualidade_com < 30%  (comunicacao baixa)
        DF = consumo > geracao    (deficit energetico)

    Regras (5 regras AND/OR/NOT — paper exige minimo 3):
        R1  CRITICO = RB AND DF
        R2  CRITICO = (NOT SV) OR (NOT EN)
        R3  ALERTA  = (NOT CO) OR CB OR RD
        R4  ALERTA  = RA AND DF
        R5  ALERTA  = DF AND (NOT LAB)
        R6  NORMAL  = caso contrario

    Returns:
        Dict com chaves: ciclo, status, severidade_num, regra, descricao, acao.
    """
    booleanas = _extrair_booleanas(registro)

    # Avaliacao em ordem de prioridade (if/elif/else encadeado)
    if booleanas["rb"] and booleanas["df"]:
        return _construir_resultado(
            registro,
            status="CRITICO",
            severidade=SEV_CRITICO,
            regra="R1: reserva<20% AND consumo>geracao",
            descricao="Reserva critica com deficit energetico",
            acao="Ativar modo emergencia - desligar todos os sistemas nao essenciais, manter suporte a vida",
        )

    if (not booleanas["sv"]) or (not booleanas["en"]):
        return _construir_resultado(
            registro,
            status="CRITICO",
            severidade=SEV_CRITICO,
            regra="R2: (NOT suporte_vida) OR (NOT energia)",
            descricao="Falha em modulo vital",
            acao="Acionar protocolo de emergencia - intervencao manual urgente",
        )

    if (not booleanas["co"]) or booleanas["cb"] or booleanas["rd"]:
        motivos = []
        if not booleanas["co"]:
            motivos.append("modulo comunicacao inativo")
        if booleanas["cb"]:
            motivos.append("qualidade do sinal abaixo de 30%")
        if booleanas["rd"]:
            motivos.append("radiacao acima de 80")
        return _construir_resultado(
            registro,
            status="ALERTA",
            severidade=SEV_ALERTA,
            regra="R3: (NOT comunicacao) OR comunicacao_baixa OR radiacao_alta",
            descricao="Comunicacao/radiacao comprometidas: " + ", ".join(motivos),
            acao="Ativar comunicacao de emergencia e recolher equipamentos expostos",
        )

    if booleanas["ra"] and booleanas["df"]:
        return _construir_resultado(
            registro,
            status="ALERTA",
            severidade=SEV_ALERTA,
            regra="R4: reserva<50% AND consumo>geracao",
            descricao="Reserva moderada com deficit energetico",
            acao="Desligar laboratorio e sistemas nao essenciais para preservar reserva",
        )

    if booleanas["df"] and (not booleanas["lab"]):
        return _construir_resultado(
            registro,
            status="ALERTA",
            severidade=SEV_ALERTA,
            regra="R5: consumo>geracao AND (NOT laboratorio)",
            descricao="Consumo elevado mesmo com laboratorio desligado",
            acao="Revisar habitat e sistemas auxiliares - possivel vazamento",
        )

    return _construir_resultado(
        registro,
        status="NORMAL",
        severidade=SEV_NORMAL,
        regra="fallback: nenhuma condicao critica",
        descricao="Todos os parametros dentro da faixa segura",
        acao="Operacao normal - sem acao necessaria",
    )


def _extrair_booleanas(registro: dict[str, Any]) -> dict[str, bool]:
    """Extrai todas as variaveis booleanas do registro de telemetria."""
    reserva = registro["reserva_energia_pct"]
    consumo = registro["consumo_total_kwh"]
    geracao = registro["geracao_solar_kwh"] + registro["geracao_eolica_kwh"]
    return {
        "sv": registro["suporte_vida"] == 1,
        "en": registro["energia"] == 1,
        "co": registro["comunicacao"] == 1,
        "lab": registro["laboratorio"] == 1,
        "rb": reserva < RESERVA_CRITICA,
        "ra": reserva < RESERVA_ALERTA,
        "rd": registro["radiacao_nivel"] > RADIACAO_CRITICA,
        "cb": registro["qualidade_comunicacao_pct"] < COMUNICACAO_CRITICA,
        "df": consumo > geracao,
    }


def _construir_resultado(
    registro: dict[str, Any],
    *,
    status: str,
    severidade: int,
    regra: str,
    descricao: str,
    acao: str,
) -> dict[str, Any]:
    """Padroniza o dict de saida da avaliacao."""
    return {
        "ciclo": registro["ciclo"],
        "status": status,
        "severidade_num": severidade,
        "regra": regra,
        "descricao": descricao,
        "acao": acao,
    }
