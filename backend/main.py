from dotenv import load_dotenv

# Load configuration before importing routes.  Route imports create the shared
# LLM service, whose OpenAI client needs OPENAI_API_KEY during initialization.
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rest.research import router as research_router
from rest.sources import router as sources_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research_router, prefix="/api")
app.include_router(sources_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Backend is running"}
