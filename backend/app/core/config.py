from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AgentOps Runtime"
    app_env: str = "dev"
    api_v1_prefix: str = "/api/v1"

    postgres_dsn: str = "postgresql+asyncpg://agentops:agentops@postgres:5432/agentops"
    redis_url: str = "redis://redis:6379/0"
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "medical_docs"
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "replace-me"

    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = "changeme"
    llm_model: str = "gpt-4o-mini"
    prompt_version: str = "v1"

    azure_openai_enabled: bool = False
    azure_openai_endpoint: str = "https://example.openai.azure.com"
    azure_openai_api_key: str = "changeme"
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment: str = "gpt-4o-mini"

    otel_service_name: str = "agentops-runtime"
    otel_exporter_otlp_endpoint: str = "http://jaeger:4318"


settings = Settings()
