"""HTML report builder for data drift."""


from datetime import datetime
from typing import Any, Callable, Dict, List

from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord


class HtmlReportBuilder:
    """HTML report builder for data drift."""

    def __init__(
        self,
    ) -> None:
        """Initializes report builder."""
        self.record: DataDriftRecord

        self.thresholds_list_maker: Callable[
            [Dict[str, Dict[str, float]]], str
        ] = basic_thresholds_list_maker
        self.data_summary_maker: Callable[[int, int], str]
        self.drift_summary_maker: Callable[[int, int, int, int], str]
        self.drift_magnitude_maker: Callable[[List[str], Dict[str, List[Any]]], str]

    def compile(self) -> None:
        """Builds an HTML report."""
        timestamp_date = datetime.fromisoformat(self.record.results.metadata.timestamp)
        timestamp_str = timestamp_date.strftime("%Y-%m-%d %H:%M:%S (%Z)")

        thresholds_list_html = self.thresholds_list_maker(
            self.record.results.metadata.thresholds
        )
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
                    <title>{self.record.bundle.job_config.report_name}</title>
                </head>
                <body>
                    <h3 style ='color: darkred'>Timestamp: {timestamp_str}</h3>
                    <h3 style ='color: darkred'> Report name: {self.record.bundle.job_config.report_name} </h3>
                    <h3 style ='color: darkred'> Dataset name: {self.record.bundle.job_config.dataset_name} </h3>
                    <h3 style ='color: darkred'> Dataset Version: {self.record.bundle.job_config.dataset_version} </h3>
                    <h3 style ='color: darkred'> Model Catalog ID: {self.record.bundle.job_config.model_catalog_id} </h3>
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
                            <td>{self.record.bundle.data["baseline_data"].num_rows} X {self.record.bundle.data["baseline_data"].num_columns}</td>
                            <td>{self.record.bundle.data["test_data"].num_rows} X {self.record.bundle.data["test_data"].num_columns}</td>
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
