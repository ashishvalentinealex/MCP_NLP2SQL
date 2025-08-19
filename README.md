![Architecture Overview](https://cdn.hashnode.com/res/hashnode/image/upload/v1746992148580/1aa31433-dc65-43cb-8eaf-1335c35a0f52.png)

# Model context protocol for interacting with database using Natural Language processing 
This project provides an **MCP (Model Context Protocol) server** that connects to a PostgreSQL  database, auto-documents the schema, and enables **natural language → SQL** querying with minimal hallucination by using strict schema validation.

# README for MCP Server

This MCP server uses **FastMCP**, **SQLAlchemy**, and **OpenAI models** to:
- Inspect and document your PostgreSQL schema.
- Expose schema resources (tables, columns, samples) via MCP.
- Translate natural language queries into safe, validated SQL.

## Requirements

1. **PostgreSQL 12+**
2. **Python 3.10+**
3. **Conda or venv** for environment setup

## Dependencies (requirements.txt):
```
fastmcp
sqlalchemy
psycopg2-binary
openai
uvicorn
```

## Setup Instructions

1. **Clone repository**
```bash
git clone https://github.com/<your-org>/MCP_NLP2SQL.git
cd nlp2sql-mcp
```

# Environment Setup

To create and activate the **conda** environment for this project:

``` bash
# Create the environment
conda create -n env python=3.10 -y
```

# Activate the environment
``` bash 
conda activate env
```

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/db"
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"


# Usage Instructions

Run the following commands to set up and use the MCP server:

```bash
# Generate schema documentation
python generate_schema.py
# Start MCP server
python server.py
```

## MCP Resources

warehouse://tables → List all tables

warehouse://{table}/columns → Show column details

warehouse://{table}/sample → First 3 rows of a table

## MCP Tools

Use JSON-RPC requests to call tools:

## nlp2sql
```bash 
{
  "method": "tools/call",
  "params": {
    "name": "nlp2sql",
    "arguments": { "user_query": "Show all products with quantity > 50" }
  }
}
```

## table_info
```bash 
{
  "method": "tools/call",
  "params": {
    "name": "table_info",
    "arguments": { "table": "products" }
  }
}
```
## Example Workflow
python generate_schema.py
python server.py


## Then query in natural language:
```bash 
{
  "method": "tools/call",
  "params": {
    "name": "nlp2sql",
    "arguments": { "user_query": "List all suppliers and their contact emails" }
  }
}
```

The SQL is generated, validated, and executed safely.

## Key Parameters

ALLOW_WRITE_SQL=false → Keeps queries read-only (default)

MAX_ROWS=1000 → Caps query result size

SQL_TIMEOUT_SECONDS=30 → Query timeout


## if in doubt feel free to reach out to me at my email ashishvalentinealex@gmail.com  
