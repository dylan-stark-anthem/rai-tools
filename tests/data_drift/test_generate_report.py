"""Tests for generate report use case."""


from pathlib import Path
from typing import Any, Dict, List

import bs4

from raitools.data_drift.domain.data_drift_record import (
    DataDriftRecord,
)
from raitools.data_drift.use_cases.generate_report import generate_report


def test_can_generate_report(simple_record: DataDriftRecord, tmp_path: Path) -> None:
    """Tests that we can generate an HTML report."""
    timestamp = "1970-01-01 00:00:00"

    generate_report(
        simple_record,
        output_path=tmp_path,
        timestamp=timestamp,
        data_summary_maker=html_data_summary_maker,
        drift_summary_maker=html_drift_summary_maker,
        drift_magnitude_maker=html_drift_magnitude_maker,
    )

    job_config = simple_record.bundle.job_config

    report_name = simple_record.bundle.job_config.report_name
    report_filename = f"{report_name}.html"
    report_path = tmp_path / report_filename
    report_html = report_path.read_text()
    report_soup = bs4.BeautifulSoup(report_html, "html.parser")

    features = simple_record.drift_summary.features.values()
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

    # assert soup.head.title.string == report_name
    # assert soup.body.contents[1]["style"] == "color: darkred"
    # assert soup.body.contents[1]["style"].string == f"Timestamp : {timestamp}"
    # assert soup.body.contents[3]["style"] == "color: darkred"
    # assert soup.body.contents[3]["style"].string == f" Report name  : {report_name} "
    # assert soup.body.contents[5]["style"] == "color: darkred"
    # assert (
    #     soup.body.contents[5]["style"].string
    #     == f" Dataset name  : {job_config.dataset_name} "
    # )
    # assert soup.body.contents[7]["style"] == "color: darkred"
    # assert (
    #     soup.body.contents[7]["style"].string
    #     == f" Dataset Version : {job_config.dataset_version} "
    # )
    # assert soup.body.contents[9]["style"] == "color: darkred"
    # assert (
    #     soup.body.contents[9]["style"].string
    #     == f" Model Catalog ID : {job_config.model_catalog_id} "
    # )
    # assert soup.body.contents[11]["style"] == "color: darkred"
    # assert (
    #     soup.body.contents[11]["style"].string
    #     == f" Model Catalog ID : {job_config.model_catalog_id} "
    # )
    # assert soup.body.contents[11]

    # actual_thresholds_list = [
    #     li.string for li in soup.body.contents[11].ul.contents if li != "\n"
    # ]
    # expected_threshold_list = [
    #     "For numerical features, kolmogorov-smirnov test with a threshold of 0.025 is used",
    #     ">For categorical features, chi-square test with a threshold of 0.000388 is used<",
    # ]
    # assert actual_thresholds_list == expected_threshold_list

    actual_soup = bs4.BeautifulSoup(
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
                    <ul>
                        <li>For numerical features, kolmogorov-smirnov test with a threshold of 0.025 is used</li>
                        <li>For categorical features, chi-squared test with a threshold of 0.016667 is used</li>
                    </ul>
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
                        <td>{simple_record.bundle.data["baseline_data"].num_rows} X {simple_record.bundle.data["baseline_data"].num_columns}</td>
                        <td>{simple_record.bundle.data["test_data"].num_rows} X {simple_record.bundle.data["test_data"].num_columns}</td>
                      </tr>
                    </tbody>
                </table>
                <br/>
                <div>
                    {html_data_summary_maker(simple_record.drift_summary.metadata.num_numerical_features, simple_record.drift_summary.metadata.num_categorical_features)}
                </div>
                <br/>
                <div>
                    {html_drift_summary_maker(num_total_features, num_features_drifted, num_top_10_features_drifted, num_top_20_features_drifted)}
                </div>
                <br/>
                <div>
                    {html_drift_magnitude_maker(fields, observations)}
                </div>
                <br/>
            </body>
        </html>
        """,  # noqa: B950
        "html.parser",
    )

    assert actual_soup.prettify() == report_soup.prettify()


def html_data_summary_maker(
    num_numerical_features: int, num_categorical_features: int
) -> str:
    """Creates an easy-to-test version of a data summary."""
    html = f"""
        <p>This is the "Data Summary".</p>
        <p>It contains two data cards: "Numerical features" showing {num_numerical_features} and "Categorical features" showing {num_categorical_features}.</p>
        """  # noqa: B950
    return html


def html_drift_summary_maker(
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


def html_drift_magnitude_maker(
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
            td = soup.new_tag("")
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
