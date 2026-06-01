"""Dashboard Aurora Siger — interface grafica seguindo o style guide oficial.

Estrutura espelhando o prototipo (pagina 6 do guia):

    +--------+-----------------------------------------------+
    | SIDE   | HEADER (titulo + ciclo + meta)                |
    |        +-----------------------------------------------+
    | NAV    |                                               |
    | 200px  | CONTEUDO (cards, tabelas, grafico)            |
    |        |                                               |
    |        +-----------------------------------------------+
    |        | STATUS BAR (mono, dados em tempo real)        |
    +--------+-----------------------------------------------+

Cada secao usa componentes do guia (KPI cards, Treeview com tags, grafico
nativo no Canvas, botoes Primary/Ghost). Layout responsivo via grid()
com weight nas linhas/colunas (checklist item 3).

Execucao:
    python3 -m src.interface_grafica
"""

from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

# Garante a raiz no PYTHONPATH para imports absolutos
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from src.config import COLUNAS_NUMERICAS, MODULOS_CRITICOS
from src.estruturas import buscar_bst, buscar_modulo_por_nome
from src.gui.charts import LineChart
from src.gui.theme import (
    BORDER,
    CRITICAL,
    MUTED,
    PINK,
    SIDEBAR_BG,
    SPACE,
    STATUS_BG,
    SUCCESS,
    SURFACE,
    SURFACE_HI,
    WARNING,
    WHITE,
    Fontes,
    aplicar_estilos,
    criar_fontes,
)
from src.gui.widgets import (
    divisor,
    get_inner,
    make_kpi_card,
    make_nav_item,
    make_section_card,
    make_status_dot,
)
from src.logica import classificar_modulos
from src.sistema import consolidar_alertas, executar_pipeline


# =============================================================================
# UTILITARIOS DE STATUS
# =============================================================================

CORES_STATUS = {"NORMAL": SUCCESS, "ALERTA": WARNING, "CRITICO": CRITICAL}
CORES_SEVERIDADE = {1: CRITICAL, 2: WARNING, 3: SUCCESS}  # severidade_num


def cor_por_status(status: str) -> str:
    return CORES_STATUS.get(status, MUTED)


# =============================================================================
# APLICACAO
# =============================================================================

