"""HTML report builder for data drift."""


import time
from typing import Any, Callable, Dict, List

import bs4
from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord

from raitools.services.data_drift.domain.data_drift_report import DataDriftReportRecord


class HtmlReportBuilder:
    """HTML report builder for data drift."""

    def __init__(
        self,
    ) -> None:
        """Initializes report builder."""
        self.timestamp: str = time.strftime("%Y-%m-%d %H:%M:%S")

        self.record: DataDriftRecord
        self.report_data: DataDriftReportRecord

        self.thresholds_list_maker: Callable[
            [Dict[str, Dict[str, float]]], str
        ] = basic_thresholds_list_maker
        self.data_summary_maker: Callable[[int, int], str]
        self.drift_summary_maker: Callable[[int, int, int, int], str]
        self.drift_magnitude_maker: Callable[[List[str], Dict[str, List[Any]]], str]

    def compile(self) -> None:
        """Builds an HTML report."""
        thresholds_list_html = self.thresholds_list_maker(self.report_data.thresholds)
        data_summary_html = self.data_summary_maker(
            self.record.results.data_summary.num_numerical_features,
            self.record.results.data_summary.num_categorical_features,
        )
        drift_summary_html = self.drift_summary_maker(
            self.record.results.drift_summary.num_total_features,
            self.record.results.drift_summary.num_features_drifted,
            self.record.results.drift_summary.top_10_features_drifted,
            self.record.results.drift_summary.top_20_features_drifted,
        )
        drift_magnitude_html = self.drift_magnitude_maker(
            self.record.results.drift_details.fields,
            self.record.results.drift_details.observations,
        )

        self.html = f"""\
            <html>
                <head>
                    <title>{self.report_data.report_name}</title>
                </head>
                <body>
                    <h3 style ='color: darkred'>Timestamp: {self.timestamp}</h3>
                    <h3 style ='color: darkred'> Report name: {self.report_data.report_name} </h3>
                    <h3 style ='color: darkred'> Dataset name: {self.report_data.dataset_name} </h3>
                    <h3 style ='color: darkred'> Dataset Version: {self.report_data.dataset_version} </h3>
                    <h3 style ='color: darkred'> Model Catalog ID: {self.report_data.model_catalog_id} </h3>
                    <h3 style ='color: darkred'>
                        {thresholds_list_html}
                    </h3>
                    <table border="1" class="dataframe">
                        <thead>
                          <tr style="text-align: right;">
                            <th>Baseline Data Size</th>
                            <th>Test Data Size</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td>{self.report_data.num_rows_baseline_data} X {self.report_data.num_columns_baseline_data}</td>
                            <td>{self.report_data.num_rows_test_data} X {self.report_data.num_columns_test_data}</td>
                          </tr>
                        </tbody>
                    </table>
                    <br/>
                    <div>
                        {data_summary_html}
                    </div>
                    <br/>
                    <div>
                        {drift_summary_html}
                    </div>
                    <br/>
                    <div>
                        {drift_magnitude_html}
                    </div>
                    <br/>
                </body>
            </html>
        """  # noqa: B950

    def get(self) -> str:
        """Gets final HTML string for the report."""
        return self.html


def basic_thresholds_list_maker(thresholds: Dict[str, Dict[str, float]]) -> str:
    """Creates HTML from thresholds list."""
    thresholds_list_html = "<ul>\n"
    for kind, tests in thresholds.items():
        for test_name, threshold in tests.items():
            thresholds_list_html += f"    <li>For {kind} features, {test_name} test with a threshold of {threshold} is used</li>\n"
    thresholds_list_html += "</ul>"
    return thresholds_list_html


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
