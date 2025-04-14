# Deployment Guide

This guide provides instructions for deploying the X AI-Forum application in a production environment.

## Prerequisites

- A Linux server (Ubuntu 20.04+ recommended)
- Python 3.9+
- Nginx or Apache
- Domain name (optional, but recommended)
- SSL certificate (Let's Encrypt recommended)
- AWS account with Bedrock access
- Slack workspace with admin permissions

## Server Preparation

1. Update system packages:
   ```
   sudo apt update
   sudo apt upgrade -y
   ```

2. Install required system packages:
   ```
   sudo apt install -y python3-pip python3-venv nginx supervisor
   ```

3. Create a dedicated user for running the app (optional):
   ```
   sudo useradd -m -s /bin/bash xaiforum
   sudo su - xaiforum
   ```

## Application Deployment

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/x-ai-forum.git
   cd x-ai-forum
   ```

2. Set up the backend:
   ```
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Create and configure the `.env` file:
   ```
   cp .env.example .env
   nano .env
   ```
   
   Update with your specific configuration.

4. Initialize the vector database:
   ```
   python data_loader.py
   ```

5. Run the Slack setup helper:
   ```
   python setup_slack.py
   ```

6. Test the application:
   ```
   python test_integration.py
   ```

## Setting up Supervisor

Supervisor is used to keep your application running and restart it if it crashes.

1. Create a supervisor configuration file:
   ```
   sudo nano /etc/supervisor/conf.d/x-ai-forum.conf
   ```

2. Add the following configuration:
   ```
   [program:x-ai-forum]
   command=/home/xaiforum/x-ai-forum/backend/venv/bin/python app.py
   directory=/home/xaiforum/x-ai-forum/backend
   user=xaiforum
   autostart=true
   autorestart=true
   stopasgroup=true
   killasgroup=true
   stderr_logfile=/var/log/x-ai-forum/error.log
   stdout_logfile=/var/log/x-ai-forum/access.log
   ```

3. Create log directories:
   ```
   sudo mkdir -p /var/log/x-ai-forum
   sudo chown -R xaiforum:xaiforum /var/log/x-ai-forum
   ```

4. Reload supervisor:
   ```
   sudo supervisorctl reread
   sudo supervisorctl update
   ```

5. Check the status:
   ```
   sudo supervisorctl status x-ai-forum
   ```

## Setting up Nginx

Nginx will serve the frontend and proxy API requests to the Flask backend.

1. Create an Nginx configuration file:
   ```
   sudo nano /etc/nginx/sites-available/x-ai-forum
   ```

2. Add the following configuration:
   ```
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           root /path/to/x-ai-forum/frontend;
           index index.html;
           try_files $uri $uri/ /index.html;
       }

       location /api/ {
           proxy_pass http://localhost:8080/;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

3. Enable the site:
   ```
   sudo ln -s /etc/nginx/sites-available/x-ai-forum /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## SSL with Let's Encrypt (Optional but Recommended)

1. Install Certbot:
   ```
   sudo apt install -y certbot python3-certbot-nginx
   ```

2. Obtain and configure SSL certificate:
   ```
   sudo certbot --nginx -d your-domain.com
   ```

3. Configure auto-renewal:
   ```
   sudo systemctl status certbot.timer
   ```

## Frontend Deployment

1. Update the API URL in the frontend:
   ```
   cd /home/xaiforum/x-ai-forum/frontend
   nano app.js
   ```

   Change the API_URL to:
   ```javascript
   const API_URL = 'https://your-domain.com/api';  // Or http://your-domain.com/api if not using SSL
   ```

## Monitoring and Logs

- Check application logs:
  ```
  sudo tail -f /var/log/x-ai-forum/access.log
  sudo tail -f /var/log/x-ai-forum/error.log
  ```

- Check Nginx logs:
  ```
  sudo tail -f /var/log/nginx/access.log
  sudo tail -f /var/log/nginx/error.log
  ```

## Security Considerations

1. Set up a firewall:
   ```
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. Store sensitive environment variables securely.

3. Regularly update system packages and dependencies.

4. Consider using AWS Secrets Manager for AWS credentials.

## Scaling Considerations

For higher traffic scenarios:

1. Use a dedicated database (PostgreSQL) for forum data storage.

2. Deploy behind a load balancer if using multiple servers.

3. Use a dedicated AWS account for Bedrock API access.

4. Monitor API usage and costs.

## Backup Procedures

1. Backup the vector database regularly:
   ```
   tar -czvf vector_db_backup_$(date +%Y%m%d).tar.gz /home/xaiforum/x-ai-forum/backend/vector_db
   ```

2. Set up a cron job for automated backups.

3. Consider AWS S3 for backup storage.

## Troubleshooting

1. Application won't start:
   - Check supervisor logs
   - Verify environment variables
   - Check Python version

2. Slack integration not working:
   - Verify tokens in .env file
   - Check Slack app configuration
   - Run setup_slack.py again

3. AI not responding:
   - Check AWS credentials
   - Verify Bedrock model access
   - Check for API quotas or limits 