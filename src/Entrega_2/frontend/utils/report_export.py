# utils/report_export.py
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Tuple, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --------- Plotly / Matplotlib (opcionais) ---------
try:
    import plotly.graph_objects as go
    import plotly.io as pio
except Exception:  # pragma: no cover
    go = None
    pio = None

try:
    import matplotlib.figure as mpl_fig
except Exception:  # pragma: no cover
    mpl_fig = None


# =========================
# Paleta & utilidades de cor
# =========================
_DEFAULT_COLORWAY = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
]

def _is_single_color(value: Any) -> bool:
    if value is None:
        return True
    # string (uma cor), ou lista/tupla de tamanho 1
    if isinstance(value, str):
        return True
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return True
    return False

def _bar_len(tr: Any) -> int:
    # tenta deduzir quantos pontos a barra tem
    if getattr(tr, "x", None) is not None:
        return len(tr.x)
    if getattr(tr, "y", None) is not None:
        return len(tr.y)
    return 0

def _apply_plotly_defaults(fig: "go.Figure", colorway: List[str] | None = None) -> "go.Figure":
    """
    Garante fundo branco e define colorway se não houver.
    Além disso, para traços de barra "monocromáticos", aplica cores por barra.
    """
    if fig is None or go is None:
        return fig

    # Clone leve
    f = go.Figure(fig.to_dict())

    # Fundo branco (evita export "branco")
    try:
        bg = (f.layout.paper_bgcolor or "").lower()
    except Exception:
        bg = ""
    if not bg or bg in ("transparent", "rgba(0,0,0,0)", "rgba(0, 0, 0, 0)"):
        f.update_layout(paper_bgcolor="#FFFFFF")

    # Colorway default se não houver
    cw = colorway or _DEFAULT_COLORWAY
    try:
        has_colorway = hasattr(f.layout, "colorway") and f.layout.colorway
    except Exception:
        has_colorway = False
    if not has_colorway:
        f.update_layout(colorway=cw)

    # --- Anti-monocromático para Barras ---
    # Regra: se um traço Bar tiver marker.color ausente ou "simples",
    # pintamos cada barra com a sequência da paleta (cíclica).
    try:
        for tr in f.data:
            if isinstance(tr, go.Bar):
                # Se já veio uma lista de cores do usuário, respeitamos
                mark = getattr(tr, "marker", None)
                cur = getattr(mark, "color", None) if mark is not None else None
                if _is_single_color(cur):
                    n = _bar_len(tr)
                    if n > 0:
                        cores = [cw[i % len(cw)] for i in range(n)]
                        # aplica por ponto
                        f.update_traces(
                            selector=lambda t: t is tr,
                            marker_color=cores
                        )
    except Exception:
        # Em caso de qualquer problema, não travar exportação
        pass

    return f


# =========================
# Tipos e checagens
# =========================
def _is_supported_figure(obj: Any) -> bool:
    if go is not None and isinstance(obj, go.Figure):
        return True
    if mpl_fig is not None and isinstance(obj, mpl_fig.Figure):
        return True
    return False


# =========================
# Exportadores de imagem
# =========================
def _plotly_to_png(fig: "go.Figure") -> bytes:
    if pio is None:
        raise RuntimeError("plotly.io não disponível.")
    fig_ready = _apply_plotly_defaults(fig)
    return pio.to_image(fig_ready, format="png", engine="kaleido", width=1200, scale=2)

def _matplotlib_to_png(fig: "mpl_fig.Figure") -> bytes:
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    buf.seek(0)
    return buf.read()

def fig_to_png_bytes(fig) -> bytes:
    if go is not None and isinstance(fig, go.Figure):
        try:
            return _plotly_to_png(fig)
        except Exception as e:
            raise TypeError(f"Falha ao exportar figura Plotly: {e}")
    if mpl_fig is not None and isinstance(fig, mpl_fig.Figure):
        try:
            return _matplotlib_to_png(fig)
        except Exception as e:
            raise TypeError(f"Falha ao exportar figura Matplotlib: {e}")
    raise TypeError("Tipo de figura não suportado. Use Plotly (go.Figure) ou Matplotlib.")


