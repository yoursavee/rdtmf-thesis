import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from urllib.parse import quote_plus

st.set_page_config(
    page_title="RDTMF MySQL Dashboard",
    layout="wide"
)

st.title("RDTMF Thesis Results Dashboard")
st.write("This dashboard displays RDTMF implementation results stored in the MySQL database.")

with st.sidebar:
    st.header("MySQL Connection")

    mysql_user = st.text_input("MySQL username", value="root")
    mysql_password = st.text_input("MySQL password", type="password")
    mysql_host = st.text_input("Host", value="localhost")
    mysql_port = st.number_input("Port", value=3306)
    database_name = st.text_input("Database", value="rdtmf_thesis")

if mysql_user == "":
    st.warning("Please enter MySQL username.")
    st.stop()

encoded_password = quote_plus(mysql_password)

if mysql_password:
    connection_url = f"mysql+pymysql://{mysql_user}:{encoded_password}@{mysql_host}:{mysql_port}/{database_name}"
else:
    connection_url = f"mysql+pymysql://{mysql_user}@{mysql_host}:{mysql_port}/{database_name}"

try:
    engine = create_engine(connection_url)
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

tables = {
    "Final Evaluation Metrics": "final_evaluation_metrics",
    "Multi-Attack Detection Metrics": "multi_attack_detection_metrics",
    "Thesis Multi-Attack Detection Table": "thesis_multi_attack_detection_table",
    "Top N Recommendations": "top_n_recommendations_user_0",
    "Recommendation Summary": "recommendation_summary_user_0",
    "Access Decisions": "access_decisions_user_0",
    "Access Decision Summary": "access_decision_summary_user_0",
    "Flagged Users": "flagged_users",
    "Detection Metrics": "detection_metrics",
    "Final Result Summary": "final_result_summary"
}

selected_label = st.sidebar.selectbox(
    "Select result table",
    list(tables.keys())
)

selected_table = tables[selected_label]

try:
    df = pd.read_sql(f"SELECT * FROM {selected_table}", engine)

    st.subheader(selected_label)
    st.dataframe(df, use_container_width=True)

    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download selected table as CSV",
        data=csv_data,
        file_name=f"{selected_table}.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Could not load table: {e}")
    st.stop()

st.divider()

st.subheader("Key Visual Results")

try:
    eval_df = pd.read_sql("SELECT * FROM final_evaluation_metrics", engine)
    eval_df["Value"] = pd.to_numeric(eval_df["Value"], errors="coerce")

    st.write("Final Evaluation Metrics")
    st.bar_chart(eval_df.set_index("Metric")["Value"])

except Exception as e:
    st.warning(f"Could not load final evaluation chart: {e}")

try:
    attack_df = pd.read_sql("SELECT * FROM multi_attack_detection_metrics", engine)

    st.write("Detection Rate and False Positive Rate Across Attack Levels")

    attack_chart = attack_df[
        ["attack_percentage", "detection_rate", "false_positive_rate"]
    ].set_index("attack_percentage")

    st.line_chart(attack_chart)

except Exception as e:
    st.warning(f"Could not load attack detection chart: {e}")

try:
    rec_df = pd.read_sql("SELECT * FROM top_n_recommendations_user_0", engine)

    st.write("Top N Trusted Services")

    if "service_id" in rec_df.columns and "final_trust" in rec_df.columns:
        rec_chart = rec_df[["service_id", "final_trust"]].copy()
        rec_chart["service_id"] = rec_chart["service_id"].astype(str)
        st.bar_chart(rec_chart.set_index("service_id")["final_trust"])

except Exception as e:
    st.warning(f"Could not load recommendation chart: {e}")

try:
    access_df = pd.read_sql("SELECT * FROM access_decision_summary_user_0", engine)

    st.write("RBAC Access Decision Summary")

    if "access_decision" in access_df.columns and "count" in access_df.columns:
        st.bar_chart(access_df.set_index("access_decision")["count"])

except Exception as e:
    st.warning(f"Could not load access decision chart: {e}")
