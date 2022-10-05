"""HTML report generation."""

from collections import defaultdict
from pathlib import Path
import textwrap
import time
from typing import Any, Callable, Dict, List


from raitools.data_drift.domain.data_drift_record import DataDriftRecord


def plotly_data_summary_maker(
    num_numerical_features: int, num_categorical_features: int
) -> str:
    """Creates a plotly view of the data summary."""
    return ""


def plotly_drift_summary_maker(
    num_total_features: int,
    num_features_drifted: int,
    num_top_10_features_drifted: int,
    num_top_20_features_drifted: int,
) -> str:
    """Creates a plotly view of the data summary."""
    return ""


def plotly_drift_magnitude_maker(
    fields: List[str], observations: Dict[str, List[Any]]
) -> str:
    """Creates a plotly view of the data summary."""
    return ""


def generate_report(
    record: DataDriftRecord,
    output_path: Path,
    timestamp: str = None,
    data_summary_maker: Callable[[int, int], str] = plotly_data_summary_maker,
    drift_summary_maker: Callable[
        [int, int, int, int], str
    ] = plotly_drift_summary_maker,
    drift_magnitude_maker: Callable[
        [List[str], Dict[str, List[Any]]], str
    ] = plotly_drift_magnitude_maker,
) -> None:
    """Generates a report for the given record."""
    job_config = record.bundle.job_config

    report_name = job_config.report_name
    report_filename = f"{report_name}.html"
    report_path = output_path / report_filename

    if not timestamp:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # Create mapping for type of feature and tests
    thresholds: Dict[str, Dict[str, float]] = defaultdict(dict)
    for feature in record.drift_summary.features.values():
        kind = feature.kind
        test_name = feature.statistical_test.name
        threshold = feature.statistical_test.adjusted_significance_level
        thresholds[kind][test_name] = threshold
    thresholds_list = "<ul>\n"
    for kind, tests in thresholds.items():
        for test_name, threshold in tests.items():
            thresholds_list += f"    <li>For {kind} features, {test_name} test with a threshold of {threshold} is used</li>\n"
    thresholds_list += "</ul>"

    # Create drift summary statistics
    features = record.drift_summary.features.values()
    num_total_features = len(features)

    drifted_features = [
        feature for feature in features if feature.drift_status == "drifted"
    ]
    num_features_drifted = len(drifted_features)

    top_10_drifted_features = [
        feature for feature in drifted_features if feature.rank <= 10
    ]
    num_top_10_features_drifted = len(top_10_drifted_features)

    top_20_drifted_features = [
        feature for feature in drifted_features if feature.rank <= 20
    ]
    num_top_20_features_drifted = len(top_20_drifted_features)

    # Create magnitude table
    fields = [
        "rank",
        "name",
        "kind",
        "p_value",
        "drift_status",
    ]
    ranked_features = sorted(features, key=lambda x: x.rank)
    observations: Dict[str, Any] = {
        "rank": [feature.rank for feature in ranked_features],
        "name": [feature.name for feature in ranked_features],
        "kind": [feature.kind for feature in ranked_features],
        "p_value": [
            feature.statistical_test.result.p_value for feature in ranked_features
        ],
        "drift_status": [feature.drift_status for feature in ranked_features],
    }

    report_html = textwrap.dedent(
        f"""\
        <html>
            <head>
                <title>{report_name}</title>
            </head>
            <body>
                <h3 style ='color: darkred'>Timestamp : {timestamp}</h3>
                <h3 style ='color: darkred'> Report name  : {report_name} </h3>
                <h3 style ='color: darkred'> Dataset name  : {job_config.dataset_name} </h3>
                <h3 style ='color: darkred'> Dataset Version : {job_config.dataset_version} </h3>
                <h3 style ='color: darkred'> Model Catalog ID : {job_config.model_catalog_id} </h3>
                <h3 style ='color: darkred'>
                    {thresholds_list}
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
                        <td>{record.bundle.data["baseline_data"].num_rows} X {record.bundle.data["baseline_data"].num_columns}</td>
                        <td>{record.bundle.data["test_data"].num_rows} X {record.bundle.data["test_data"].num_columns}</td>
                      </tr>
                    </tbody>
                </table>
                <br/>
                <div>
                    {data_summary_maker(record.drift_summary.metadata.num_numerical_features, record.drift_summary.metadata.num_categorical_features)}
                </div>
                <br/>
                <div>
                    {drift_summary_maker(num_total_features, num_features_drifted, num_top_10_features_drifted, num_top_20_features_drifted)}
                </div>
                <br/>
                <div>
                    {drift_magnitude_maker(fields, observations)}
                </div>
                <br/>
            </body>
        </html>
        """  # noqa: B950
    )

    report_path.write_text(report_html)