class AuroraDashboard:
    """Janela principal do dashboard."""

    SECOES = [
        "Resumo",
        "Modulos",
        "Alertas",
        "Pilha",
        "Hierarquia",
        "Matriz",
        "Previsao",
        "Diagnostico",
        "Log",
        "Buscar",
    ]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._configurar_janela()
        criar_fontes()
        aplicar_estilos(self.root)
        self._carregar_dados()
        self._construir_layout()
        self._popular_sidebar()
        self.mostrar("Resumo")

    # ---- Setup ----

    def _configurar_janela(self) -> None:
        self.root.title("Aurora Siger — Sistema de Monitoramento")
        self.root.geometry("1280x800")
        self.root.minsize(1040, 640)
        self.root.configure(bg="#1e1e1e")

    def _carregar_dados(self) -> None:
        self.ctx = executar_pipeline()
        self.tabela_status = classificar_modulos(self.ctx["dicionario_modulos"])
        self.alertas_priorizados, self.fila_alertas = consolidar_alertas(self.ctx)
        self.matriz, self.matriz_colunas = self.ctx["matriz_e_colunas"]

    # ---- Layout root: grid 3x2 (sidebar | header/content/status) ----

    def _construir_layout(self) -> None:
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self._construir_sidebar()
        self._construir_header()
        self._construir_content_area()
        self._construir_status_bar()

    def _construir_sidebar(self) -> None:
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR_BG, width=200)
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="ns")
        self.sidebar.grid_propagate(False)

    def _construir_header(self) -> None:
        header = tk.Frame(self.root, bg="#1e1e1e", height=84)
        header.grid(row=0, column=1, sticky="ew")
        header.grid_propagate(False)

        wrap = tk.Frame(header, bg="#1e1e1e")
        wrap.pack(side="left", fill="y", padx=SPACE["xl"], pady=SPACE["lg"])

        ttk.Label(wrap, text="AURORA SIGER", style="H1.TLabel").pack(anchor="w")
        ttk.Label(
            wrap,
            text="Sistema Inteligente de Monitoramento  ·  Global Solution FIAP",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(SPACE["xs"], 0))

        # Indicador de ciclo atual a direita
        ult = self.ctx["telemetria"][-1]
        right = tk.Frame(header, bg="#1e1e1e")
        right.pack(side="right", fill="y", padx=SPACE["xl"], pady=SPACE["lg"])

        ttk.Label(right, text="CICLO ATUAL", style="Muted.TLabel").pack(anchor="e")
        ttk.Label(
            right, text=str(ult["ciclo"]),
            background="#1e1e1e", foreground=PINK, font=Fontes.display,
        ).pack(anchor="e")

    def _construir_content_area(self) -> None:
        self.content = tk.Frame(self.root, bg="#1e1e1e")
        self.content.grid(row=1, column=1, sticky="nsew",
                          padx=SPACE["xl"], pady=(0, SPACE["lg"]))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        # Cabecalho da secao
        self.titulo_secao = ttk.Label(self.content, text="", style="H2.TLabel")
        self.titulo_secao.grid(row=0, column=0, sticky="w", pady=(0, SPACE["md"]))

        # Container que troca o conteudo a cada navegacao
        self.painel = tk.Frame(self.content, bg="#1e1e1e")
        self.painel.grid(row=1, column=0, sticky="nsew")
        self.painel.grid_columnconfigure(0, weight=1)
        self.painel.grid_rowconfigure(0, weight=1)

    def _construir_status_bar(self) -> None:
        bar = tk.Frame(self.root, bg=STATUS_BG, height=30)
        bar.grid(row=2, column=1, sticky="ew")
        bar.grid_propagate(False)

        ult = self.ctx["telemetria"][-1]
        prev = self.ctx["previsao"]
        cor_prev = CORES_STATUS.get(prev["nivel"], MUTED)

        partes = [
            ("RESERVA",   f"{ult['reserva_energia_pct']:.1f}%", WHITE),
            ("RADIACAO",  f"{ult['radiacao_nivel']:.0f}",       WHITE),
            ("ALERTAS",   f"{len(self.alertas_priorizados)}",   WHITE),
            ("INCONSIST.", f"{len(self.ctx['inconsistencias'])}", WHITE),
            ("PROJ. C.13", f"{prev['reserva_prevista_pct']:.1f}%", cor_prev),
        ]

        for rotulo, valor, cor in partes:
            grupo = tk.Frame(bar, bg=STATUS_BG)
            grupo.pack(side="left", padx=SPACE["md"] + 2)
            tk.Label(grupo, text=rotulo,
                     bg=STATUS_BG, fg=MUTED, font=Fontes.label).pack(side="left")
            tk.Label(grupo, text=valor,
                     bg=STATUS_BG, fg=cor, font=Fontes.body_bold).pack(side="left", padx=(SPACE["xs"] + 2, 0))

        tk.Label(
            bar, text="RM 571330  ·  Gabriel de Leao Rocha",
            bg=STATUS_BG, fg=MUTED, font=Fontes.label,
        ).pack(side="right", padx=SPACE["md"] + 2)

    # ---- Sidebar nav ----

    def _popular_sidebar(self) -> None:
        # Espaco superior
        tk.Frame(self.sidebar, bg=SIDEBAR_BG, height=SPACE["lg"]).pack()

        # Label de secao
        tk.Label(
            self.sidebar, text="NAVEGACAO",
            bg=SIDEBAR_BG, fg=MUTED, font=Fontes.label,
            padx=SPACE["md"] + 3,
        ).pack(anchor="w", pady=(0, SPACE["sm"]))

        self._nav_widgets: dict[str, tk.Frame] = {}
        self._secao_atual: str = "Resumo"

        for nome in self.SECOES:
            self._renderizar_nav_item(nome)

    def _renderizar_nav_item(self, nome: str) -> None:
        ativo = nome == self._secao_atual
        item = make_nav_item(
            self.sidebar, nome, lambda n=nome: self.mostrar(n), active=ativo,
        )
        self._nav_widgets[nome] = item

    def _recriar_sidebar(self) -> None:
        """Recria os items da sidebar para refletir o item ativo."""
        for widget in self._nav_widgets.values():
            widget.destroy()
        self._nav_widgets.clear()
        for nome in self.SECOES:
            self._renderizar_nav_item(nome)

    # ---- Navegacao ----

    def mostrar(self, nome: str) -> None:
        self._secao_atual = nome
        if self._nav_widgets:
            self._recriar_sidebar()
        self.titulo_secao.configure(text=nome.upper())

        # Limpa o painel
        for child in self.painel.winfo_children():
            child.destroy()

        # Despacha
        renderizadores: dict[str, Callable[[], None]] = {
            "Resumo":      self._render_resumo,
            "Modulos":     self._render_modulos,
            "Alertas":     self._render_alertas,
            "Pilha":       self._render_pilha,
            "Hierarquia":  self._render_hierarquia,
            "Matriz":      self._render_matriz,
            "Previsao":    self._render_previsao,
            "Diagnostico": self._render_diagnostico,
            "Log":         self._render_log,
            "Buscar":      self._render_buscar,
        }
        renderizadores[nome]()

    # =========================================================================
    # SECAO: RESUMO — KPI cards + status dos modulos + gerac/consumo
    # =========================================================================

    def _render_resumo(self) -> None:
        ult = self.ctx["telemetria"][-1]
        prev = self.ctx["previsao"]
        cor_prev = CORES_STATUS.get(prev["nivel"], MUTED)

        # Grid de KPI cards (4 colunas)
        kpi_grid = tk.Frame(self.painel, bg="#1e1e1e")
        kpi_grid.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            kpi_grid.grid_columnconfigure(i, weight=1, uniform="kpi")

        kpis = [
            ("Reserva atual",  f"{ult['reserva_energia_pct']:.1f}", "%",
             PINK,
             CRITICAL if ult["reserva_energia_pct"] < 20 else (WARNING if ult["reserva_energia_pct"] < 50 else WHITE)),
            ("Radiacao",       f"{ult['radiacao_nivel']:.0f}", "",
             WARNING if ult["radiacao_nivel"] > 60 else PINK,
             CRITICAL if ult["radiacao_nivel"] > 80 else (WARNING if ult["radiacao_nivel"] > 60 else WHITE)),
            ("Alertas ativos", f"{len(self.alertas_priorizados)}", "",
             PINK,
             CRITICAL if any(a["status"] == "CRITICO" for a in self.alertas_priorizados) else (WARNING if self.alertas_priorizados else WHITE)),
            ("Proj. c.13",     f"{prev['reserva_prevista_pct']:.1f}", "%",
             cor_prev, cor_prev),
        ]
        for i, (titulo, valor, unidade, acento, cor_val) in enumerate(kpis):
            card = make_kpi_card(kpi_grid, titulo, valor, unidade,
                                 accent=acento, value_color=cor_val)
            card.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else SPACE["md"], 0))

        # Row 2: modulos + energia (lado a lado)
        row2 = tk.Frame(self.painel, bg="#1e1e1e")
        row2.grid(row=1, column=0, sticky="nsew", pady=(SPACE["lg"], 0))
        row2.grid_columnconfigure(0, weight=2, uniform="r2")
        row2.grid_columnconfigure(1, weight=1, uniform="r2")
        row2.grid_rowconfigure(0, weight=1)

        # --- Card: status modulos ---
        card_mods = make_section_card(row2, "Status dos modulos")
        card_mods.grid(row=0, column=0, sticky="nsew", padx=(0, SPACE["md"]))
        inner_mods = get_inner(card_mods)

        grid_mods = tk.Frame(inner_mods, bg=SURFACE)
        grid_mods.pack(fill="both", expand=True)
        for col in range(3):
            grid_mods.grid_columnconfigure(col, weight=1, uniform="mod")

        for i, nome in enumerate(MODULOS_CRITICOS):
            r, c = divmod(i, 3)
            self._render_modulo_resumo(grid_mods, nome, r, c)

        # --- Card: energia ---
        card_en = make_section_card(row2, "Energia (medias)")
        card_en.grid(row=0, column=1, sticky="nsew")
        inner_en = get_inner(card_en)

        from src.previsao import media
        telemetria = self.ctx["telemetria"]
        solar = media([r["geracao_solar_kwh"] for r in telemetria])
        eolica = media([r["geracao_eolica_kwh"] for r in telemetria])
        consumo = media([r["consumo_total_kwh"] for r in telemetria])

        for rotulo, valor, unidade, cor in [
            ("Solar",   f"{solar:.2f}",   "kWh", PINK),
            ("Eolica",  f"{eolica:.2f}",  "kWh", SUCCESS),
            ("Consumo", f"{consumo:.2f}", "kWh", WARNING),
        ]:
            linha = tk.Frame(inner_en, bg=SURFACE)
            linha.pack(fill="x", pady=SPACE["xs"] + 2)
            make_status_dot(linha, cor, bg=SURFACE).pack(side="left", padx=(0, SPACE["sm"]))
            tk.Label(linha, text=rotulo, bg=SURFACE, fg=MUTED,
                     font=Fontes.label).pack(side="left")
            tk.Label(linha, text=f"{valor} {unidade}", bg=SURFACE, fg=WHITE,
                     font=Fontes.body_bold).pack(side="right")

        # Configurar peso das linhas no painel
        self.painel.grid_rowconfigure(1, weight=1)

    def _render_modulo_resumo(self, parent: tk.Frame, nome: str, row: int, col: int) -> None:
        info = self.tabela_status[nome]
        cor = cor_por_status(info["status"])

        wrap = tk.Frame(parent, bg=SURFACE)
        wrap.grid(row=row, column=col, sticky="ew", padx=SPACE["sm"], pady=SPACE["sm"])

        topo = tk.Frame(wrap, bg=SURFACE)
        topo.pack(fill="x")
        make_status_dot(topo, cor, bg=SURFACE).pack(side="left", padx=(0, SPACE["sm"]))
        tk.Label(topo, text=nome, bg=SURFACE, fg=WHITE,
                 font=Fontes.body_bold).pack(side="left")

        tk.Label(
            wrap, text=f"{info['status']}  ·  ativo em {info['pct_ativo']:.0f}% dos ciclos",
            bg=SURFACE, fg=MUTED, font=Fontes.label,
        ).pack(anchor="w", pady=(SPACE["xs"], 0))

    # =========================================================================
    # SECAO: MODULOS — tabela (Treeview)
    # =========================================================================

    def _render_modulos(self) -> None:
        colunas = ("modulo", "status", "pct", "atual")
        tv = self._criar_treeview(self.painel, colunas, headings={
            "modulo": ("Modulo", 220, "w"),
            "status": ("Status", 120, "center"),
            "pct":    ("% Ativo", 100, "center"),
            "atual":  ("Atual",  90,  "center"),
        })
        for nome, info in self.tabela_status.items():
            tag = info["status"].lower()
            tv.insert(
                "", "end",
                values=(nome, info["status"], f"{info['pct_ativo']:.1f}%",
                        "ATIVO" if info["status_atual"] == 1 else "INATIVO"),
                tags=(tag,),
            )
        tv.tag_configure("normal", foreground=SUCCESS)
        tv.tag_configure("alerta", foreground=WARNING)
        tv.tag_configure("critico", foreground=CRITICAL)

    # =========================================================================
    # SECAO: ALERTAS — tabela
    # =========================================================================

    def _render_alertas(self) -> None:
        colunas = ("ciclo", "sev", "regra", "descricao")
        tv = self._criar_treeview(self.painel, colunas, headings={
            "ciclo":     ("Ciclo",  60,  "center"),
            "sev":       ("Sev.",   80,  "center"),
            "regra":     ("Regra",  240, "w"),
            "descricao": ("Descricao + Acao", 460, "w"),
        })
        if not self.alertas_priorizados:
            tv.insert("", "end", values=("-", "OK", "-", "Nenhum alerta ativo."))
        else:
            for a in self.alertas_priorizados:
                tag = a["status"].lower()
                tv.insert(
                    "", "end",
                    values=(a["ciclo"], a["status"], a["regra"],
                            f"{a['descricao']}  →  {a['acao']}"),
                    tags=(tag,),
                )
        tv.tag_configure("normal", foreground=SUCCESS)
        tv.tag_configure("alerta", foreground=WARNING)
        tv.tag_configure("critico", foreground=CRITICAL)

    # =========================================================================
    # SECAO: PILHA DE EVENTOS CRITICOS (LIFO)
    # =========================================================================

    def _render_pilha(self) -> None:
        pilha = self.ctx["pilha_eventos"]
        if pilha.is_empty():
            tk.Label(self.painel, text="Pilha vazia (nenhum evento critico).",
                     bg="#1e1e1e", fg=MUTED, font=Fontes.body).pack(pady=SPACE["xl"])
            return

        wrap = tk.Frame(self.painel, bg="#1e1e1e")
        wrap.grid(row=0, column=0, sticky="nsew")
        wrap.grid_columnconfigure(0, weight=1)

        for i, evento in enumerate(pilha.listar()):
            card = tk.Frame(wrap, bg=SURFACE)
            card.grid(row=i, column=0, sticky="ew", pady=(0, SPACE["sm"]))

            # acento esquerdo
            tk.Frame(card, bg=CRITICAL, width=3).pack(side="left", fill="y")

            inner = tk.Frame(card, bg=SURFACE)
            inner.pack(side="left", fill="both", expand=True,
                       padx=SPACE["lg"], pady=SPACE["md"])

            badge = "TOPO" if i == 0 else f"#{i + 1}"
            top = tk.Frame(inner, bg=SURFACE)
            top.pack(fill="x")
            tk.Label(top, text=badge, bg=SURFACE, fg=PINK,
                     font=Fontes.label).pack(side="left")
            tk.Label(top, text=f"  ciclo {evento['ciclo']}  ·  {evento['modulo']}",
                     bg=SURFACE, fg=MUTED, font=Fontes.label).pack(side="left")

            tk.Label(inner, text=evento["descricao"], bg=SURFACE, fg=WHITE,
                     font=Fontes.body, wraplength=900,
                     justify="left").pack(anchor="w", pady=(SPACE["xs"], 0))

    # =========================================================================
    # SECAO: HIERARQUIA — Treeview com show='tree'
    # =========================================================================

    def _render_hierarquia(self) -> None:
        tv = ttk.Treeview(self.painel, show="tree", selectmode="browse")
        sb = ttk.Scrollbar(self.painel, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")
        tv.grid(row=0, column=0, sticky="nsew")
        self.painel.grid_columnconfigure(0, weight=1)
        self.painel.grid_rowconfigure(0, weight=1)

        # Insere hierarquia recursivamente
        hier = self.ctx["hierarquia"]
        raiz = tv.insert("", "end", text=hier["missao"], open=True)
        self._inserir_hierarquia(tv, raiz, hier["sistemas"])

    def _inserir_hierarquia(self, tv: ttk.Treeview, pai: str, dados: dict) -> None:
        for chave, valor in dados.items():
            if isinstance(valor, dict):
                no = tv.insert(pai, "end", text=chave, open=True)
                self._inserir_hierarquia(tv, no, valor)
            elif isinstance(valor, list):
                tv.insert(pai, "end", text=f"{chave}  ({len(valor)} valores)")
            else:
                tv.insert(pai, "end", text=f"{chave}: {valor}")

    # =========================================================================
    # SECAO: MATRIZ — Treeview com todas as colunas numericas
    # =========================================================================

    def _render_matriz(self) -> None:
        # Cria colunas com abreviacoes para caber bem
        abrev = {
            "geracao_solar_kwh": "solar_kWh",
            "geracao_eolica_kwh": "eolica_kWh",
            "consumo_total_kwh": "consumo_kWh",
            "reserva_energia_pct": "reserva_%",
            "temperatura_externa_c": "temp_C",
            "radiacao_nivel": "radiacao",
            "qualidade_comunicacao_pct": "qual_com_%",
            "velocidade_vento_ms": "vento_m/s",
        }
        colunas = ("ciclo",) + tuple(abrev[c] for c in self.matriz_colunas)
        headings: dict[str, tuple[str, int, str]] = {
            "ciclo": ("Ciclo", 60, "center"),
        }
        for c in self.matriz_colunas:
            headings[abrev[c]] = (abrev[c], 100, "center")

        tv = self._criar_treeview(self.painel, colunas, headings=headings)
        for i, linha in enumerate(self.matriz, 1):
            valores = (i,) + tuple(f"{v:.2f}" for v in linha)
            tv.insert("", "end", values=valores, tags=("zebra" if i % 2 == 0 else "",))
        tv.tag_configure("zebra", background=SURFACE_HI)

    # =========================================================================
    # SECAO: PREVISAO — KPIs + grafico de linha nativo
    # =========================================================================

    def _render_previsao(self) -> None:
        prev = self.ctx["previsao"]
        cor_nivel = CORES_STATUS.get(prev["nivel"], MUTED)

        # Grid: 3 KPI cards no topo + chart + recomendacao
        self.painel.grid_columnconfigure(0, weight=1)
        self.painel.grid_rowconfigure(2, weight=1)

        kpis = tk.Frame(self.painel, bg="#1e1e1e")
        kpis.grid(row=0, column=0, sticky="ew")
        for i in range(3):
            kpis.grid_columnconfigure(i, weight=1, uniform="kpi")

        cards = [
            ("Reserva prevista", f"{prev['reserva_prevista_pct']:.2f}", "%", cor_nivel, cor_nivel),
            ("R^2 do ajuste",    f"{prev['r_quadrado']:.4f}",           "",  PINK, WHITE),
            ("Nivel",            prev["nivel"],                          "",  cor_nivel, cor_nivel),
        ]
        for i, (titulo, valor, unidade, acento, cor_val) in enumerate(cards):
            card = make_kpi_card(kpis, titulo, valor, unidade,
                                 accent=acento, value_color=cor_val)
            card.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else SPACE["md"], 0))

        # Chart
        card_chart = make_section_card(
            self.painel,
            f"Reserva energetica por ciclo  ·  y = {prev['beta_0']:.2f} + {prev['beta_1']:.2f} * x",
        )
        card_chart.grid(row=1, column=0, sticky="ew", pady=(SPACE["lg"], 0))
        inner = get_inner(card_chart)

        x_vals = [r["ciclo"] for r in self.ctx["telemetria"]]
        y_vals = [r["reserva_energia_pct"] for r in self.ctx["telemetria"]]

        chart = LineChart(inner, width=1000, height=300)
        chart.plot(
            x_vals, y_vals,
            previsao=(prev["proximo_ciclo"], prev["reserva_prevista_pct"]),
            y_label="reserva (%)", x_label="ciclo  (* = projecao)",
            limites_y=(0, 100),
        )
        chart.pack(fill="x", expand=False)

        # Recomendacao
        rec_card = make_section_card(self.painel, "Recomendacao automatica")
        rec_card.grid(row=2, column=0, sticky="ew", pady=(SPACE["lg"], 0))
        rec_inner = get_inner(rec_card)
        tk.Label(
            rec_inner, text=prev["recomendacao"],
            bg=SURFACE, fg=cor_nivel, font=Fontes.body_bold,
            wraplength=1000, justify="left",
        ).pack(anchor="w")

    # =========================================================================
    # SECAO: DIAGNOSTICO — inconsistencias em cards de warning
    # =========================================================================

    def _render_diagnostico(self) -> None:
        inconsistencias = self.ctx["inconsistencias"]
        if not inconsistencias:
            tk.Label(self.painel, text="Nenhuma inconsistencia detectada.",
                     bg="#1e1e1e", fg=SUCCESS, font=Fontes.body_bold).pack(pady=SPACE["xl"])
            return

        wrap = tk.Frame(self.painel, bg="#1e1e1e")
        wrap.grid(row=0, column=0, sticky="ew")
        wrap.grid_columnconfigure(0, weight=1)

        for i, inc in enumerate(inconsistencias):
            card = tk.Frame(wrap, bg=SURFACE)
            card.grid(row=i, column=0, sticky="ew", pady=(0, SPACE["sm"]))
            tk.Frame(card, bg=WARNING, width=3).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=SURFACE)
            inner.pack(side="left", fill="both", expand=True,
                       padx=SPACE["lg"], pady=SPACE["md"])

            topo = tk.Frame(inner, bg=SURFACE)
            topo.pack(fill="x")
            tk.Label(topo, text=inc["tipo"], bg=SURFACE, fg=WARNING,
                     font=Fontes.body_bold).pack(side="left")
            tk.Label(topo, text=f"  ·  ciclo {inc['ciclo']}",
                     bg=SURFACE, fg=MUTED, font=Fontes.label).pack(side="left")

            tk.Label(inner, text=inc["descricao"], bg=SURFACE, fg=WHITE,
                     font=Fontes.body, wraplength=1000,
                     justify="left").pack(anchor="w", pady=(SPACE["xs"], 0))

    # =========================================================================
    # SECAO: LOG — tabela
    # =========================================================================

    def _render_log(self) -> None:
        colunas = ("id", "ciclo", "tipo", "modulo", "severidade", "descricao")
        tv = self._criar_treeview(self.painel, colunas, headings={
            "id":         ("ID",          50,  "center"),
            "ciclo":      ("Ciclo",       60,  "center"),
            "tipo":       ("Tipo",        180, "w"),
            "modulo":     ("Modulo",      130, "w"),
            "severidade": ("Severidade",  100, "center"),
            "descricao":  ("Descricao",   500, "w"),
        })
        for ev in self.ctx["log_eventos"]:
            tag = ev["severidade"].lower()
            tv.insert(
                "", "end",
                values=(ev["id"], ev["ciclo"], ev["tipo"], ev["modulo"],
                        ev["severidade"], ev["descricao"]),
                tags=(tag,),
            )
        tv.tag_configure("normal", foreground=SUCCESS)
        tv.tag_configure("alerta", foreground=WARNING)
        tv.tag_configure("critico", foreground=CRITICAL)

    # =========================================================================
    # SECAO: BUSCAR — formularios em cards
    # =========================================================================

    def _render_buscar(self) -> None:
        wrap = tk.Frame(self.painel, bg="#1e1e1e")
        wrap.grid(row=0, column=0, sticky="nsew")
        wrap.grid_columnconfigure(0, weight=1)

        # --- Card 1: BST ---
        card_bst = make_section_card(wrap, "Buscar ciclo na BST  (O(log n))")
        card_bst.grid(row=0, column=0, sticky="ew", pady=(0, SPACE["md"]))
        inner_bst = get_inner(card_bst)

        ttk.Label(inner_bst, text="Numero do ciclo (1 a 12):",
                  style="CardMuted.TLabel").pack(anchor="w", pady=(0, SPACE["sm"]))

        linha_bst = tk.Frame(inner_bst, bg=SURFACE)
        linha_bst.pack(fill="x")
        entry_ciclo = ttk.Entry(linha_bst, width=10, font=Fontes.mono)
        entry_ciclo.pack(side="left")
        saida_bst = self._area_resultado(inner_bst)
        ttk.Button(
            linha_bst, text="Buscar", style="Primary.TButton",
            command=lambda: self._fazer_busca_bst(entry_ciclo.get(), saida_bst),
        ).pack(side="left", padx=(SPACE["md"], 0))

        # --- Card 2: Modulo ---
        card_mod = make_section_card(wrap, "Buscar modulo  (busca linear O(n))")
        card_mod.grid(row=1, column=0, sticky="ew")
        inner_mod = get_inner(card_mod)

        ttk.Label(inner_mod, text="Selecione o modulo:",
                  style="CardMuted.TLabel").pack(anchor="w", pady=(0, SPACE["sm"]))

        linha_mod = tk.Frame(inner_mod, bg=SURFACE)
        linha_mod.pack(fill="x")
        var = tk.StringVar(value="energia")
        ttk.Combobox(
            linha_mod, textvariable=var, state="readonly",
            values=MODULOS_CRITICOS, width=20, font=Fontes.body,
        ).pack(side="left")
        saida_mod = self._area_resultado(inner_mod)
        ttk.Button(
            linha_mod, text="Buscar", style="Primary.TButton",
            command=lambda: self._fazer_busca_modulo(var.get(), saida_mod),
        ).pack(side="left", padx=(SPACE["md"], 0))

    def _area_resultado(self, parent: tk.Misc) -> tk.Text:
        text = tk.Text(
            parent, height=7,
            bg="#1e1e1e", fg=WHITE, insertbackground=PINK,
            font=Fontes.mono, relief="flat", borderwidth=0,
            padx=SPACE["md"], pady=SPACE["sm"],
            wrap="word", state="disabled",
        )
        text.pack(fill="x", pady=(SPACE["md"], 0))
        return text

    def _fazer_busca_bst(self, valor: str, area: tk.Text) -> None:
        area.configure(state="normal")
        area.delete("1.0", "end")
        try:
            ciclo = int(valor)
        except ValueError:
            area.insert("1.0", "Entrada invalida — informe um numero inteiro.")
            area.configure(state="disabled")
            return
        resultado = buscar_bst(self.ctx["bst"], ciclo)
        if resultado is None:
            area.insert("1.0", f"Ciclo {ciclo} nao encontrado.")
        else:
            linhas = [f"Dados do ciclo {ciclo}:"]
            for chave, valor_ in resultado.items():
                linhas.append(f"  {chave:<28s} = {valor_}")
            area.insert("1.0", "\n".join(linhas))
        area.configure(state="disabled")

    def _fazer_busca_modulo(self, nome: str, area: tk.Text) -> None:
        area.configure(state="normal")
        area.delete("1.0", "end")
        info = buscar_modulo_por_nome(self.ctx["dicionario_modulos"], nome)
        if info is None:
            area.insert("1.0", f"Modulo '{nome}' nao encontrado.")
        else:
            estado = "ATIVO" if info["status_atual"] == 1 else "INATIVO"
            linhas = [
                info["nome"],
                f"  status atual:    {estado}",
                f"  ciclos ativo:    {info['ciclos_ativo']}",
                f"  ciclos inativo:  {info['ciclos_inativo']}",
                f"  historico:       {info['historico']}",
            ]
            area.insert("1.0", "\n".join(linhas))
        area.configure(state="disabled")

    # =========================================================================
    # HELPER COMUM: Treeview com scrollbar
    # =========================================================================

    def _criar_treeview(
        self, parent: tk.Misc,
        colunas: tuple[str, ...],
        headings: dict[str, tuple[str, int, str]],
    ) -> ttk.Treeview:
        """Cria Treeview + scrollbar dentro de um card.

        headings = {coluna: (titulo, largura, anchor)}
        """
        card = make_section_card(parent)
        card.grid(row=0, column=0, sticky="nsew")
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        inner = get_inner(card)

        tv = ttk.Treeview(inner, columns=colunas, show="headings", selectmode="browse")
        for c in colunas:
            titulo, largura, ancora = headings[c]
            tv.heading(c, text=titulo, anchor=ancora)
            tv.column(c, width=largura, anchor=ancora)

        sb = ttk.Scrollbar(inner, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tv.pack(side="left", fill="both", expand=True)

        return tv


# =============================================================================
# ENTRYPOINT
# =============================================================================

def main() -> int:
    root = tk.Tk()
    AuroraDashboard(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
