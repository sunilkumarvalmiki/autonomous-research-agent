# Deployment Guide

## Deployment Options

The Autonomous Research Agent can be deployed in several ways:

1. **Local Development** - Run on your local machine
2. **Docker Container** - Containerized deployment
3. **Cloud Deployment** - Deploy to cloud platforms
4. **API Server** - Run as a REST API service

## 1. Local Development

### Prerequisites
- Python 3.8+
- Ollama (for local models)
- 8GB+ RAM (16GB+ recommended)

### Installation
```bash
git clone https://github.com/sunilkumarvalmiki/autonomous-research-agent.git
cd autonomous-research-agent
pip install -r requirements.txt
pip install -e .
```

### Running Examples
```bash
# Simple research
python examples/simple_research.py

# With RAG
python examples/rag_example.py

# Multi-step research
python examples/multi_step_research.py
```

## 2. Docker Deployment

### Build Docker Image
```bash
docker build -t autonomous-agent:latest .
```

### Run Container
```bash
# Run API server
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  autonomous-agent:latest

# Run CLI
docker run -it autonomous-agent:latest \
  python -m autonomous_agent.cli research "What is machine learning?"
```

### Docker Compose
```bash
docker-compose up -d
```

## 3. API Server Deployment

### Run Locally
```bash
# Start the API server
python -m autonomous_agent.api

# Or with uvicorn
uvicorn autonomous_agent.api:app --host 0.0.0.0 --port 8000
```

### API Endpoints

**Research**
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?", "use_rag": true}'
```

**Multi-Step Research**
```bash
curl -X POST http://localhost:8000/research/multi-step \
  -H "Content-Type: application/json" \
  -d '{"query": "How to build an AI system?", "max_steps": 3}'
```

**Add Knowledge**
```bash
curl -X POST http://localhost:8000/knowledge \
  -H "Content-Type: application/json" \
  -d '{"content": "AI is artificial intelligence..."}'
```

**Get Statistics**
```bash
curl http://localhost:8000/statistics
```

**API Documentation**
Visit `http://localhost:8000/docs` for interactive API documentation.

## 4. CLI Usage

### Basic Research
```bash
# Simple query
autonomous-agent research "What are neural networks?"

# With specific model
autonomous-agent research "Write Python code for sorting" --model llama

# With RAG
autonomous-agent research "Explain quantum computing" --use-rag

# Multi-step research
autonomous-agent research "How to deploy ML models?" --multi-step --steps 4
```

### Knowledge Management
```bash
# Add knowledge from file
autonomous-agent add-knowledge knowledge.txt --chunk

# Add with metadata
autonomous-agent add-knowledge paper.pdf --metadata '{"source": "research_paper"}'
```

### Configuration
```bash
# Create default config
autonomous-agent config --init

# Show current config
autonomous-agent config --show

# Use custom config
autonomous-agent research "Query" --config my-config.json
```

### Statistics
```bash
autonomous-agent stats
```

## 5. Cloud Deployment

### AWS Deployment (EC2)

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.large or larger
   - Storage: 50GB+

2. **Setup**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip git

# Clone and install
git clone https://github.com/sunilkumarvalmiki/autonomous-research-agent.git
cd autonomous-research-agent
pip install -r requirements.txt

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b

# Run API server
nohup python -m autonomous_agent.api &
```

3. **Configure Security Group**
   - Allow inbound traffic on port 8000
   - Restrict to specific IPs if needed

### Google Cloud Platform (GCP)

1. **Create VM Instance**
```bash
gcloud compute instances create agent-vm \
  --machine-type=n1-standard-4 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB
```

2. **SSH and Setup**
```bash
gcloud compute ssh agent-vm
# Follow same setup as AWS
```

### Azure Deployment

1. **Create VM**
```bash
az vm create \
  --resource-group myResourceGroup \
  --name agent-vm \
  --image Ubuntu2204 \
  --size Standard_D4s_v3
```

2. **SSH and Setup**
```bash
az vm ssh agent-vm
# Follow same setup as AWS
```

## 6. Production Deployment Best Practices

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
AGENT_LOG_LEVEL=INFO
AGENT_DATA_DIR=/app/data
AGENT_FEEDBACK_DIR=/app/data/feedback
OLLAMA_HOST=http://localhost:11434
EOF
```

### Process Management with systemd

Create `/etc/systemd/system/autonomous-agent.service`:
```ini
[Unit]
Description=Autonomous Research Agent API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/autonomous-research-agent
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 -m autonomous_agent.api
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable autonomous-agent
sudo systemctl start autonomous-agent
sudo systemctl status autonomous-agent
```

### Nginx Reverse Proxy

Install and configure Nginx:
```bash
sudo apt install nginx

# Create config
sudo nano /etc/nginx/sites-available/autonomous-agent
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/autonomous-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 7. Monitoring and Logging

### Logging Configuration
```python
# In your deployment script
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/autonomous-agent.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks
```bash
# Add to cron for periodic health checks
*/5 * * * * curl -f http://localhost:8000/health || systemctl restart autonomous-agent
```

### Monitoring with Prometheus (Optional)
Add metrics endpoint to API and configure Prometheus scraping.

## 8. Scaling Considerations

### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Deploy multiple API instances
- Share knowledge base via network storage

### Vertical Scaling
- Increase VM resources
- Use GPU instances for larger models
- Optimize model quantization

### Caching
- Cache frequent queries
- Use Redis for distributed caching

## 9. Security

### API Authentication
Add authentication to API:
```python
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if api_key != "your-secret-key":
        raise HTTPException(status_code=403)
```

### Rate Limiting
```bash
pip install slowapi
```

### HTTPS
Always use HTTPS in production (Let's Encrypt)

## 10. Backup and Recovery

### Backup Knowledge Base
```bash
# Backup vector database
tar -czf backup-$(date +%Y%m%d).tar.gz data/vector_db

# Backup feedback
tar -czf feedback-$(date +%Y%m%d).tar.gz data/feedback
```

### Automated Backups
```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

## Troubleshooting

### Common Issues

1. **Out of Memory**
   - Use smaller models (phi3)
   - Increase swap space
   - Use quantized models

2. **Slow Response**
   - Use faster models (mistral)
   - Reduce max_tokens
   - Enable caching

3. **Connection Refused**
   - Check if Ollama is running
   - Verify firewall settings
   - Check port availability

### Logs
```bash
# System logs
journalctl -u autonomous-agent -f

# Application logs
tail -f /var/log/autonomous-agent.log

# Nginx logs
tail -f /var/log/nginx/access.log
```

## Support

For deployment issues:
- GitHub Issues: https://github.com/sunilkumarvalmiki/autonomous-research-agent/issues
- Documentation: Check README.md and GETTING_STARTED.md
