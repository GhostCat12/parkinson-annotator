# Running Parkinson's Annotator with Docker

This document explains how to run the **Parkinson's Annotator** application using Docker and Docker Compose.

The Docker setup runs the Flask app in a container, with the runtime data (database, uploads, logs) written to an 
instance directory inside the container. This directory is mounted as a volume to the host machine to ensure data is 
not lost when the container is stopped or rebuilt.

## Requirements
- Docker (Engine)
- Docker Compose

Both Docker and Docker Compose are included in the official [Docker Desktop](https://docs.docker.com/desktop/) 
installation.  

Verify installation using `docker --version` and `docker compose version`.

## Repository setup
Clone the parkinson-annotator repository:
```bash
git clone https://github.com/JellyEllie/parkinson-annotator.git
```
Change directory to the root of the repository to continue installation:
```bash
cd parkinson-annotator
```

## Set environment variables
Modify the .env file to set the environment variables:
- Rename .env.example to .env  
    `cp .env.example .env`
- Open the file (note that files beginning with `.` are hidden by default on most systems)
- Enter your own email under ENTREZ_EMAIL for NCBI Entrez API access
    ```
  ENTREZ_EMAIL=name@example.com
  ```
- Save the file before contiuing with installation

## Build and run the Docker image

### Build using Docker Compose
From the repository root directory:
```bash
docker compose up --build
```
This will:
- Build the Docker image
- Start the Flask app inside a container
- Create the database if it does not exist
- Load any initial data from CSVs/VCFs found in src/instance/uploads/  
  (Usually applies if the database has been built and files uploaded previously.  
New files can be uploaded once the 
container is running via the web interface.)
- Expose the Flask app on port 8000

### Access the application
When running in Docker, the application does not auto-open the browser. Open the browser manually and access the 
application at http://localhost:8000/.

### Running the application again
After the first build using `docker compose up --build` and stopping the container with `docker compose down`, the 
Docker image parkinsons-annotator will remain.  
To start the application again using the existing image:
```bash
docker compose up
```

## Stopping the container
In a separate terminal to the running container, navigate to the directory the container is running in, and stop the 
container using:
```bash
docker compose down
```


## Persistent Data
The following directories are mounted as Docker volumes:  

| Host Directory | Container Directory | Description                      |
| -------------- | ------------------- |----------------------------------|
| ./src/instance/ | /app/instance/ | SQLite database and user uploads |
| ./src/logs | /app/logs | Application logs                 |  

This ensures that data is persisted across container restarts, and that logs are accessible after the container is 
stopped.

## Rebuilding the image
To fully rebuild the image:
```bash
docker compose down
docker compose build --no-cache
docker compose up
```
## Troubleshooting
#### App runs but browser does not connect
Check the port the Flask app is exposed on (localhost 8000). Either ensure the browser is directing to this address, 
or change the compose.yml to expose the app on a different available port.

#### Docker Compose fails to build the image
- Ensure Docker is running
- Retry with:
    ```bash
    docker compose build --no-cache
    ```

#### Database does not persist across container restarts
Confirm the volume mount in `compose.yml`:
```yaml
- ./src/instance/:/app/instance/
```
Ensure the src/instance/ directory exists on host.