# =========================
# Helpers de layout
# =========================
def _params_table_data(params: Dict[str, Any]) -> List[List[str]]:
    linhas = [["Parâmetro", "Valor"]]
    for k, v in params.items():
        if isinstance(v, (list, tuple, set)):
            linhas.append([str(k), ", ".join(map(str, v))])
        else:
            linhas.append([str(k), str(v)])
    return linhas

def _placeholder_box(texto: str, largura_cm: float) -> Table:
    tbl = Table([[texto]], colWidths=[largura_cm * cm])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF2F2")),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#FF9999")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    return tbl


# =========================
# Função principal
# =========================
def construir_pdf_relatorio(
    titulo: str,
    params: Dict[str, Any],
    secoes: List[Tuple[str, Any]],  # [(titulo_secao, figura_plotly_ou_matplotlib), ...]
    resumo_kpis: Dict[str, Any] | None = None,

    # -------- Layout da grade --------
    figs_per_page: int = 6,    # quantos gráficos por página
    cols: int = 1,             # **uma coluna** por preferência
    gutter_cm: float = 0.4,    # espaçamento horizontal (irrelevante em 1 col)
    caption_font_size: int = 9,
    cell_img_max_h_cm: float = 8.5,  # altura máx. da imagem por célula
) -> bytes:
    """
    PDF com:
      - Capa + parâmetros (+ KPIs se houver)
      - Grade (N por página, 1 coluna por padrão)
      - Apêndice OK/FALHA/IGNORADA

    Barras Plotly monocromáticas recebem cores por barra automaticamente.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    style_caption = ParagraphStyle(
        "Caption",
        parent=styles["Normal"],
        fontSize=caption_font_size,
        textColor=colors.HexColor("#444444"),
        spaceAfter=0.08 * cm,
    )

    story: List[Any] = []

    # Capa
    story.append(Paragraph(titulo, styles["Title"]))
    story.append(Paragraph(datetime.now().strftime("%d/%m/%Y %H:%M"), styles["Normal"]))
    story.append(Spacer(1, 0.6 * cm))

    # Parâmetros
    story.append(Paragraph("Parâmetros aplicados", styles["Heading2"]))
    dados_params = _params_table_data(params)
    tbl = Table(dados_params, colWidths=[6.2 * cm, 9.3 * cm])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 0.4 * cm))

    # Resumo de KPIs (opcional)
    if resumo_kpis:
        story.append(Paragraph("Resumo de KPIs", styles["Heading2"]))
        linhas = [["KPI", "Valor"]]
        for k, v in resumo_kpis.items():
            linhas.append([str(k), str(v)])
        kpi_tbl = Table(linhas, colWidths=[8.0 * cm, 7.5 * cm])
        kpi_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ]
            )
        )
        story.append(kpi_tbl)
        story.append(Spacer(1, 0.6 * cm))

    # Preparar exportação e grade
    export_log: List[Tuple[str, str]] = []
    if not secoes:
        export_log.append(("Nenhuma seção fornecida", "IGNORADA"))

    # Largura útil (cm)
    usable_w_cm = (A4[0] / cm) - (doc.leftMargin / cm + doc.rightMargin / cm)
    cols = max(1, int(cols))
    figs_per_page = max(1, int(figs_per_page))
    gutter_total_cm = gutter_cm * (cols - 1)
    cell_w_cm = (usable_w_cm - gutter_total_cm) / cols

    # Converte cada seção em um "card" (tabela interna 2 linhas: caption + imagem)
    cards: List[Table] = []
    for (titulo_secao, figura) in (secoes or []):
        caption = Paragraph(titulo_secao, style_caption)

        if not _is_supported_figure(figura):
            inner = Table([[caption], [_placeholder_box("Figura não suportada (Plotly/Matplotlib)", cell_w_cm)]],
                          colWidths=[cell_w_cm * cm])
            inner.setStyle(TableStyle([
                ("LEFTPADDING",  (0,0), (-1,-1), 0),
                ("RIGHTPADDING", (0,0), (-1,-1), 0),
                ("TOPPADDING",   (0,0), (-1,-1), 0),
                ("BOTTOMPADDING",(0,0), (-1,-1), 0),
                ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ]))
            cards.append(inner)
            export_log.append((titulo_secao, "IGNORADA"))
            continue

        try:
            png_bytes = fig_to_png_bytes(figura)
            if not png_bytes:
                raise ValueError("Exportação retornou bytes vazios.")
            img = Image(BytesIO(png_bytes))
            img._restrictSize(cell_w_cm * cm, cell_img_max_h_cm * cm)

            inner = Table([[caption], [img]], colWidths=[cell_w_cm * cm])
            inner.setStyle(TableStyle([
                ("LEFTPADDING",  (0,0), (-1,-1), 0),
                ("RIGHTPADDING", (0,0), (-1,-1), 0),
                ("TOPPADDING",   (0,0), (-1,-1), 0.06 * cm),
                ("BOTTOMPADDING",(0,0), (-1,-1), 0.06 * cm),
                ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ]))
            cards.append(inner)
            export_log.append((titulo_secao, "OK"))
        except Exception as e:
            inner = Table([[caption], [_placeholder_box(f"Imagem não exportada: {e}", cell_w_cm)]],
                          colWidths=[cell_w_cm * cm])
            inner.setStyle(TableStyle([
                ("LEFTPADDING",  (0,0), (-1,-1), 0),
                ("RIGHTPADDING", (0,0), (-1,-1), 0),
                ("TOPPADDING",   (0,0), (-1,-1), 0.06 * cm),
                ("BOTTOMPADDING",(0,0), (-1,-1), 0.06 * cm),
                ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ]))
            cards.append(inner)
            export_log.append((f"{titulo_secao} – {e}", "FALHA"))

    # Monta grade por página (tabela externa)
    if cards:
        def _chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i+n]

        for page_idx, chunk in enumerate(_chunks(cards, figs_per_page), start=1):
            rows = []
            row = []
            for i, card in enumerate(chunk, start=1):
                row.append(card)
                if i % cols == 0:
                    rows.append(row)
                    row = []
            if row:
                for _ in range(cols - len(row)):
                    row.append(Spacer(1, 0.1 * cm))
                rows.append(row)

            col_widths = [cell_w_cm * cm] * cols
            grid = Table(rows, colWidths=col_widths, hAlign="LEFT", repeatRows=0, splitByRow=1)
            grid.setStyle(TableStyle([
                ("LEFTPADDING",  (0,0), (-1,-1), 0),
                ("RIGHTPADDING", (0,0), (-1,-1), 0),
                ("TOPPADDING",   (0,0), (-1,-1), 0),
                ("BOTTOMPADDING",(0,0), (-1,-1), 0),
                ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ]))
            story.append(grid)

            if page_idx * figs_per_page < len(cards):
                story.append(PageBreak())

    # Apêndice: resumo da exportação
    story.append(PageBreak())
    story.append(Paragraph("Apêndice – Resumo da Exportação", styles["Heading2"]))
    linhas = [["Seção", "Status"]]
    if export_log:
        for titulo_s, status in export_log:
            linhas.append([titulo_s, status])
    else:
        linhas.append(["(Sem entradas de exportação)", "—"])
    resumo_tbl = Table(linhas, colWidths=[12.5 * cm, 4.5 * cm])
    resumo_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    story.append(resumo_tbl)

    doc.build(story)
    buf.seek(0)
    return buf.read()
