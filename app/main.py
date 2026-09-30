from fastapi import FastAPI

from app.ingestion.api import router as ingestion_router
from app.storage.database import initialize_database

app = FastAPI(
    title="AgentSentry",
    description="AI Reliability Engineer for RAG applications",
    version ="0.1.0",
)

initialize_database()
app.include_router(ingestion_router)
