# #!/usr/bin/env python3
# import os
# import json
# from sqlalchemy import text, create_engine, inspect
# from openai import OpenAI

# # Instantiate the OpenAI client (reads OPENAI_API_KEY from env)
# client = OpenAI()

# # Files to track previous state and output schema summaries
# PREV_TABLES_FILE = "db_tables.json"
# SCHEMA_OUT_FILE   = "db_schema.txt"

# def load_previous_tables():
#     """Load the last-seen table list (or return empty list)."""
#     if os.path.exists(PREV_TABLES_FILE):
#         with open(PREV_TABLES_FILE, "r") as f:
#             return json.load(f)
#     return []

# def save_current_tables(tables):
#     """Persist the current table list to disk."""
#     with open(PREV_TABLES_FILE, "w") as f:
#         json.dump(tables, f, indent=2)

# def main():
#     # Check required env vars
#     database_url = os.getenv("DATABASE_URL")
#     if not database_url or not os.getenv("OPENAI_API_KEY"):
#         print("Error: Set both DATABASE_URL and OPENAI_API_KEY environment variables.")
#         return

#     # Connect to the database and inspect table names
#     engine = create_engine(database_url)
#     inspector = inspect(engine)
#     current_tables = inspector.get_table_names()

#     #  Load previously seen tables and compare
#     previous_tables = load_previous_tables()
#     if set(current_tables) == set(previous_tables):
#         print("No schema change detected. Exiting without regeneration.")
#         return

#     print("Detected schema change. Regenerating db_schema.txt ...")

#     summaries = []
#     for table in current_tables:
#         #  Fetch column names
#         columns = inspector.get_columns(table)
#         column_names = [col["name"] for col in columns]

#         #  Fetch sample rows (limit 3)
#         with engine.connect() as conn:
#             result = conn.execute(text(f"SELECT * FROM {table} LIMIT 3"))
#             sample_rows = [dict(row._mapping) for row in result]

#         #  Build metadata for GPT
#         metadata = {
#             "table":       table,
#             "columns":     column_names,
#             "sample_rows": sample_rows
#         }

#         system_msg = {
#             "role": "system",
#             "content": (
#                 "You are a warehouse data expert. "
#                 "Generate a Markdown table summarizing the given database table. "
#                 "Columns: Column Name, Description, Example Value."
#             )
#         }
#         user_msg = {
#             "role":    "user",
#             "content": json.dumps(metadata, default=str)
#         }

#         #  Call GPT-4o to produce the table summary
#         response       = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[system_msg, user_msg]
#         )
#         table_summary = response.choices[0].message.content.strip()

#         #  Prepend table header and collect
#         header = f"## Table name - {table}\n\n"
#         summaries.append(header + table_summary + "\n")

#     #  Write out the new schema summary file
#     with open(SCHEMA_OUT_FILE, "w") as f:
#         f.write("\n".join(summaries))

#     #  Persist the current table list for next run
#     save_current_tables(current_tables)

#     print(f"{SCHEMA_OUT_FILE} regenerated. Table list updated in {PREV_TABLES_FILE}.")

# if __name__ == "__main__":
#     main()

# #!/usr/bin/env python3
# import os
# import json
# from sqlalchemy import text, create_engine, inspect
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

# client = OpenAI()

# PREV_TABLES_FILE = "db_tables.json"
# SCHEMA_OUT_FILE   = "db_schema.txt"

# def load_previous_tables():
#     if os.path.exists(PREV_TABLES_FILE):
#         with open(PREV_TABLES_FILE, "r") as f:
#             return json.load(f)
#     return []

# def save_current_tables(tables):
#     with open(PREV_TABLES_FILE, "w") as f:
#         json.dump(tables, f, indent=2)

# def main():
#     database_url = os.getenv("DATABASE_URL")
#     if not database_url or not os.getenv("OPENAI_API_KEY"):
#         print("Error: Set both DATABASE_URL and OPENAI_API_KEY environment variables.")
#         return

#     engine = create_engine(database_url)
#     inspector = inspect(engine)
#     current_tables = inspector.get_table_names()
#     previous_tables = load_previous_tables()

#     if set(current_tables) == set(previous_tables):
#         print("No schema change detected. Exiting without regeneration.")
#         return

#     print("Detected schema change. Regenerating db_schema.txt ...")

#     summaries = []
#     relationships = []  # Collect global FK relationships

#     for table in current_tables:
#         columns = inspector.get_columns(table)
#         fks = inspector.get_foreign_keys(table)

#         # Fetch sample rows
#         with engine.connect() as conn:
#             result = conn.execute(text(f"SELECT * FROM {table} LIMIT 3"))
#             sample_rows = [dict(row._mapping) for row in result]

