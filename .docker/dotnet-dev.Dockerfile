FROM mcr.microsoft.com/dotnet/sdk:8.0

RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser -m appuser

WORKDIR /workspace
COPY --chown=appuser:appuser orchestrator/ ./orchestrator/
COPY --chown=appuser:appuser tests/orchestrator/ ./tests/orchestrator/

USER appuser
