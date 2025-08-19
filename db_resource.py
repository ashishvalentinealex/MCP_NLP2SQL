from sqlalchemy import create_engine, inspect, text

class WarehouseDB:
    """
    Wraps a PostgreSQL warehouse_management database.
    Provides methods to list tables, get column metadata, run arbitrary SQL,
    and fetch sample rows for inspection.
    """
    def __init__(self, url: str):
        # e.g., url="postgresql://user:pass@host:port/warehouse_management"
        self.engine = create_engine(url)
        self.inspector = inspect(self.engine)

    def list_tables(self) -> list[str]:
        """Return a list of all table names in the database."""
        return self.inspector.get_table_names()

    def get_columns(self, table: str) -> list[dict]:
        """Return column metadata for the given table as a list of dicts with name and type."""
        cols = self.inspector.get_columns(table)
        return [{"name": c['name'], "type": str(c['type'])} for c in cols]

    def query(self, sql: str) -> list[dict]:
        """Execute an arbitrary SQL statement and return the results as a list of dicts."""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            return [dict(row._mapping) for row in result]

    def get_sample_data(self, table: str, limit: int = 3) -> list[dict]:
        """Fetch up to `limit` rows from the specified table for sampling."""
        sql = f"SELECT * FROM {table} LIMIT {limit}"
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            return [dict(row._mapping) for row in result]
