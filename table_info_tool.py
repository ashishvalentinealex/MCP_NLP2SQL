import os
from openai import OpenAI
from db_resource import WarehouseDB

client = OpenAI()

class TableInfoTool:
    """
    Given a table name, returns the chunk of db_schema.txt
    corresponding to that table (including header and markdown table).
    """
    def run(self, resource: WarehouseDB, table: str) -> str:
        schema_file = os.getenv("SCHEMA_FILE", "db_schema.txt")
        if not os.path.exists(schema_file):
            return f"Schema file not found at {schema_file}."

        with open(schema_file, "r", encoding="utf-8") as f:
            all_notes = f.read()

        # Split out sections by header marker
        sections = all_notes.split("## Table name - ")
        for sec in sections:
            if sec.startswith(table):
                return "## Table name - " + sec

        return f"No schema notes found for table '{table}'."
