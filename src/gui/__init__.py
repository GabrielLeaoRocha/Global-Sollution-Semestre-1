"""Pacote da interface grafica — segue o Aurora Siger Tkinter Style Guide.

Modulos:
    theme    paleta, fontes, ttk.Style global (checklist item 1 do guia)
    widgets  componentes reaproveitaveis (KPI card, nav item, status dot)
    charts   grafico de linha nativo (Canvas) sem dependencias externas
"""

from src.gui import charts, theme, widgets

__all__ = ["theme", "widgets", "charts"]
