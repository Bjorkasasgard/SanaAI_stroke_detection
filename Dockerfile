FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for caching
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the rest of the backend files
COPY backend/ backend/

# Set working directory to backend
WORKDIR /app/backend

# Train the models during the Docker build process
# (This avoids needing to push large .pkl files to Git)
RUN python train_model.py

# Expose the port FastAPI will run on
EXPOSE 7860

# Command to run both the FastAPI server and the Telegram bot
CMD uvicorn main:app --host 0.0.0.0 --port 7860
