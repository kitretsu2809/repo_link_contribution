# RepoRadar Deployment Guide

This document provides step-by-step instructions to deploy RepoRadar (React frontend + Django backend) to AWS using a free-tier friendly architecture.

---

## 🚀 Step-by-Step Deployment Instructions

### Phase 1: Host and Network Setup (AWS EC2)

1. **Launch EC2 Instance:**
   - Launch an Ubuntu-based EC2 instance (e.g. `t2.micro` or `t3.small`).
   - Assign an **Elastic IP** to your EC2 instance so that the IP address does not change when the instance is restarted.

2. **Configure Security Group Inbound Rules:**
   Go to your EC2 Security Group and ensure the following ports are open to **Anywhere (`0.0.0.0/0`)**:
   - **Port 80 (HTTP)** — *Required for ZeroSSL validation.*
   - **Port 443 (HTTPS)** — *Required to serve the secure API.*
   - **Port 22 (SSH)** — *Required for administrative access.*

---

### Phase 2: Backend Deployment (EC2 Containerization)

1. **Install Docker and Git on EC2:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose git
   ```

2. **Clone the Repository:**
   ```bash
   git clone <YOUR_GIT_REPO_URL>
   cd repo_link_contribution
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```bash
   nano .env
   ```
   Add your keys and configuration:
   ```env
   # Database Configuration
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=postgres_password
   DB_HOST=db
   DB_PORT=5432

   # API Keys
   GEMINI_API_KEY=your_gemini_api_key
   GROQ_API_KEY=your_groq_api_key

   # Django Settings
   APP_BASE_URL=https://main.d25lyjl7b5u7se.amplifyapp.com
   ```

4. **Launch Backend Services:**
   ```bash
   docker compose up -d
   ```

5. **Run Django Migrations:**
   ```bash
   docker compose exec web python manage.py migrate
   ```

6. **Trigger the GitHub Repository Crawler:**
   To populate the dashboard with repository data, trigger a manual crawl:
   ```bash
   docker compose exec web python trigger_crawler.py
   ```

---

### Phase 3: Frontend Deployment (AWS Amplify)

1. **Host App on Amplify:**
   - Go to the **AWS Amplify** console.
   - Connect your GitHub repository and select the branch (e.g. `main`).
   - If prompted for Monorepo settings, set the App Root directory to `frontend`.

2. **Configure Build Settings:**
   Amplify will automatically detect the `amplify.yml` file in your repository. It will automatically build the React project using the correct secure API URL (`https://<your-elastic-ip>.sslip.io/api`).

3. **Verify:**
   - Wait for the Amplify build to complete.
   - Open your site in an **Incognito Window** to verify that everything works and that the API is loaded over HTTPS.
