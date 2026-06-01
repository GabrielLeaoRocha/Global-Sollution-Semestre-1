"""Widgets reutilizaveis seguindo o Aurora Siger Style Guide.

Componentes (paginas 5, 6, 8, 11 do guia):
    - make_kpi_card        Card com acento rosa lateral + valor grande
    - make_nav_item        Item de menu da sidebar (com hover + estado ativo)
    - make_status_dot      Bolinha colorida (Canvas) para indicar status
    - make_section_card    Card generico com titulo opcional
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable

from src.gui.theme import (
    BORDER,
    MUTED,
    PINK,
    SIDEBAR_BG,
    SPACE,
    SURFACE,
    SURFACE_HI,
    WHITE,
    Fontes,
)


# =============================================================================
# 6. CARD KPI
# =============================================================================

def make_kpi_card(
    parent: tk.Misc,
    title: str,
    value: str,
    unit: str = "",
    *,
    accent: str = PINK,
    value_color: str = WHITE,
) -> tk.Frame:
    """Card KPI com barra lateral colorida (simula sombra/destaque).

    Layout: [acento 3px] [conteudo: TITULO em mute + valor grande + unidade]
    """
    wrap = tk.Frame(parent, bg=SURFACE, highlightthickness=0)

    # Barra lateral colorida (3px)
    tk.Frame(wrap, bg=accent, width=3).pack(side="left", fill="y")

    inner = tk.Frame(wrap, bg=SURFACE)
    inner.pack(side="left", fill="both", expand=True,
               padx=SPACE["lg"], pady=SPACE["md"] + 2)

    tk.Label(
        inner, text=title.upper(),
        bg=SURFACE, fg=MUTED, font=Fontes.label,
    ).pack(anchor="w")

    row = tk.Frame(inner, bg=SURFACE)
    row.pack(anchor="w", pady=(SPACE["xs"] + 2, 0))

    tk.Label(
        row, text=value,
        bg=SURFACE, fg=value_color, font=Fontes.display,
    ).pack(side="left")

    if unit:
        tk.Label(
            row, text=" " + unit,
            bg=SURFACE, fg=MUTED, font=Fontes.body,
        ).pack(side="left", pady=(SPACE["sm"], 0))

    return wrap


# =============================================================================
# 8. NAV ITEM
# =============================================================================

def make_nav_item(
    parent: tk.Misc,
    text: str,
    callback: Callable[[], None],
    *,
    active: bool = False,
) -> tk.Frame:
    """Item da sidebar com hover + acento rosa quando ativo.

    Quando ativo: bg=SURFACE, texto branco bold, barra rosa de 3px na esquerda.
    Quando inativo: bg=SIDEBAR_BG, texto MUTED, sem barra.
    """
    bg = SURFACE if active else SIDEBAR_BG
    fg = WHITE if active else MUTED
    fonte = Fontes.body_bold if active else Fontes.body

    row = tk.Frame(parent, bg=bg, height=36)
    row.pack(fill="x")
    row.pack_propagate(False)

    accent = tk.Frame(row, bg=PINK if active else bg, width=3)
    accent.pack(side="left", fill="y")

    label = tk.Label(
        row, text=text, bg=bg, fg=fg,
        anchor="w", font=fonte,
        padx=SPACE["md"],
    )
    label.pack(side="left", fill="both", expand=True)

    # Cursor de mao + acoes de hover
    for widget in (row, label):
        widget.configure(cursor="hand2")
        widget.bind("<Button-1>", lambda _e: callback())

    if not active:
        def on_enter(_event: object) -> None:
            row.configure(bg=SURFACE)
            label.configure(bg=SURFACE, fg=WHITE)
            accent.configure(bg=SURFACE)

        def on_leave(_event: object) -> None:
            row.configure(bg=SIDEBAR_BG)
            label.configure(bg=SIDEBAR_BG, fg=MUTED)
            accent.configure(bg=SIDEBAR_BG)

        for widget in (row, label, accent):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    return row


# =============================================================================
# 11. STATUS DOT
# =============================================================================

def make_status_dot(parent: tk.Misc, color: str, *, bg: str = SURFACE, size: int = 10) -> tk.Canvas:
    """Canvas com uma bolinha colorida (status indicator)."""
    canvas = tk.Canvas(
        parent, width=size, height=size,
        bg=bg, highlightthickness=0, borderwidth=0,
    )
    canvas.create_oval(1, 1, size - 1, size - 1, fill=color, outline="")
    return canvas


# =============================================================================
# CARD GENERICO COM TITULO
# =============================================================================

def make_section_card(parent: tk.Misc, title: str | None = None) -> tk.Frame:
    """Card generico (bg=SURFACE) com titulo opcional e divisor.

    Retorna o frame INTERNO onde o caller adiciona o conteudo.
    """
    wrap = tk.Frame(parent, bg=SURFACE, highlightthickness=0)

    if title:
        header = tk.Frame(wrap, bg=SURFACE)
        header.pack(fill="x")
        tk.Label(
            header, text=title.upper(),
            bg=SURFACE, fg=MUTED, font=Fontes.label,
            padx=SPACE["lg"], pady=SPACE["md"],
        ).pack(anchor="w")
        tk.Frame(wrap, bg=BORDER, height=1).pack(fill="x", padx=SPACE["lg"])

    inner = tk.Frame(wrap, bg=SURFACE)
    inner.pack(fill="both", expand=True,
               padx=SPACE["lg"], pady=(SPACE["md"], SPACE["lg"]))

    # Devolvemos tanto o wrap (para empacotar) quanto o inner (para preencher).
    # Para simplificar, anexamos inner ao wrap.
    wrap._inner = inner  # type: ignore[attr-defined]
    return wrap


def get_inner(card: tk.Frame) -> tk.Frame:
    """Acessa o frame interno de um make_section_card()."""
    return getattr(card, "_inner", card)


# =============================================================================
# DIVISOR HORIZONTAL
# =============================================================================

def divisor(parent: tk.Misc, *, bg: str = BORDER, height: int = 1) -> tk.Frame:
    """Linha divisoria horizontal sutil."""
    return tk.Frame(parent, bg=bg, height=height)
