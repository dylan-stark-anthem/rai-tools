"""Simple report builder."""

from typing import Any, Dict, List

import bs4

from raitools.services.data_drift.data.data_drift_record import DataDriftRecord
from raitools.services.data_drift.reports.html_report_builder import HtmlReportBuilder


def simple_report_builder(record: DataDriftRecord) -> str:
    """Creates a report builder for the simple test case."""
    report_builder = HtmlReportBuilder()
    report_builder.data_summary_maker = basic_data_summary_maker
    report_builder.drift_summary_maker = basic_drift_summary_maker
    report_builder.drift_magnitude_maker = basic_drift_magnitude_maker
    report_builder.record = record
    report_builder.compile()
    return report_builder.get()


def basic_data_summary_maker(
    num_numerical_features: int, num_categorical_features: int
) -> str:
    """Creates an easy-to-test version of a data summary."""
    html = f"""
        <p>This is the "Data Summary".</p>
        <p>It contains two data cards: "Numerical features" showing {num_numerical_features} and "Categorical features" showing {num_categorical_features}.</p>
        """  # noqa: B950
    return html


def basic_drift_summary_maker(
    num_total_features: int,
    num_features_drifted: int,
    num_top_10_features_drifted: int,
    num_top_20_features_drifted: int,
) -> str:
    """Creates an easy-to-test version of a drift summary."""
    html = f"""
        <p>This is the "Drift Summary".</p>
        <p>It contains four data cards:
        "Total Features" showing {num_total_features}.
        "Features Drifted" showing {num_features_drifted}.
        "Top 10 Features Drifted" showing {num_top_10_features_drifted}.
        "Top 20 Features Drifted" showing {num_top_20_features_drifted}.
    """
    return html


def basic_drift_magnitude_maker(
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

    num_observations = len(observations[fields[0]])
    soup.table.append(soup.new_tag("tbody"))
    for row in range(num_observations):
        tr = soup.new_tag("tr")
        for column in fields:
            td = soup.new_tag("td")
            td.string = str(observations[column][row])
            tr.append(td)
        soup.table.tbody.append(tr)

    html = f"""
        <p>
            This is the "Drift Magnitude" section.
            There are two visualizations: a heatmap and a table.
            In the heatmap, "Each cell contains the p-value for the top <= 100 features",
            there are 10 columns, and each row is labeled with the range
            of feature ranks displayed (e.g., 1-10, 2-20, ...).

            The table has more detail, such as the "Feature Rank",
            "Feature Name", "Feature Type", "p-value", and "Drift Status".
        </p>
        {soup}
    """

    return html
