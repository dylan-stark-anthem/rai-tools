"""Plotly-based report builder."""

from typing import Any, Dict, List, Optional

import plotly.graph_objs as go
from plotly.subplots import make_subplots

from raitools.services.data_drift.data.data_drift_record import DataDriftRecord
from raitools.services.data_drift.reports.html_report_builder import HtmlReportBuilder


def plotly_report_builder(record: DataDriftRecord) -> Any:
    """Builds an HTML report with fancy plotly diagrams."""
    report_builder = HtmlReportBuilder()
    report_builder.data_summary_maker = plotly_data_summary_maker
    report_builder.drift_summary_maker = plotly_drift_summary_maker
    report_builder.drift_magnitude_maker = plotly_drift_magnitude_maker
    report_builder.record = record
    report_builder.compile()
    return report_builder.get()


def plotly_data_summary_maker(
    num_numerical_features: int, num_categorical_features: int
) -> str:
    """Creates an plotly version of a data summary."""
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
            "shapes": [
                {
                    "type": "rect",
                    "xref": "paper",
                    "yref": "paper",
                    "x0": 0.15,
                    "y0": 0.02,
                    "x1": 0.33,
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
                    "x0": 0.67,
                    "y0": 0.02,
                    "x1": 0.86,
                    "y1": 1.35,
                    "fillcolor": "#1f2c56",
                    "opacity": 0.5,
                    "layer": "below",
                    "line_width": 0,
                },
            ],
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
    """Creates an plotly version of a drift summary."""
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
            "shapes": [
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
            ],
        }
    )
    html = fig.to_html(include_plotlyjs=False, full_html=False)
    return html


def plotly_drift_magnitude_maker(
    fields: List[str], observations: Dict[str, List[Any]]
) -> str:
    """Creates an plotly version of drift magnitude section."""
    num_observations = len(observations[fields[0]])
    heatmap_data: List[Optional[Dict[str, Any]]] = [
        {field: observations[field][index] for field in fields}
        for index in range(num_observations)
    ]

    num_columns_in_heatmap = 10
    chunked_data = []
    for start in range(0, num_observations, num_columns_in_heatmap):
        stop = start + num_columns_in_heatmap
        if stop > num_observations:
            chunk = heatmap_data[start:num_observations]
            chunk.extend([None] * (num_columns_in_heatmap - len(chunk)))
        else:
            chunk = heatmap_data[start:stop]
        chunked_data.append(chunk)
    chunked_data.reverse()

    def hover_text(element: Optional[Dict[str, Any]]) -> str:
        text = []
        if element:
            text.append(f"Rank: {element['rank']}")
            text.append(f"Importance score: {element['importance_score']:.6f}")
            text.append(f"Name: {element['name']}")
            text.append(f"Kind: {element['kind'].capitalize()}")
            text.append(f"P-value: {element['p_value']:.3f}")
            text.append(f"Status: {element['drift_status'].capitalize()}")

        return "<br>".join(text)

    def display_text(element: Optional[Dict[str, Any]]) -> str:
        text = ""
        if element:
            text = f"{element['p_value']:.3f}"

        return text

    def z(element: Dict[str, Any]) -> Optional[Any]:
        z = element["p_value"]
        return z

    z_data = [[z(element) for element in chunk if element] for chunk in chunked_data]
    hover_text_data = [
        [hover_text(element) for element in chunk] for chunk in chunked_data
    ]
    display_text_data = [
        [display_text(element) for element in chunk] for chunk in chunked_data
    ]

    heatmap_fig = go.Figure(
        data=go.Heatmap(
            z=z_data,
            text=display_text_data,
            hoverongaps=False,
            hovertemplate="%{hovertext}",
            hovertext=hover_text_data,
            name="",
            showscale=False,
            texttemplate="%{text}",
        )
    )
    heatmap_fig.update_layout(
        {
            "title": {
                "text": "(Each cell contains the p-value for the top <= 100 features)",
                "font": {
                    "size": 20,
                },
            },
        }
    )

    def create_table_trace(fields: List[str], cell_values: List[List]) -> go.Table:
        table = go.Table(
            header=dict(values=fields, fill_color="grey", align="left"),
            cells=dict(
                values=cell_values,
                fill_color="lightgrey",
                align="left",
                format=["g", ".6f", "", "", ".3f", ""],
            ),
            visible=False,
        )
        return table

    cell_values = [observations[field] for field in fields]
    table_fig = go.Figure()

    num_observations_in_view = 10
    for start in range(0, num_observations, num_observations_in_view):
        stop = start + num_observations_in_view
        if stop > num_observations:
            view_values = [values[start:num_observations] for values in cell_values]
        else:
            view_values = [values[start:stop] for values in cell_values]
        step_trace = create_table_trace(fields, view_values)
        table_fig.add_trace(step_trace)

    table_fig.data[0].visible = True

    table_fig.update_traces(
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

    combined_fig = make_subplots(
        rows=2, cols=1, specs=[[{"type": "heatmap"}], [{"type": "domain"}]]
    )
    for trace in heatmap_fig["data"]:
        combined_fig.add_trace(trace=trace, row=1, col=1)
    for trace in table_fig["data"]:
        combined_fig.add_trace(trace=trace, row=2, col=1)
    sliders = _create_sliders(len(table_fig.data), len(combined_fig.data))
    combined_fig.update_layout(
        {
            "title": {
                "text": "Drift details<br><br><sup>(Each cell contains the p-value for the top <= 100 features)</sup>",
                "font": {
                    "size": 40,
                },
            },
            "title_x": 0.49,
            "title_y": 0.87,
            "width": 1775,
            "height": 1152,
            "template": "plotly_dark",
            "margin": {"l": 155, "r": 130, "b": 90, "t": 250},
            "xaxis": {"title": "x-label", "visible": False, "showticklabels": False},
            "yaxis": {
                "title": "y-label",
                "visible": False,
                "showticklabels": False,
            },
            "sliders": sliders,
        }
    )

    html = combined_fig.to_html(include_plotlyjs=False, full_html=False)
    return html


def _create_sliders(num_pages: int, num_figs: int) -> List:
    """Creates sliders for paginated table."""
    steps = []
    for index in range(num_pages):
        step: Dict = dict(
            method="restyle",
            args=[
                {"visible": [False] * num_figs},
            ],
            label=f"{index}",
        )
        step["args"][0]["visible"][0] = True  # Keep heatmap visible
        step["args"][0]["visible"][1 + index] = True
        steps.append(step)

    sliders = [
        dict(
            active=0,
            currentvalue={"prefix": "Table page: "},
            pad={"t": 50},
            steps=steps,
        )
    ]

    return sliders
