from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""  # set in .env if you want GPT-4
    OPENAI_MODEL: str = "gpt-4"
    FAISS_INDEX_PATH: str = "./data/faiss.index"
    EMBED_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    MAX_CHUNK_TOKENS: int = 400
    CHUNK_OVERLAP_TOKENS: int = 50
    TOP_K: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
