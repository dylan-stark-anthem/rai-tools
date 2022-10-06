"""Plotly helpers for data drift."""

from typing import Any, Dict, List

import bs4
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def plotly_data_summary_maker(
    num_numerical_features: int, num_categorical_features: int
) -> str:
    """Creates an easy-to-test version of a data summary."""
    fig = make_subplots(
        rows=1,
        cols=2,
        start_cell="top-left",
        horizontal_spacing=0.05,
        vertical_spacing=0.15,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
    )
    fig.add_trace(
        trace=go.Indicator(
            mode="number",
            value=num_numerical_features,
            title={
                "text": "Numerical features",
                "font": {"size": 24, "color": "white"},
            },
            number={
                "font": {"size": 90},
                "valueformat": "f",
            },
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        trace=go.Indicator(
            mode="number",
            value=num_categorical_features,
            title={
                "text": "Categorical features",
                "font": {"size": 24, "color": "white"},
            },
            number={
                "font": {"size": 90},
                "valueformat": "f",
            },
        ),
        row=1,
        col=2,
    )
    fig.update_layout(
        {
            "title": {
                "text": "Data Summary",
                "font": {
                    "size": 40,
                },
            },
            "title_x": 0.49,
            "title_y": 0.86,
            "template": "plotly_dark",
            "height": 340,
            "width": 1775,
            "margin": {"l": 100, "r": 100, "b": 50, "t": 160},
        }
    )
    html = fig.to_html()

    return html


def plotly_drift_summary_maker(
    num_total_features: int,
    num_features_drifted: int,
    num_top_10_features_drifted: int,
    num_top_20_features_drifted: int,
) -> str:
    """Creates an easy-to-test version of a drift summary."""
    fig = make_subplots(
        rows=1,
        cols=4,
        start_cell="top-left",
        horizontal_spacing=0.2,
        vertical_spacing=0.15,
        specs=[
            [
                {"type": "domain"},
                {"type": "domain"},
                {"type": "domain"},
                {"type": "domain"},
            ]
        ],
    )
    fig.add_trace(
        trace=go.Indicator(
            mode="number",
            value=num_total_features,
            title={
                "text": "Total features",
                "font": {"size": 24, "color": "white"},
            },
            number={
                "font": {"size": 90, "color": "#F4C430"},
                "valueformat": "f",
            },
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        trace=go.Indicator(
            mode="number",
            value=num_features_drifted,
            title={
                "text": "Features drifted",
                "font": {"size": 24, "color": "white"},
            },
            number={
                "font": {"size": 90, "color": "red"},
                "valueformat": "f",
            },
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        trace=go.Indicator(
            mode="number",
            value=num_top_10_features_drifted,
            title={
                "text": "Top 10 features drifted",
                "font": {"size": 24, "color": "white"},
            },
            number={
                "font": {"size": 90, "color": "green"},
                "valueformat": "f",
            },
        ),
        row=1,
        col=3,
    )
    fig.add_trace(
        trace=go.Indicator(
            mode="number",
            value=num_top_20_features_drifted,
            title={
                "text": "Top 20 features drifted",
                "font": {"size": 24, "color": "white"},
            },
            number={
                "font": {"size": 90, "color": "#fc8eac"},
                "valueformat": "f",
            },
        ),
        row=1,
        col=4,
    )
    fig.update_layout(
        {
            "title": {
                "text": "Drift summary",
                "font": {
                    "size": 40,
                },
            },
            "title_x": 0.49,
            "title_y": 0.87,
            "template": "plotly_dark",
            "height": 360,
            "width": 1775,
            "margin": {"l": 100, "r": 150, "b": 70, "t": 160},
        }
    )
    fig.update_layout(
        shapes=[
            {
                "type": "rect",
                "xref": "paper",
                "yref": "paper",
                "x0": -0.04,
                "y0": 0.02,
                "x1": 0.17,
                "y1": 1.35,
                "fillcolor": "#1f2c56",
                "opacity": 0.5,
                "layer": "below",
                "line_width": 0,
            },
            {
                "type": "rect",
                "xref": "paper",
                "yref": "paper",
                "x0": 0.24,
                "y0": 0.02,
                "x1": 0.46,
                "y1": 1.35,
                "fillcolor": "#1f2c56",
                "opacity": 0.5,
                "layer": "below",
                "line_width": 0,
            },
            {
                "type": "rect",
                "xref": "paper",
                "yref": "paper",
                "x0": 0.53,
                "y0": 0.02,
                "x1": 0.77,
                "y1": 1.35,
                "fillcolor": "#1f2c56",
                "opacity": 0.5,
                "layer": "below",
                "line_width": 0,
            },
            {
                "type": "rect",
                "xref": "paper",
                "yref": "paper",
                "x0": 0.83,
                "y0": 0.02,
                "x1": 1.07,
                "y1": 1.35,
                "fillcolor": "#1f2c56",
                "opacity": 0.5,
                "layer": "below",
                "line_width": 0,
            },
        ]
    )
    html = fig.to_html(include_plotlyjs=False, full_html=False)
    return html


def plotly_drift_magnitude_maker(
    fields: List[str], observations: Dict[str, List[Any]]
) -> str:
    """Creates an easy-to-test version of drift magnitude section."""
    soup = bs4.BeautifulSoup("")
    soup.append(soup.new_tag("table"))
    soup.table.append(soup.new_tag("thead"))
    soup.table.thead.append(soup.new_tag("tr"))
    for field in fields:
        th = soup.new_tag("th")
        th.string = field
        soup.table.thead.tr.append(th)

    cell_values = [values for values in observations.values()]

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=fields, fill_color="grey", align="left"),
                cells=dict(
                    values=cell_values,
                    fill_color="lightgrey",
                    align="left",
                ),
            )
        ]
    )
    fig.update_traces(
        header_line_color="black",
        header_fill_color="#AFEEEE",
        header_align="left",
        header_font_size=18,
        header_font_color="black",
        header_values=fields,
        cells_line_color="black",
        cells_fill_color="#E0FFFF",
        cells_align="left",
        cells_font_size=14,
        cells_font_color="black",
        cells_height=30,
    )
    fig.update_layout(
        {
            "title": {
                "text": "Drift details",
                "font": {
                    "size": 40,
                },
            },
            "title_x": 0.49,
            "title_y": 0.87,
            "margin": {"l": 155, "r": 130, "b": 90, "t": 150},
        }
    )
    fig.update_layout(
        width=1775,
        height=530,
        template="plotly_dark",
    )

    html = fig.to_html(include_plotlyjs=False, full_html=False)
    return html
