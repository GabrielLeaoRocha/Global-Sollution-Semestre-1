"""Tema visual da interface grafica — Aurora Siger Style Guide.

Centraliza paleta, fontes, escala de espacamento e configuracao global do
ttk.Style. Importado uma vez no entrypoint da GUI.

Conformidade com o guia de estilo (paginas 1-4):
    - paleta #e90061 / #1e1e1e / #f8f8f8 + tons de superficie
    - rosa como ACENTO (max ~10% da area visivel)
    - fallback gracioso de fontes (Space Grotesk / Inter / fallback do SO)
    - tema 'clam' do ttk (unico que aceita customizacao completa de cor)
"""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

# =============================================================================
# 1. PALETA — tokens semanticos
# =============================================================================

PINK = "#e90061"          # acao primaria, destaques, alertas, criticos
PINK_HOVER = "#c8004f"
PINK_PRESSED = "#a80042"

GREY = "#1e1e1e"          # background principal
WHITE = "#f8f8f8"         # texto sobre fundo escuro

SURFACE = "#282828"       # cards, paineis
SURFACE_HI = "#383838"    # hover, linhas alternadas (zebra)
SIDEBAR_BG = "#161616"    # sidebar (mais escura que GREY)
STATUS_BG = "#141414"     # status bar
BORDER = "#3a3a3a"        # divisores sutis

MUTED = "#aaaaaa"         # texto secundario, labels

SUCCESS = "#2ec48a"       # estados OK
WARNING = "#f0b428"       # estados de atencao
CRITICAL = PINK           # estados criticos (alias do PINK)

# =============================================================================
# 3. ESPACAMENTO — escala fixa em pixels (Tkinter usa px diretamente)
# =============================================================================

SPACE = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "xxl": 32}


# =============================================================================
# 2. TIPOGRAFIA — fallback gracioso por familia de fontes
# =============================================================================

def _pick(family_list: list[str], size: int, weight: str = "normal") -> tkfont.Font:
    """Escolhe a primeira fonte disponivel no SO; cai para TkDefaultFont."""
    disponiveis = set(tkfont.families())
    for familia in family_list:
        if familia in disponiveis:
            return tkfont.Font(family=familia, size=size, weight=weight)
    return tkfont.Font(family="TkDefaultFont", size=size, weight=weight)


# As fontes precisam ser criadas APOS a inicializacao do Tk(). Por isso,
# expomos uma funcao `criar_fontes()` que deve ser chamada uma vez depois
# que a janela raiz existir.

class Fontes:
    """Container das fontes da aplicacao (preenchido por criar_fontes())."""
    display: tkfont.Font
    h1: tkfont.Font
    h2: tkfont.Font
    body: tkfont.Font
    body_bold: tkfont.Font
    label: tkfont.Font
    mono: tkfont.Font


def criar_fontes() -> type[Fontes]:
    """Inicializa as fontes — chamar depois de criar tk.Tk()."""
    sans_display = ["Space Grotesk", "Inter", "SF Pro Display", "Segoe UI", "Helvetica Neue", "Helvetica"]
    sans_text = ["Inter", "SF Pro Text", "Segoe UI", "Helvetica Neue", "Helvetica", "Arial"]
    mono = ["JetBrains Mono", "SF Mono", "Menlo", "Consolas", "DejaVu Sans Mono", "Courier"]

    Fontes.display = _pick(sans_display, 22, "bold")
    Fontes.h1 = _pick(sans_display, 18, "bold")
    Fontes.h2 = _pick(sans_text, 14, "bold")
    Fontes.body = _pick(sans_text, 11)
    Fontes.body_bold = _pick(sans_text, 11, "bold")
    Fontes.label = _pick(sans_text, 9)
    Fontes.mono = _pick(mono, 11)
    return Fontes


# =============================================================================
# 4. SETUP DO ttk.Style — chamar uma vez apos criar a raiz
# =============================================================================

