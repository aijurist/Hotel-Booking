# app.py
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
import dateparser

from services.hotel_service import HotelService
from services.geo_service import GeoService

# Load environment variables
load_dotenv()

class HotelBookingBot:
    """Hotel booking chatbot with memory and natural language processing."""
    
    def __init__(self):
        self.hotel_service = HotelService()
        self.geo_service = GeoService()
        self.context = {
            "location": None,
            "arrival_date": None,
            "departure_date": None,
            "adults": None,
            "rooms": None,
            "room_types": None,
            "coordinates": None,
            "search_performed": False
        }
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.2
        )
        
        # Define tools
        self.tools = self._setup_tools()
        
        # Setup memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create agent with tools and memory
        self.agent = self._setup_agent()
    
    def _setup_tools(self) -> List[Tool]:
        """Set up the tools for the agent."""
        return [
            Tool(
                name="search_hotels",
                description="""
                Search for hotels using location and booking details.
                Required parameters:
                - location: city or place name
                - arrival_date: in format YYYY-MM-DD
                - departure_date: in format YYYY-MM-DD
                - adults: number of adults
                - rooms: number of rooms
                """,
                func=self._search_hotels_tool
            ),
            Tool(
                name="book_hotel",
                description="""
                Book a hotel from the search results.
                Required parameters:
                - hotel_name: exact name or part of the hotel name
                Use this only after search_hotels has been called.
                """,
                func=self._book_hotel_tool
            ),
            Tool(
                name="parse_date",
                description="""
                Convert a natural language date reference to YYYY-MM-DD format.
                Input should be a string like "tomorrow", "next week", "December 15", etc.
                """,
                func=self._parse_date_tool
            ),
            Tool(
                name="get_current_date",
                description="Get today's date in YYYY-MM-DD format.",
                func=self._get_current_date_tool
            )
        ]
    
    def _setup_agent(self) -> AgentExecutor:
        """Set up the agent with tools and memory."""
        # Define the system prompt
        system_prompt = """You are a helpful hotel booking assistant. 
        Your job is to help users find and book hotels for their trips.
        
        Follow these guidelines:
        1. Ask for missing information: location, check-in date, check-out date, number of adults, and number of rooms.
        2. Parse dates from natural language (like "tomorrow", "next weekend", etc.).
        3. Search for hotels once you have all the necessary information.
        4. Help the user select a hotel from the search results.
        5. Create a booking once the user has made a selection.
        6. Be conversational but efficient - don't repeat questions if you already have the information.
        7. Be polite and helpful throughout the process.
        
        ONLY use the tools provided to you. Don't make up information about hotels.
        """
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create the agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _get_current_date_tool(self) -> str:
        """Get the current date in YYYY-MM-DD format."""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _parse_date_tool(self, date_string: str) -> str:
        """Parse natural language date references."""
        parsed_date = dateparser.parse(
            date_string,
            settings={'RELATIVE_BASE': datetime.now(), 'DATE_ORDER': 'YMD'}
        )
        if parsed_date:
            return parsed_date.strftime("%Y-%m-%d")
        return "Could not parse the date. Please provide a date in YYYY-MM-DD format."
    
    def _search_hotels_tool(self, 
                           location: str = None, 
                           arrival_date: str = None, 
                           departure_date: str = None, 
                           adults: int = None, 
                           rooms: int = None) -> str:
        """Search for hotels using the HotelService."""
        # Update context with provided parameters
        if location:
            self.context["location"] = location
        if arrival_date:
            self.context["arrival_date"] = arrival_date
        if departure_date:
            self.context["departure_date"] = departure_date
        if adults:
            self.context["adults"] = int(adults)
        if rooms:
            self.context["rooms"] = int(rooms)
        
        # Check if we have all necessary parameters
        required_params = ["location", "arrival_date", "departure_date", "adults", "rooms"]
        missing_params = [param for param in required_params if not self.context.get(param)]
        
        if missing_params:
            return f"Missing required parameters: {', '.join(missing_params)}"
        
        # Get coordinates for the location
        if not self.context.get("coordinates"):
            coordinates = self.geo_service.get_coordinates(self.context["location"])
            if not coordinates:
                return f"Could not find coordinates for location: {self.context['location']}"
            self.context["coordinates"] = coordinates
        
        # Search for hotels
        hotels = self.hotel_service.search_hotels(
            latitude=self.context["coordinates"][0],
            longitude=self.context["coordinates"][1],
            arrival_date=self.context["arrival_date"],
            departure_date=self.context["departure_date"],
            adults=self.context["adults"],
            room_qty=self.context["rooms"]
        )
        
        if not hotels:
            return "No hotels found matching your criteria."
        
        self.context["search_performed"] = True
        return self.hotel_service.format_search_results_for_display()
    
    def _book_hotel_tool(self, hotel_name: str) -> str:
        """Book a hotel from the search results."""
        if not self.context.get("search_performed"):
            return "Please search for hotels before trying to book."
        
        return self.hotel_service.book_hotel(hotel_name, self.context)
    
    def chat(self, user_input: str) -> str:
        """Process a user message and return the response."""
        response = self.agent.invoke({"input": user_input})
        return response["output"]

if __name__ == "__main__":
    bot = HotelBookingBot()
    
    print("Welcome to Hotel Booking Assistant! How can I help you with your hotel booking today?")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Thank you for using our hotel booking service. Goodbye!")
            break
            
        response = bot.chat(user_input)
        print(f"Bot: {response}")