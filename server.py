#!/usr/bin/env python3
import os
from mcp.server.fastmcp import FastMCP
from db_resource import WarehouseDB
from nlp2sql_tool import NLP2SQLTool
from table_info_tool import TableInfoTool

# Read configuration
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("Please set DATABASE_URL to your Postgres DSN")

# Create FastMCP with stateless JSON on /jsonrpc
mcp = FastMCP(
    name="WarehouseMCP",
    stateless_http=True,            # no session dance
    json_response=True,             # pure JSON responses
    streamable_http_path="/jsonrpc" # mount point
)
db = WarehouseDB(db_url)

#  Register resources 
@mcp.resource("warehouse://tables")
def list_tables() -> list[str]:
    return db.list_tables()

@mcp.resource("warehouse://{table}/columns")
def get_columns(table: str) -> list[dict]:
    return db.get_columns(table)

@mcp.resource("warehouse://{table}/sample")
def get_sample_data(table: str) -> list[dict]:
    return db.get_sample_data(table, limit=3)

#  Register tools
@mcp.tool()
def nlp2sql(user_query: str) -> list[dict]:
    return NLP2SQLTool().run(db, user_query)

@mcp.tool()
def table_info(table: str) -> str:
    return TableInfoTool().run(db, table)

#  Start Uvicorn serving the ASGI app
if __name__ == "__main__":
    import uvicorn
    app = mcp.streamable_http_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
