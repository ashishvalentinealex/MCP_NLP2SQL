import os
import json
from openai import OpenAI
from sqlalchemy import text
from db_resource import WarehouseDB
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

class NLP2SQLTool:
    """
    Tool that translates natural-language queries into SQL using GPT-4o
    and executes them against the WarehouseDB. Adds debug output for the generated SQL.
    """
    def __init__(self):
        # Load the pre-generated schema context
        schema_path = os.getenv("SCHEMA_FILE", "db_schema.txt")
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema_notes = f.read()

    def run(self, resource: WarehouseDB, user_query: str) -> list[dict]:
        # Build messages for function calling
        system_msg = {
            "role": "system",
            "content": (
                "You are an expert SQL generator. "
                "Use the given database schema to produce a single SQL SELECT query. "
                "Respond only with a JSON object containing a single field 'sql'. "
                "Do not include any explanations.\n\n"
                f"Schema:\n{self.schema_notes}"
            )
        }
        user_msg = {"role": "user", "content": user_query}

        # Call GPT-4o with function-calling to get structured SQL
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[system_msg, user_msg],
            functions=[{
                "name": "generate_sql",
                "description": "Generate a single SELECT SQL statement",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string", "description": "The SQL query to execute"}
                    },
                    "required": ["sql"]
                }
            }],
            function_call={"name": "generate_sql"}
        )

        # Extract SQL from the function call
        call = response.choices[0].message.function_call
        args = json.loads(call.arguments)
        sql = args.get("sql", "")

        # DEBUG: print the SQL before execution
        print(f"DEBUG – executing SQL: {sql}")

        # Execute the SQL and return the results
        rows = resource.query(sql)
        return rows

