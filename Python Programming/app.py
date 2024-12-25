from fastapi import FastAPI, APIRouter, BackgroundTasks, Depends
from src.fastapi import user, blob
from src.utils.helperfunction import generate_random_number
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import yaml, uvicorn
from fastapi.responses import StreamingResponse
from datetime import datetime
import time
import ssl

config_file = yaml.safe_load(open("config/cloud_params.yaml","r"))
AccountName = config_file['BlobStorage']['AccountName']
AccountKey = config_file['BlobStorage']['AccountKey']
EndpointSuffix = config_file['BlobStorage']['EndpointSuffix']
ConnectionString = config_file['BlobStorage']['ConnectionString']

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('SSL/cert.pem', keyfile='SSL/key.pem')

def get_datetime_stream():
    while True:
        # Yield a timestamp in the format required for text/event-stream
        yield f"data: {datetime.now().isoformat()}\n\n"
        # This ensures a new event is sent every second
        time.sleep(1)

# Initialize FastAPI app
app = FastAPI()
# app.add_middleware(HTTPSRedirectMiddleware) # Enable Https

# Define a route for the home endpoint
@app.get("/")
async def home():
    while True:
        return {"status": "Working On API"}
    
@app.get("/stream")
async def stream_endpoint():
    return StreamingResponse(get_datetime_stream(), media_type="text/event-stream")

# Include routers for user and blob endpoints
app.include_router(user.router)
app.include_router(blob.router)

# Define a route for generating a random number
@app.post("/generate_random_number")
async def generate_random_number_endpoint(start_num: int, end_num: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_random_number, start_num, end_num)
    return {"message": "Number generation process has started"}

'''
if below code is enable use command - python app.py to run application
'''
# if __name__ == "__main__":
#     uvicorn.run(
#         "app:app",
#         ssl_certfile='SSL/cert.pem',  # Provide the path to your SSL certificate
#         ssl_keyfile='SSL/key.pem'      # Provide the path to your SSL private key
#     )