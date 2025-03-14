# main.py
import os
import asyncio
import argparse
import logging
from dotenv import load_dotenv
from agents.hotel_booking_agent import HotelBookingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_required_env_vars():
    """Check for required API keys."""
    required_keys = ["GEMINI_API_KEY", "RAPIDAPI_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        logger.error(f"Missing required environment variables: {', '.join(missing_keys)}")
        logger.error("Please set these in your .env file")
        exit(1)

async def run_cli_mode():
    """Run the hotel booking agent in command-line interface mode."""
    agent = HotelBookingAgent(api_key=os.getenv("GEMINI_API_KEY"))
    
    print("Welcome to the Hotel Booking Assistant!")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("How can I help you with your hotel booking today?")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("Thank you for using the Hotel Booking Assistant. Goodbye!")
            break
        
        print("\nAssistant: ", end="")
        try:
            response = await agent.process_message(user_input)
            print(response)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            print(f"I'm sorry, I encountered an error: {str(e)}. Please try again.")

def run_api_mode():
    """Run the hotel booking agent as a FastAPI service."""
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    import uvicorn
    
    app = FastAPI(title="Hotel Booking API")
    agent = HotelBookingAgent(api_key=os.getenv("GEMINI_API_KEY"))
    
    @app.post("/chat")
    async def chat(request: Request):
        data = await request.json()
        user_message = data.get("message", "")
        
        if not user_message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message cannot be empty"}
            )
        
        try:
            response = await agent.process_message(user_message)
            return {"response": response}
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Error processing message: {str(e)}"}
            )
    
    # Add a health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    # Start the API server
    logger.info("Starting API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Hotel Booking Assistant")
    parser.add_argument("--api", action="store_true", help="Run as API service")
    args = parser.parse_args()
    
    # Check for required environment variables
    check_required_env_vars()
    
    if args.api:
        # Run in API mode
        logger.info("Running in API mode")
        run_api_mode()
    else:
        # Run in CLI mode
        logger.info("Running in CLI mode")
        asyncio.run(run_cli_mode())