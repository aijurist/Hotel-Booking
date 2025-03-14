from langchain.tools import BaseTool
from datetime import datetime

class DateTool(BaseTool):
    name: str = "date_tool"
    description: str = "Returns today's date in YYYY-MM-DD format. No input required."

    def _run(self, query: str = None) -> str:
        """Returns today's date in YYYY-MM-DD format."""
        return datetime.today().strftime('%Y-%m-%d')