"""
Executive Dashboard for ChurnGuard AI
-------------------------------------
Displays:
- Customer KPIs
- Retention vs churn distribution
- Churn rate by contract type
- Churn volume by tenure group
- Data-driven churn drivers
- High-risk customer segment

Dataset: IBM Telco Customer Churn
"""

import os
import sys

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)


# ---------------------------------------------------------
# PROJECT IMPORTS
# ---------------------------------------------------------

from preprocessing import load_raw_data, clean_data

from components.ui import (
    render_page_header,
    render_insight_box,
    render_footer,
    PLOTLY_DARK_LAYOUT,
    apply_custom_css,
)


# ---------------------------------------------------------
# COLORS
# ---------------------------------------------------------

COLORS = {
    "retained": "#82B5AD",
    "churned": "#D995A5",
    "primary": "#9290CF",
    "secondary": "#A5A7BB",
    "background": "#202230",
    "surface": "#2A2C3C",
    "text": "#E6E6F0",
    "muted": "#A5A7BB",
    "warning": "#D8B77D",
    "danger": "#D995A5",
    "success": "#8BC5A9",
}


# ---------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------

@st.cache_data
def get_dashboard_data():
    """
    Load and clean the customer churn dataset.
    """

    data_path = os.path.join(
        PROJECT_ROOT,
        "data",
        "customer_churn.csv",
    )

    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Customer churn dataset not found at:\n{data_path}"
        )

    df = load_raw_data(data_path)
    df = clean_data(df)

    required_columns = [
        "Churn",
        "Contract",
        "PaymentMethod",
        "tenure",
        "MonthlyCharges",
        "InternetService",
        "TechSupport",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "The cleaned dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    # Ensure tenure is numeric
    df["tenure"] = pd.to_numeric(
        df["tenure"],
        errors="coerce",
    ).fillna(0)

    # Ensure monthly charges are numeric
    df["MonthlyCharges"] = pd.to_numeric(
        df["MonthlyCharges"],
        errors="coerce",
    ).fillna(0)

    # Create tenure groups
    tenure_bins = [-1, 12, 24, 48, 72, float("inf")]

    tenure_labels = [
        "0–12 Months",
        "13–24 Months",
        "25–48 Months",
        "49–72 Months",
        "72+ Months",
    ]

    df["TenureGroup"] = pd.cut(
        df["tenure"],
        bins=tenure_bins,
        labels=tenure_labels,
        include_lowest=True,
        ordered=True,
    )

    return df


# ---------------------------------------------------------
# PLOTLY THEME HELPER
# ---------------------------------------------------------

def style_chart(fig, height=320):
    """
    Apply the common Plotly theme.

    Important:
    PLOTLY_DARK_LAYOUT already contains a margin property.
    We merge dictionaries instead of passing margin twice.
    """

    chart_layout = {
        **PLOTLY_DARK_LAYOUT,
        "height": height,
        "margin": {
            "l": 20,
            "r": 20,
            "t": 30,
            "b": 25,
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "color": COLORS["text"],
            "family": "Inter, sans-serif",
            "size": 12,
        },
        "hoverlabel": {
            "bgcolor": COLORS["surface"],
            "font_color": COLORS["text"],
            "bordercolor": COLORS["primary"],
        },
    }

    fig.update_layout(**chart_layout)

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(255,255,255,0.08)",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.07)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.08)",
    )

    return fig


# ---------------------------------------------------------
# KPI CARD
# ---------------------------------------------------------

