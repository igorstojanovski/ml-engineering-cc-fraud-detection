# ml-engineering-cc-fraud-detection
A repository for the PA2595 Machine Learning Engineering BTH Course

## Running locally with Docker Compose

This project uses `docker-compose` to serve the production-ready frontend through Nginx, with proxying of `/api/*` requests to a locally running ML model.

-  ⚠️ The `model` service is not included in this setup yet.  
- For now, make sure your ML API is running on your host machine at `localhost:5001`.  
- In the future, this will be replaced with a dedicated `model` service.

To run the frontend + proxy setup locally:

```bash
docker compose up --build
```

then open your browser at http://localhost:3000