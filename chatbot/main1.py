from agents.hotel_booking_agent import HotelBookingAgent
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

async def main():
    agent = HotelBookingAgent(api_key=os.getenv('GEMINI_API_KEY'))
    await agent.process_message("I need a hotel in Paris")

# Run the async function
asyncio.run(main())