def render_kpi_card(
    title,
    value,
    subtitle,
    card_class="",
):
    """
    Render a dashboard KPI card.
    """

    st.markdown(
        f"""
        <div class="kpi-card {card_class}">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------

def calculate_churn_rate(data):
    """
    Calculate churn percentage for a dataframe.
    """

    if data.empty:
        return 0.0

    return float(
        (data["Churn"] == "Yes").mean() * 100
    )


def get_segment_churn_rate(data, column, value):
    """
    Calculate churn percentage for a specific segment.
    """

    segment = data[data[column] == value]

    if segment.empty:
        return 0.0

    return calculate_churn_rate(segment)


def get_top_churn_segment(data, column):
    """
    Find the segment with the highest churn rate.
    """

    if column not in data.columns or data.empty:
        return None, 0.0

    summary = (
        data.groupby(column, dropna=False)["Churn"]
        .apply(lambda values: (values == "Yes").mean() * 100)
        .dropna()
    )

    if summary.empty:
        return None, 0.0

    highest_segment = summary.idxmax()
    highest_rate = float(summary.max())

    return highest_segment, highest_rate


# ---------------------------------------------------------
# DASHBOARD PAGE
# ---------------------------------------------------------

def render_dashboard_page():

    render_page_header(
        "Executive Churn Dashboard",
        "Monitor customer retention, identify churn patterns, "
        "and discover high-risk customer segments.",
    )

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    try:
        df = get_dashboard_data()

    except Exception as error:
        st.error(
            f"Unable to load dashboard data: {error}"
        )
        st.stop()

    if df.empty:
        st.warning(
            "The customer dataset is empty. "
            "Please check your dataset."
        )
        st.stop()

    # -----------------------------------------------------
    # KPI CALCULATIONS
    # -----------------------------------------------------

    total_customers = len(df)

    churned_count = int(
        (df["Churn"] == "Yes").sum()
    )

    retained_count = int(
        (df["Churn"] == "No").sum()
    )

    churn_rate = calculate_churn_rate(df)

    retention_rate = (
        retained_count / total_customers * 100
        if total_customers > 0
        else 0
    )

    # High-risk segment:
    # Month-to-month + Electronic Check + Tenure <= 12 months

    high_risk_filter = (
        (df["Contract"] == "Month-to-month")
        & (df["PaymentMethod"] == "Electronic check")
        & (df["tenure"] <= 12)
    )

    high_risk_customers = df[high_risk_filter]

    high_risk_count = len(high_risk_customers)

    high_risk_churn_rate = calculate_churn_rate(
        high_risk_customers
    )

    # -----------------------------------------------------
    # DASHBOARD KPI ROW
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="section-label">
            CUSTOMER OVERVIEW
        </div>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        render_kpi_card(
            "TOTAL CUSTOMERS",
            f"{total_customers:,}",
            "Total customer base",
        )

    with k2:
        render_kpi_card(
            "RETAINED CUSTOMERS",
            f"{retained_count:,}",
            f"{retention_rate:.1f}% retention rate",
            "retained",
        )

    with k3:
        render_kpi_card(
            "CHURNED CUSTOMERS",
            f"{churned_count:,}",
            "Customers who left",
            "churn",
        )

    with k4:
        render_kpi_card(
            "OVERALL CHURN RATE",
            f"{churn_rate:.2f}%",
            "Historical customer churn",
            "churn",
        )

    with k5:
        render_kpi_card(
            "HIGH-RISK COHORT",
            f"{high_risk_count:,}",
            f"{high_risk_churn_rate:.1f}% segment churn rate",
            "churn",
        )

    st.write("")


    # -----------------------------------------------------
    # ROW 1: RETENTION DONUT + CONTRACT CHURN
    # -----------------------------------------------------

    left_col, right_col = st.columns(
        [1, 1.25],
        gap="large",
    )

    # -----------------------------------------------------
    # RETENTION DONUT
    # -----------------------------------------------------

    with left_col:

        st.markdown(
            """
            <div class="glass-card">
                <h4 style="margin:0; color:#ffffff;">
                    Customer Retention Distribution
                </h4>
                <p style="color:#A5A7BB; font-size:0.82rem;">
                    Retained customers compared with churned customers
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        donut_fig = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        "Retained",
                        "Churned",
                    ],
                    values=[
                        retained_count,
                        churned_count,
                    ],
                    hole=0.68,
                    sort=False,
                    marker=dict(
                        colors=[
                            COLORS["retained"],
                            COLORS["churned"],
                        ],
                        line=dict(
                            color=COLORS["background"],
                            width=3,
                        ),
                    ),
                    textinfo="percent",
                    textposition="outside",
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Customers: %{value:,}<br>"
                        "Share: %{percent}"
                        "<extra></extra>"
                    ),
                )
            ]
        )

        donut_layout = {
            **PLOTLY_DARK_LAYOUT,
            "height": 310,
            "showlegend": False,
            "margin": {
                "l": 10,
                "r": 10,
                "t": 20,
                "b": 10,
            },
            "annotations": [
                dict(
                    text=(
                        f"<b>{churn_rate:.1f}%</b>"
                        "<br>"
                        "<span style='font-size:12px;'>Churn Rate</span>"
                    ),
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(
                        size=20,
                        color=COLORS["text"],
                    ),
                )
            ],
        }

        donut_fig.update_layout(**donut_layout)

        st.plotly_chart(
            donut_fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

        render_insight_box(
            f"Out of {total_customers:,} customers, "
            f"{churned_count:,} have churned. "
            f"The overall churn rate is {churn_rate:.2f}%, "
            f"while {retention_rate:.2f}% of customers remain."
        )


    # -----------------------------------------------------
    # CHURN BY CONTRACT
    # -----------------------------------------------------

    with right_col:

        st.markdown(
            """
            <div class="glass-card">
                <h4 style="margin:0; color:#ffffff;">
                    Churn Rate by Contract Type
                </h4>
                <p style="color:#A5A7BB; font-size:0.82rem;">
                    Customer retention patterns across contract categories
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        contract_summary = (
            df.groupby("Contract")["Churn"]
            .value_counts(normalize=True)
            .unstack(fill_value=0)
            * 100
        )

        # Ensure both churn classes exist
        for churn_class in ["No", "Yes"]:
            if churn_class not in contract_summary.columns:
                contract_summary[churn_class] = 0

        contract_summary = contract_summary.reset_index()

        contract_fig = go.Figure()

        contract_fig.add_trace(
            go.Bar(
                name="Retained",
                x=contract_summary["Contract"],
                y=contract_summary["No"],
                marker_color=COLORS["retained"],
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Retained: %{y:.1f}%"
                    "<extra></extra>"
                ),
            )
        )

        contract_fig.add_trace(
            go.Bar(
                name="Churned",
                x=contract_summary["Contract"],
                y=contract_summary["Yes"],
                marker_color=COLORS["churned"],
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Churned: %{y:.1f}%"
                    "<extra></extra>"
                ),
            )
        )

        contract_layout = {
            **PLOTLY_DARK_LAYOUT,
            "barmode": "stack",
            "height": 310,
            "margin": {
                "l": 20,
                "r": 20,
                "t": 20,
                "b": 25,
            },
            "yaxis_title": "Customers (%)",
            "yaxis": {
                "range": [0, 100],
                "ticksuffix": "%",
            },
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
        }

        contract_fig.update_layout(**contract_layout)

        contract_fig = style_chart(
            contract_fig,
            height=310,
        )

        st.plotly_chart(
            contract_fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

        month_to_month_rate = get_segment_churn_rate(
            df,
            "Contract",
            "Month-to-month",
        )

        two_year_rate = get_segment_churn_rate(
            df,
            "Contract",
            "Two year",
        )

        render_insight_box(
            f"Month-to-month customers have a churn rate of "
            f"{month_to_month_rate:.1f}%. "
            f"Customers on two-year contracts have a churn rate "
            f"of {two_year_rate:.1f}%. "
            "Longer contracts are associated with stronger retention."
        )


    # -----------------------------------------------------
    # ROW 2: TENURE ANALYSIS + CHURN DRIVERS
    # -----------------------------------------------------

    st.write("")

    tenure_col, drivers_col = st.columns(
        [1.2, 1],
        gap="large",
    )

    # -----------------------------------------------------
    # TENURE ANALYSIS
    # -----------------------------------------------------

    with tenure_col:

        st.markdown(
            """
            <div class="glass-card">
                <h4 style="margin:0; color:#ffffff;">
                    Churn Volume by Customer Tenure
                </h4>
                <p style="color:#A5A7BB; font-size:0.82rem;">
                    Compare retained and churned customers by tenure group
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tenure_summary = (
            df.groupby(
                ["TenureGroup", "Churn"],
                observed=False,
            )
            .size()
            .reset_index(name="Customer Count")
        )

        tenure_fig = px.bar(
            tenure_summary,
            x="TenureGroup",
            y="Customer Count",
            color="Churn",
            barmode="group",
            color_discrete_map={
                "No": COLORS["retained"],
                "Yes": COLORS["churned"],
            },
            category_orders={
                "TenureGroup": [
                    "0–12 Months",
                    "13–24 Months",
                    "25–48 Months",
                    "49–72 Months",
                    "72+ Months",
                ],
                "Churn": [
                    "No",
                    "Yes",
                ],
            },
            labels={
                "TenureGroup": "Customer Tenure",
                "Churn": "Customer Status",
            },
        )

        tenure_fig = style_chart(
            tenure_fig,
            height=320,
        )

        tenure_fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            )
        )

        st.plotly_chart(
            tenure_fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

        early_tenure_df = df[df["tenure"] <= 12]

        early_tenure_churn_rate = calculate_churn_rate(
            early_tenure_df
        )

        render_insight_box(
            f"Customers in their first 12 months have a churn rate "
            f"of {early_tenure_churn_rate:.1f}%. "
            "Early customer engagement and onboarding can help "
            "identify retention opportunities."
        )


    # -----------------------------------------------------
    # TOP CHURN DRIVERS
    # -----------------------------------------------------

    with drivers_col:

        st.markdown(
            """
            <div class="glass-card">
                <h4 style="margin-top:0; color:#ffffff;">
                    Top Churn Drivers
                </h4>
                <p style="color:#A5A7BB; font-size:0.82rem;">
                    Customer segments with the highest observed churn rates
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        driver_columns = [
            "Contract",
            "PaymentMethod",
            "InternetService",
            "TechSupport",
        ]

        driver_labels = {
            "Contract": "Contract Type",
            "PaymentMethod": "Payment Method",
            "InternetService": "Internet Service",
            "TechSupport": "Tech Support",
        }

        driver_results = []

        for column in driver_columns:

            segment_name, segment_rate = get_top_churn_segment(
                df,
                column,
            )

            if segment_name is not None:

                driver_results.append(
                    {
                        "label": driver_labels[column],
                        "segment": str(segment_name),
                        "rate": segment_rate,
                    }
                )

        driver_results.sort(
            key=lambda item: item["rate"],
            reverse=True,
        )

        # Use Streamlit-native elements instead of raw HTML. This avoids
        # HTML being displayed as text if Markdown sanitization/theme changes.
        for index, driver in enumerate(driver_results[:4], start=1):
            with st.container(border=True):
                header_col, rate_col = st.columns([3, 1])

                with header_col:
                    st.caption(f"DRIVER {index}")
                    st.markdown(f"**{driver['label']}**")

                with rate_col:
                    st.metric(
                        label="Churn rate",
                        value=f"{driver['rate']:.1f}%",
                    )

                st.caption(
                    f"Highest churn segment: {driver['segment']}"
                )

        st.caption(
            "These are observed segment-level churn rates. "
            "They show association, not proof of causation."
        )


    # -----------------------------------------------------
    # HIGH-RISK CUSTOMER SEGMENT
    # -----------------------------------------------------

    st.write("")

    st.markdown(
        """
        <div class="glass-card">
            <h4 style="margin:0; color:#ffffff;">
                High-Risk Customer Segment
            </h4>
            <p style="color:#A5A7BB; font-size:0.82rem;">
                Customers with month-to-month contracts, electronic
                check payments, and 12 months or less of tenure.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    risk_col1, risk_col2, risk_col3 = st.columns(3)

    with risk_col1:
        render_kpi_card(
            "SEGMENT SIZE",
            f"{high_risk_count:,}",
            "Customers matching the segment",
            "churn",
        )

    with risk_col2:
        render_kpi_card(
            "SEGMENT CHURN RATE",
            f"{high_risk_churn_rate:.1f}%",
            "Observed churn within this segment",
            "churn",
        )

    with risk_col3:
        render_kpi_card(
            "CHURNED IN SEGMENT",
            f"{int((high_risk_customers['Churn'] == 'Yes').sum()):,}",
            "Customers who have churned",
            "churn",
        )

    if high_risk_count > 0:

        render_insight_box(
            f"This segment contains {high_risk_count:,} customers, "
            f"with an observed churn rate of "
            f"{high_risk_churn_rate:.1f}%. "
            "It may be useful to prioritize these customers "
            "for retention outreach."
        )

    else:

        st.info(
            "No customers currently match the selected high-risk criteria."
        )


    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    render_footer()


# ---------------------------------------------------------
# STANDALONE EXECUTION
# ---------------------------------------------------------

if __name__ == "__main__":

    apply_custom_css()

    if not st.session_state.get(
        "authenticated",
        False,
    ):

        st.warning(
            "Authentication Required: Please sign in "
            "on the main portal to access this page."
        )

        st.stop()

    render_dashboard_page()