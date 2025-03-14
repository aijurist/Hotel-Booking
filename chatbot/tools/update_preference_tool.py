from langchain.tools import BaseTool
from models.hotel_models import UserPreferences
from typing import Optional
from pydantic import Field

class UpdatePreferenceTool(BaseTool):
    name: str = "update_preference_tool"
    description: str = "Updates a booking preference. Input should be in the format 'field=value', e.g., 'city=Paris', 'check_in=2025-03-16', 'nights=5'."
    user_prefs: UserPreferences = Field(default_factory=UserPreferences, exclude=True)
    
    def _run(self, query: str) -> str:
        try:
            if "," in query:
                updates = query.split(",")
                results = []
                for update in updates:
                    update = update.strip()
                    if "=" in update:
                        field, value = [x.strip() for x in update.split("=", 1)]
                        results.append(self.user_prefs.update(field, value))
                    else:
                        results.append(f"Invalid format for '{update}'. Use field=value format.")
                return "\n".join(results)
            
            if "=" not in query:
                return "Invalid format. Use field=value format (e.g., 'city=Paris')."
                
            field, value = [x.strip() for x in query.split("=", 1)]
            result = self.user_prefs.update(field, value)
            return result
            
        except Exception as e:
            return f"Error updating preference: {str(e)}"
    
    def get_user_preferences(self) -> dict:
        return self.user_prefs.dict()
