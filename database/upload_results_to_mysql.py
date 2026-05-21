import getpass
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
DATABASE_NAME = "rdtmf_thesis"

MYSQL_USER = input("Enter MySQL username, usually root: ")
MYSQL_PASSWORD = getpass.getpass("Enter MySQL password. If no password, just press Enter: ")
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306

password_part = f":{MYSQL_PASSWORD}" if MYSQL_PASSWORD else ""

server_engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}{password_part}@{MYSQL_HOST}:{MYSQL_PORT}"
)

with server_engine.connect() as connection:
    connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
    connection.commit()

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}{password_part}@{MYSQL_HOST}:{MYSQL_PORT}/{DATABASE_NAME}"
)

csv_tables = {
    "final_evaluation_metrics": RESULTS_DIR / "final_evaluation_metrics.csv",
    "multi_attack_detection_metrics": RESULTS_DIR / "multi_attack_detection_metrics.csv",
    "thesis_multi_attack_detection_table": RESULTS_DIR / "thesis_multi_attack_detection_table.csv",
    "top_n_recommendations_user_0": RESULTS_DIR / "top_n_recommendations_user_0.csv",
    "recommendation_summary_user_0": RESULTS_DIR / "recommendation_summary_user_0.csv",
    "access_decisions_user_0": RESULTS_DIR / "access_decisions_user_0.csv",
    "access_decision_summary_user_0": RESULTS_DIR / "access_decision_summary_user_0.csv",
    "flagged_users": RESULTS_DIR / "flagged_users.csv",
    "detection_metrics": RESULTS_DIR / "detection_metrics.csv",
    "final_result_summary": RESULTS_DIR / "final_result_summary.csv"
}

for table_name, csv_path in csv_tables.items():
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False
        )
        print(f"Uploaded table: {table_name} | rows: {len(df)}")
    else:
        print(f"Missing file: {csv_path}")

print("\nAll available RDTMF result tables uploaded to MySQL.")
print(f"Database name: {DATABASE_NAME}")
