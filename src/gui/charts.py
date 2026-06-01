"""Graficos nativos desenhados no tk.Canvas — sem matplotlib.

O guia de estilo (pagina 8) recomenda matplotlib, mas mantemos 100% stdlib
desenhando manualmente. Resultado fica bom e nao adiciona dependencia.

Componente:
    LineChart — pontos historicos + projecao (linha pontilhada rosa)
"""

from __future__ import annotations

import tkinter as tk
from typing import Sequence

from src.gui.theme import BORDER, MUTED, PINK, SURFACE, WHITE, Fontes


class LineChart(tk.Canvas):
    """Grafico de linha com area preenchida e ponto de projecao destacado.

    Eixos automaticos com base nos valores. Pontuação visual:
        - linha principal: rosa cheia, 2px
        - area abaixo: rosa com alpha simulado (cor mais escura)
        - grid horizontal: tracejado sutil
        - ponto de projecao: estrela/diamante rosa
    """

    PADDING_LEFT = 48
    PADDING_RIGHT = 24
    PADDING_TOP = 24
    PADDING_BOTTOM = 36

    def __init__(
        self,
        master: tk.Misc,
        *,
        width: int = 720,
        height: int = 280,
        bg: str = SURFACE,
    ) -> None:
        super().__init__(
            master, width=width, height=height, bg=bg,
            highlightthickness=0, borderwidth=0,
        )
        self._width = width
        self._height = height

    def plot(
        self,
        x_vals: Sequence[float],
        y_vals: Sequence[float],
        *,
        previsao: tuple[float, float] | None = None,
        y_label: str = "",
        x_label: str = "",
        limites_y: tuple[float, float] | None = None,
    ) -> None:
        """Desenha a serie. Se `previsao` for dada, plota o ponto extra.

        Args:
            x_vals/y_vals: dados historicos
            previsao: (x, y) do ponto previsto (sera ligado por linha tracejada)
            y_label/x_label: titulos dos eixos
            limites_y: forca o range vertical; se None, usa min/max dos dados
        """
        self.delete("all")

        # Range
        todos_x = list(x_vals) + ([previsao[0]] if previsao else [])
        todos_y = list(y_vals) + ([previsao[1]] if previsao else [])

        x_min, x_max = min(todos_x), max(todos_x)
        if limites_y is not None:
            y_min, y_max = limites_y
        else:
            y_min = min(0.0, min(todos_y))
            y_max = max(100.0, max(todos_y))

        # Padding nos limites
        if y_max - y_min < 1:
            y_max += 1
        # Converte (dado) -> (pixel)
        plot_w = self._width - self.PADDING_LEFT - self.PADDING_RIGHT
        plot_h = self._height - self.PADDING_TOP - self.PADDING_BOTTOM

        def x_px(x: float) -> float:
            if x_max == x_min:
                return self.PADDING_LEFT + plot_w / 2
            return self.PADDING_LEFT + (x - x_min) / (x_max - x_min) * plot_w

        def y_px(y: float) -> float:
            return self.PADDING_TOP + (1 - (y - y_min) / (y_max - y_min)) * plot_h

        # ---- grid horizontal (5 linhas) ----
        for i in range(6):
            valor = y_min + (y_max - y_min) * i / 5
            y = y_px(valor)
            self.create_line(
                self.PADDING_LEFT, y, self._width - self.PADDING_RIGHT, y,
                fill=BORDER, dash=(2, 4),
            )
            self.create_text(
                self.PADDING_LEFT - 8, y, anchor="e",
                text=f"{valor:.0f}", fill=MUTED, font=Fontes.label,
            )

        # ---- eixo X labels ----
        for x in x_vals:
            self.create_text(
                x_px(x), self._height - self.PADDING_BOTTOM + 12, anchor="n",
                text=f"{int(x)}", fill=MUTED, font=Fontes.label,
            )

        if previsao:
            self.create_text(
                x_px(previsao[0]), self._height - self.PADDING_BOTTOM + 12, anchor="n",
                text=f"{int(previsao[0])}*", fill=PINK, font=Fontes.label,
            )

        # ---- titulos dos eixos ----
        if y_label:
            self.create_text(
                12, self.PADDING_TOP - 12, anchor="w",
                text=y_label, fill=MUTED, font=Fontes.label,
            )
        if x_label:
            self.create_text(
                self._width / 2, self._height - 6, anchor="s",
                text=x_label, fill=MUTED, font=Fontes.label,
            )

        # ---- area preenchida (poligono) ----
        pontos_poligono: list[float] = []
        for x, y in zip(x_vals, y_vals):
            pontos_poligono.extend([x_px(x), y_px(y)])
        if pontos_poligono:
            # Fecha o poligono na base
            pontos_poligono.extend([
                x_px(x_vals[-1]), y_px(y_min),
                x_px(x_vals[0]), y_px(y_min),
            ])
            self.create_polygon(
                *pontos_poligono,
                fill="#3a1929",  # tom de rosa muito escuro (simula alpha sobre SURFACE)
                outline="",
            )

        # ---- linha principal ----
        if len(x_vals) >= 2:
            linha_pts: list[float] = []
            for x, y in zip(x_vals, y_vals):
                linha_pts.extend([x_px(x), y_px(y)])
            self.create_line(*linha_pts, fill=PINK, width=2, smooth=False)

        # ---- pontos dos dados ----
        for x, y in zip(x_vals, y_vals):
            self.create_oval(
                x_px(x) - 3, y_px(y) - 3, x_px(x) + 3, y_px(y) + 3,
                fill=SURFACE, outline=PINK, width=2,
            )

        # ---- projecao ----
        if previsao:
            px, py = previsao
            ult_x, ult_y = x_vals[-1], y_vals[-1]

            # Linha tracejada conectando ultimo ponto -> projecao
            self.create_line(
                x_px(ult_x), y_px(ult_y), x_px(px), y_px(py),
                fill=PINK, width=2, dash=(4, 4),
            )

            # Marca de projecao (diamante)
            r = 6
            self.create_polygon(
                x_px(px), y_px(py) - r,
                x_px(px) + r, y_px(py),
                x_px(px), y_px(py) + r,
                x_px(px) - r, y_px(py),
                fill=PINK, outline=WHITE, width=1,
            )

            # Rotulo do valor previsto
            self.create_text(
                x_px(px), y_px(py) - 16, anchor="s",
                text=f"{py:.1f}", fill=PINK, font=Fontes.body_bold,
            )

        # Borda discreta
        self.create_rectangle(
            self.PADDING_LEFT, self.PADDING_TOP,
            self._width - self.PADDING_RIGHT, self._height - self.PADDING_BOTTOM,
            outline=BORDER, width=1,
        )