#         # Build table schema with types
#         column_table = "| Column Name | Type | Description | Example Value |\n"
#         column_table += "|-------------|------|-------------|---------------|\n"
#         for col in columns:
#             name = col["name"]
#             col_type = str(col["type"])
#             example_val = sample_rows[0].get(name, "") if sample_rows else ""
#             column_table += f"| {name} | {col_type} |  | {example_val} |\n"

#         # Keys section
#         pk_cols = [c["name"] for c in columns if c.get("primary_key", False)]
#         fk_lines = []
#         for fk in fks:
#             col = fk["constrained_columns"][0]
#             ref_table = fk["referred_table"]
#             ref_col = fk["referred_columns"][0]
#             fk_lines.append(f"{table}.{col} → {ref_table}.{ref_col}")
#             relationships.append(f"{table}.{col} → {ref_table}.{ref_col}")

#         # Format schema block
#         schema_block = f"""
# ## Table name - {table}

# ### Columns

# {column_table}

# ### Keys
# - **Primary Keys:** {', '.join(pk_cols) if pk_cols else 'None'}
# - **Foreign Keys:** {', '.join(fk_lines) if fk_lines else 'None'}
# """
#         summaries.append(schema_block.strip())

#     # Append relationship summary
#     if relationships:
#         rel_section = "\n\n# Table Relationships\n\n"
#         rel_section += "\n".join([f"- {rel}" for rel in relationships])
#         summaries.append(rel_section)

#     # Write out schema
#     with open(SCHEMA_OUT_FILE, "w") as f:
#         f.write("\n\n".join(summaries))

#     save_current_tables(current_tables)
#     print(f"{SCHEMA_OUT_FILE} regenerated with relationships. Table list updated in {PREV_TABLES_FILE}.")

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
import os
import json
from sqlalchemy import text, create_engine, inspect
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Instantiate OpenAI client (uses OPENAI_API_KEY from env)
client = OpenAI()

# Files
PREV_TABLES_FILE = "db_tables.json"
SCHEMA_OUT_FILE  = "db_schema.txt"


def load_previous_tables():
    if os.path.exists(PREV_TABLES_FILE):
        with open(PREV_TABLES_FILE, "r") as f:
            return json.load(f)
    return []


def save_current_tables(tables):
    with open(PREV_TABLES_FILE, "w") as f:
        json.dump(tables, f, indent=2)


def main():
    # Env checks
    database_url = os.getenv("DATABASE_URL")
    if not database_url or not os.getenv("OPENAI_API_KEY"):
        print("Error: Set both DATABASE_URL and OPENAI_API_KEY environment variables.")
        return

    engine = create_engine(database_url)
    inspector = inspect(engine)
    current_tables = inspector.get_table_names()

    # Skip regeneration if no schema change
    previous_tables = load_previous_tables()
    if set(current_tables) == set(previous_tables):
        print("No schema change detected. Exiting.")
        return

    print("Detected schema change. Regenerating db_schema.txt ...")

    summaries = []
    for table in current_tables:
        # Columns & types
        columns = inspector.get_columns(table)
        column_details = [
            {"name": col["name"], "type": str(col["type"])} for col in columns
        ]

        # Sample rows
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table} LIMIT 3"))
            sample_rows = [dict(row._mapping) for row in result]

        # Keys
        pk = inspector.get_pk_constraint(table).get("constrained_columns", [])
        fks = [
            {
                "constrained": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk.get("referred_columns", [])
            }
            for fk in inspector.get_foreign_keys(table)
        ]

        # Metadata for GPT
        metadata = {
            "table": table,
            "columns": column_details,
            "sample_rows": sample_rows,
            "primary_keys": pk,
            "foreign_keys": fks
        }

        system_msg = {
            "role": "system",
            "content": (
                "You are a warehouse database expert.\n"
                "Generate a Markdown schema summary for this table with:\n"
                "1. Columns (Name, Type, Description, Example Value)\n"
                "2. Keys (Primary Keys, Foreign Keys)\n"
                "Descriptions must be short and meaningful.\n"
            )
        }
        user_msg = {"role": "user", "content": json.dumps(metadata, default=str)}

        # GPT call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[system_msg, user_msg]
        )
        table_summary = response.choices[0].message.content.strip()

        # Prepend table header
        header = f"## Table name - {table}\n\n"
        summaries.append(header + table_summary + "\n")

    # Write schema file
    with open(SCHEMA_OUT_FILE, "w") as f:
        f.write("\n".join(summaries))

    save_current_tables(current_tables)
    print(f"{SCHEMA_OUT_FILE} regenerated. Updated {PREV_TABLES_FILE}.")


if __name__ == "__main__":
    main()
