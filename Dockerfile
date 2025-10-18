FROM python:3.13.9-alpine3.21 as runner

WORKDIR /app

ARG GEMINI_API_KEY
ARG API_BACKEND_URL
ENV GEMINI_API_KEY=${GEMINI_API_KEY}\
    API_BACKEND_URL=${API_BACKEND_URL}

EXPOSE 8501

COPY requirements.txt .

RUN RUN wget -qO- https://astral.sh/uv/install.sh | sh &&\
    uv pip install -r requirements.txt

COPY . .

RUN addgroup --system appgroup &&\
    adduser --system --ingroup appgroup appuser &&\
    chown -R appuser:appgroup /app

USER appgroup

ENTRYPOINT ["streamlit run"]