def aplicar_estilos(root: tk.Tk) -> ttk.Style:
    """Configura ttk.Style global com a paleta + estilos nomeados.

    Apos chamar, qualquer widget ttk criado herda as cores da marca.
    Estilos nomeados disponiveis:
        TFrame, Card.TFrame, Sidebar.TFrame
        TLabel, Muted.TLabel, Title.TLabel, Kpi.TLabel, H1.TLabel, H2.TLabel
        Primary.TButton, Ghost.TButton, Nav.TButton, NavActive.TButton
        TEntry, TCombobox
        Treeview, Treeview.Heading
        Pink.Horizontal.TProgressbar
        Vertical.TScrollbar
    """
    style = ttk.Style(root)
    style.theme_use("clam")

    # ---- defaults globais ----
    style.configure(
        ".",
        background=GREY, foreground=WHITE,
        fieldbackground=SURFACE, bordercolor=BORDER,
        lightcolor=SURFACE, darkcolor=SURFACE,
        focuscolor=PINK,
    )

    # ---- frames ----
    style.configure("TFrame", background=GREY)
    style.configure("Card.TFrame", background=SURFACE)
    style.configure("Sidebar.TFrame", background=SIDEBAR_BG)
    style.configure("Status.TFrame", background=STATUS_BG)

    # ---- labels ----
    style.configure("TLabel", background=GREY, foreground=WHITE, font=Fontes.body)
    style.configure("Muted.TLabel", background=GREY, foreground=MUTED, font=Fontes.label)
    style.configure("CardMuted.TLabel", background=SURFACE, foreground=MUTED, font=Fontes.label)
    style.configure("Card.TLabel", background=SURFACE, foreground=WHITE, font=Fontes.body)
    style.configure("CardTitle.TLabel", background=SURFACE, foreground=MUTED, font=Fontes.label)
    style.configure("CardValue.TLabel", background=SURFACE, foreground=WHITE, font=Fontes.display)
    style.configure("CardValuePink.TLabel", background=SURFACE, foreground=PINK, font=Fontes.display)
    style.configure("Title.TLabel", background=GREY, foreground=WHITE, font=Fontes.h2)
    style.configure("H1.TLabel", background=GREY, foreground=WHITE, font=Fontes.h1)
    style.configure("H2.TLabel", background=GREY, foreground=PINK, font=Fontes.h2)
    style.configure("Status.TLabel", background=STATUS_BG, foreground=WHITE, font=Fontes.label)
    style.configure("StatusMuted.TLabel", background=STATUS_BG, foreground=MUTED, font=Fontes.label)

    # ---- botoes ----
    style.configure(
        "Primary.TButton",
        background=PINK, foreground=WHITE, borderwidth=0,
        focusthickness=0, padding=(SPACE["lg"], SPACE["sm"]),
        font=Fontes.body_bold,
    )
    style.map(
        "Primary.TButton",
        background=[("active", PINK_HOVER), ("pressed", PINK_PRESSED)],
        foreground=[("active", WHITE), ("pressed", WHITE)],
    )

    style.configure(
        "Ghost.TButton",
        background=GREY, foreground=WHITE,
        borderwidth=1, bordercolor=BORDER,
        padding=(SPACE["md"], SPACE["sm"] - 1),
        font=Fontes.body,
    )
    style.map(
        "Ghost.TButton",
        background=[("active", SURFACE)],
        bordercolor=[("active", PINK), ("focus", PINK)],
    )

    # ---- inputs ----
    style.configure(
        "TEntry",
        fieldbackground=SURFACE, foreground=WHITE,
        bordercolor=BORDER, insertcolor=PINK, padding=SPACE["sm"],
    )
    style.map("TEntry", bordercolor=[("focus", PINK)])

    style.configure(
        "TCombobox",
        fieldbackground=SURFACE, background=SURFACE,
        foreground=WHITE, arrowcolor=WHITE,
        bordercolor=BORDER, padding=SPACE["xs"] + 2,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", SURFACE)],
        bordercolor=[("focus", PINK)],
        selectbackground=[("readonly", SURFACE)],
        selectforeground=[("readonly", WHITE)],
    )
    # Cor de fundo da lista dropdown (precisa de option_add no root)
    root.option_add("*TCombobox*Listbox.background", SURFACE)
    root.option_add("*TCombobox*Listbox.foreground", WHITE)
    root.option_add("*TCombobox*Listbox.selectBackground", PINK)
    root.option_add("*TCombobox*Listbox.selectForeground", WHITE)
    root.option_add("*TCombobox*Listbox.font", Fontes.body)

    # ---- treeview (tabelas) ----
    style.configure(
        "Treeview",
        background=SURFACE, fieldbackground=SURFACE,
        foreground=WHITE, bordercolor=BORDER,
        rowheight=28, font=Fontes.body, borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=GREY, foreground=MUTED,
        relief="flat", borderwidth=0,
        font=Fontes.label,
    )
    style.map(
        "Treeview",
        background=[("selected", PINK)],
        foreground=[("selected", WHITE)],
    )
    style.map("Treeview.Heading", background=[("active", GREY)])

    # ---- progress bar ----
    style.configure(
        "Pink.Horizontal.TProgressbar",
        background=PINK, troughcolor=SURFACE,
        bordercolor=SURFACE, lightcolor=PINK, darkcolor=PINK,
    )

    # ---- scrollbar ----
    style.configure(
        "Vertical.TScrollbar",
        background=SURFACE_HI, troughcolor=GREY,
        bordercolor=GREY, arrowcolor=MUTED,
        relief="flat",
    )

    return style
