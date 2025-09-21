import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import sys
import os

# Add parent directory to path to import modules from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import support bot components
from UserRequest import UserRequest
from UserResponse import UserResponse
from memory.MemoryProvider import MemoryProvider
from pinecone_db.PineconeDbRepository import PineconeDbRepository
from SupportRequestHandler import SupportRequestHandler

# Load environment variables from .env file
load_dotenv()

# Check if required environment variables are present
required_env_vars = ['PINECONE_API_KEY', 'OPENAI_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"WARNING: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please create a .env file with these variables or set them in your environment.")
    print("See .env.example for the required variables.")

# Create FastAPI app
app = FastAPI(title="Running Dinner Support Bot Local API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize components
vector_db_repository = PineconeDbRepository()
memory_provider = MemoryProvider()
support_request_handler = SupportRequestHandler(
    memory_provider=memory_provider, 
    vector_db_repository=vector_db_repository
)

@app.post("/api/support")
async def handle_support_request(request: Request):
    """
    Handle support requests just like the Lambda function would.
    Accepts a JSON body with:
    - question: The user's question
    - request_params: Optional parameters for the request
    - thread_id: Optional thread ID for conversation history
    """
    try:
        # Get the request body as a dict
        body = await request.json()
        
        # Create a UserRequest object
        user_request = UserRequest(**body)
        
        # Process the request using the same handler as the Lambda
        lambda_response = support_request_handler.process_user_request(user_request)
        
        # Extract the body from the Lambda response and return it directly
        # FastAPI will automatically handle the JSON serialization
        return json.loads(lambda_response["body"])
    except Exception as e:
        # Handle errors - extract error message from the response
        error_response = support_request_handler.process_error(e)
        return json.loads(error_response["body"])

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok"}

def start_server(host="localhost", port=8000):
    """Start the FastAPI server"""
    try:
        uvicorn.run(app, host=host, port=port)
    except ImportError as e:
        print(f"ERROR: {str(e)}")
        print("\nMake sure you have installed the development dependencies:")
        print("  pip install -r requirements-dev.txt")
        sys.exit(1)

if __name__ == "__main__":
    print(f"Starting local API server for Running Dinner Support Bot")
    print(f"API will be available at http://localhost:8000/api/support")
    print(f"Health check endpoint: http://localhost:8000/health")
    print(f"Press Ctrl+C to stop the server")
    start_server()
