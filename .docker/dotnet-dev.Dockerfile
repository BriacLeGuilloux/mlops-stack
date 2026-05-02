FROM mcr.microsoft.com/dotnet/sdk:8.0

RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser -m appuser

USER appuser
