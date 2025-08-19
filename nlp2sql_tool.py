import os
import json
from openai import OpenAI
from db_resource import WarehouseDB

client = OpenAI()

class NLP2SQLTool:
    """
    Translates a natural-language query into SQL using GPT-4o,
    then executes it against the WarehouseDB resource.
    """
    def __init__(self):
        schema_path = os.getenv("SCHEMA_FILE", "db_schema.txt")
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema_notes = f.read()

    def run(self, resource: WarehouseDB, user_query: str):
        system_msg = {
            "role": "system",
            "content": (
                "You are a warehouse data expert. Use the schema below when crafting SQL:\n\n"
                f"{self.schema_notes}"
            )
        }
        user_msg = {"role": "user", "content": user_query}

        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[system_msg, user_msg]
        )
        sql = resp.choices[0].message.content.strip()
        return resource.query(sql)



          
