from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from tools.date_tool import DateTool
from tools.geo_location_tool import GeoLocationTool
from tools.hotel_search_tool import HotelSearchTool
from tools.hotel_booking_tool import HotelBookingTool
from tools.update_preference_tool import UpdatePreferenceTool
from models.hotel_models import UserPreferences
import logging

logger = logging.getLogger(__name__)

class HotelBookingAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.2
        )
        self.user_prefs = UserPreferences()
        self.tools = self._initialize_tools()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.agent_executor = self._create_agent()

    def _initialize_tools(self):
        return [
            DateTool(),
            GeoLocationTool(user_prefs=self.user_prefs),
            HotelSearchTool(user_prefs=self.user_prefs),
            HotelBookingTool(user_prefs=self.user_prefs),
            UpdatePreferenceTool(user_prefs=self.user_prefs)
        ]

    def _create_agent(self):
        prompt_template = PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad", "chat_history"],
            template="""
You are a hotel booking assistant. You have access to these tools: {tools}

Your task is to help the user book a hotel by gathering necessary information, updating the booking details using the update_preference_tool, and then using the hotel_search_tool to find available hotels.

Previous conversation:
{chat_history}

Use this format:

Thought: [your reasoning]

[If you need to use a tool:]
Action: [tool_name] (one of [{tool_names}])
Action Input: [input for the tool]
Observation: [result from the tool]

[Repeat thought/action/observation as needed]

[When you have a response for the user or need to ask a question:]
Final Answer: [your message to the user]

When you receive information from the user, use the update_preference_tool to store it. The update_preference_tool takes input in the format 'field=value', where field can be: city, check_in, nights, adults, rooms, latitude, longitude.

Example:
Question: I want to book a hotel in Paris.
Thought: I need to update the city to Paris and automatically fetch its coordinates.
Action: update_preference_tool
Action Input: city=Paris
Observation: Updated city to Paris
Thought: Now I need to get the latitude and longitude for Paris.
Action: geo_location_tool
Action Input: Paris
Observation: Latitude=48.8566, Longitude=2.3522
Action: update_preference_tool
Action Input: latitude=48.8566, longitude=2.3522
Observation: Updated coordinates for Paris
Thought: Now I need the check-in date.
Final Answer: What is your desired check-in date?

Guidelines:
- If you need information, ask the user with a Final Answer, but only for details not yet stored.
- When the user provides information, use update_preference_tool to save it before proceeding.
- Required details are: city, latitude, longitude, check_in, nights, adults, rooms. Use hotel_search_tool only when all are set.
- Use date_tool to get today’s date if needed (e.g., for relative dates like 'tomorrow').
- Do not use tools to ask questions; use Final Answer for that.
- Ask for one piece of information at a time unless the user provides multiple details.
- Check the chat history to avoid asking for information already provided.

Begin!
Question: {input}
{agent_scratchpad}
"""
        )
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt_template
        )
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    async def process_message(self, user_input: str) -> str:
        try:
            response = await self.agent_executor.ainvoke({"input": user_input})
            return response["output"]
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            return "Sorry, I encountered an error. Let's try that again."