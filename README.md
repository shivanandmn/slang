# Slang - LiveKit Multi-Agent Storyteller

A multi-agent LiveKit application that creates personalized interactive stories using voice interaction. The application features two agents: an IntroAgent that gathers user information and a StoryAgent that creates personalized stories.

## Features

- **Multi-Agent Architecture**: Seamless handoff between introduction and storytelling agents
- **Voice Interaction**: Real-time voice communication using LiveKit
- **Personalized Stories**: Stories tailored to user's name and location
- **AI-Powered**: Uses OpenAI GPT-4o-mini for conversation and story generation
- **Speech Services**: Deepgram for STT, OpenAI for TTS, Silero for VAD

## Architecture

### Agents
- **IntroAgent**: Gathers user information (name, location) for personalization
- **StoryAgent**: Creates and tells interactive personalized stories

### Services Used
- **LiveKit**: Real-time communication platform
- **OpenAI**: LLM and TTS services
- **Deepgram**: Speech-to-text conversion
- **Silero**: Voice activity detection

## Local Development

### Prerequisites
- Python 3.11+
- LiveKit account and API credentials
- OpenAI API key
- Deepgram API key
- ElevenLabs API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd slang
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and configuration
   ```

   Required environment variables:
   ```bash
   LIVEKIT_URL=wss://your-instance.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   OPENAI_API_KEY=sk-proj-your_openai_key
   DEEPGRAM_API_KEY=your_deepgram_key
   ELEVEN_API_KEY=sk_your_elevenlabs_key
   ```

### Local Deployment & Testing

#### Method 1: Direct Python Execution
```bash
# Activate virtual environment
source venv/bin/activate

# Run the agent
python multi_agent.py
```

#### Method 2: Docker Local Testing
```bash
# Build Docker image locally
docker build -t slang-agent .

# Run with environment file
docker run --env-file .env -p 8080:8080 slang-agent

# Or run with individual environment variables
docker run -e LIVEKIT_URL="wss://your-instance.livekit.cloud" \
           -e LIVEKIT_API_KEY="your_key" \
           -e LIVEKIT_API_SECRET="your_secret" \
           -e OPENAI_API_KEY="your_openai_key" \
           -e DEEPGRAM_API_KEY="your_deepgram_key" \
           -e ELEVEN_API_KEY="your_eleven_key" \
           -p 8080:8080 slang-agent
```

### Testing the Agent

#### 1. **LiveKit Dashboard Testing**
1. Go to your LiveKit Cloud dashboard
2. Navigate to "Rooms" section
3. Create a new room or join existing room
4. The agent should automatically connect when a participant joins

#### 2. **Web Client Testing**
Create a simple HTML test client:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Slang Agent Test</title>
    <script src="https://unpkg.com/livekit-client@latest/dist/livekit-client.umd.js"></script>
</head>
<body>
    <div id="controls">
        <button id="connect">Connect</button>
        <button id="disconnect">Disconnect</button>
        <button id="mic-toggle">Toggle Mic</button>
    </div>
    <div id="status">Disconnected</div>
    
    <script>
        const room = new LiveKit.Room();
        const status = document.getElementById('status');
        
        document.getElementById('connect').onclick = async () => {
            try {
                // Get token from your LiveKit server or use temporary token
                const token = 'your_participant_token';
                await room.connect('wss://your-instance.livekit.cloud', token);
                status.textContent = 'Connected';
                
                // Enable microphone
                await room.localParticipant.enableCameraAndMicrophone();
            } catch (error) {
                console.error('Failed to connect:', error);
                status.textContent = 'Connection failed';
            }
        };
        
        document.getElementById('disconnect').onclick = () => {
            room.disconnect();
            status.textContent = 'Disconnected';
        };
        
        document.getElementById('mic-toggle').onclick = async () => {
            const enabled = room.localParticipant.isMicrophoneEnabled;
            await room.localParticipant.setMicrophoneEnabled(!enabled);
        };
    </script>
</body>
</html>
```

#### 3. **Command Line Testing with LiveKit CLI**
```bash
# Install LiveKit CLI
npm install -g @livekit/cli

# Generate participant token
livekit-cli token create \
  --api-key your_api_key \
  --api-secret your_api_secret \
  --room test-room \
  --identity test-user \
  --valid-for 24h

# Join room for testing
livekit-cli join-room \
  --url wss://your-instance.livekit.cloud \
  --token your_generated_token
```

### Debugging & Logs

#### Local Debugging
```bash
# Run with debug logging
LIVEKIT_LOG_LEVEL=debug python multi_agent.py

# Check specific component logs
export LIVEKIT_LOG_LEVEL=debug
export OPENAI_LOG_LEVEL=debug
python multi_agent.py
```

#### Docker Debugging
```bash
# Run container with interactive shell
docker run -it --env-file .env slang-agent /bin/bash

# View container logs
docker logs <container_id>

# Run with debug output
docker run --env-file .env -e LIVEKIT_LOG_LEVEL=debug slang-agent
```

### Common Issues & Solutions

#### 1. **Agent Not Connecting**
- Verify LiveKit URL format (must start with `wss://`)
- Check API key and secret are correct
- Ensure room exists or agent can create rooms

#### 2. **Audio Issues**
- Verify microphone permissions in browser
- Check Deepgram API key and quota
- Ensure ElevenLabs API key is valid

#### 3. **LLM Errors**
- Verify OpenAI API key and quota
- Check model availability (gpt-4o-mini)
- Monitor API rate limits

#### 4. **Docker Issues**
- Ensure all environment variables are set
- Check port 8080 is available
- Verify Docker has sufficient resources

### Performance Testing

#### Load Testing
```bash
# Install load testing tools
pip install locust

# Create simple load test
cat > locustfile.py << EOF
from locust import User, task
import asyncio
from livekit import api

class LiveKitUser(User):
    @task
    def connect_to_room(self):
        # Implement room connection logic
        pass
EOF

# Run load test
locust -f locustfile.py --host=wss://your-instance.livekit.cloud
```

### Quick Start with Make Commands

For easier development, use the provided Makefile:

```bash
# Complete setup (creates venv, installs deps, copies .env template)
make dev-setup

# Edit .env with your API keys, then:

# Validate environment and run agent
make dev

# Or run individual commands:
make test          # Validate configuration
make run           # Run agent locally
make docker-test   # Test with Docker
make clean         # Clean up temporary files
```

### Development Tools

#### 1. **Local Validation Script**
```bash
# Check environment, dependencies, and API key formats (requires .env file)
python test_local.py

# CI validation (no environment variables required)
python test_ci.py
```

#### 2. **Make Commands**
```bash
make help          # Show all available commands
make install       # Setup virtual environment
make test          # Run local validation checks (requires .env)
make test-ci       # Run CI validation checks (no env vars needed)
make run           # Start the agent
make docker-build  # Build Docker image
make docker-run    # Run Docker container
make lint          # Format and lint code
make clean         # Clean temporary files
```

### Development Workflow

1. **Setup**: `make dev-setup` and edit `.env`
2. **Validate**: `make test` to check configuration
3. **Develop**: Make changes to `multi_agent.py`
4. **Test locally**: `make run` for direct testing
5. **Test Docker**: `make docker-test` to simulate production
6. **Commit**: Push changes to trigger CI/CD
7. **Monitor**: Check GitHub Actions and Cloud Run deployment

## Cloud Deployment (Google Cloud Run)

This project includes automated deployment to Google Cloud Run using GitHub Actions.

### Prerequisites

1. **Google Cloud Project Setup**
   ```bash
   # Set your project ID
   export PROJECT_ID="your-project-id"
   
   # Enable required APIs
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   gcloud services enable iamcredentials.googleapis.com
   ```

2. **Create Service Account**
   ```bash
   # Create service account for Cloud Run
   gcloud iam service-accounts create slang-agent-sa \
     --display-name="Slang Agent Service Account" \
     --project=$PROJECT_ID
   
   # Grant necessary permissions
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:slang-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:slang-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:slang-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

3. **Setup Workload Identity Federation**
   ```bash
   # Create workload identity pool
   gcloud iam workload-identity-pools create "github-pool" \
     --project=$PROJECT_ID \
     --location="global" \
     --display-name="GitHub Actions Pool"
   
   # Create workload identity provider
   gcloud iam workload-identity-pools providers create-oidc "github-provider" \
     --project=$PROJECT_ID \
     --location="global" \
     --workload-identity-pool="github-pool" \
     --display-name="GitHub Actions Provider" \
     --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
     --issuer-uri="https://token.actions.githubusercontent.com"
   
   # Allow GitHub Actions to impersonate service account
   gcloud iam service-accounts add-iam-policy-binding \
     slang-agent-sa@$PROJECT_ID.iam.gserviceaccount.com \
     --project=$PROJECT_ID \
     --role="roles/iam.workloadIdentityUser" \
     --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_USERNAME/slang"
   ```

4. **Create Secrets in Secret Manager**
   ```bash
   # Create secrets for API keys
   echo -n "your_livekit_api_key" | gcloud secrets create LIVEKIT_API_KEY --data-file=-
   echo -n "your_livekit_api_secret" | gcloud secrets create LIVEKIT_API_SECRET --data-file=-
   echo -n "your_openai_api_key" | gcloud secrets create OPENAI_API_KEY --data-file=-
   echo -n "your_deepgram_api_key" | gcloud secrets create DEEPGRAM_API_KEY --data-file=-
   echo -n "your_eleven_api_key" | gcloud secrets create ELEVEN_API_KEY --data-file=-
   ```

### GitHub Secrets Configuration

Add the following secrets to your GitHub repository:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `GCP_PROJECT_ID` | Your Google Cloud Project ID | `my-project-123` |
| `GCP_REGION` | Google Cloud region for deployment | `us-central1` |
| `GCP_SERVICE_ACCOUNT` | Service account email | `slang-agent-sa@my-project-123.iam.gserviceaccount.com` |
| `GCP_WIF_PROVIDER` | Workload Identity Federation provider | `projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `LIVEKIT_URL` | LiveKit server URL | `wss://your-instance.livekit.cloud` |

**Note**: API keys are now stored in Google Secret Manager instead of GitHub secrets for better security.

### Deployment Process

1. **Push to main branch** - Triggers automatic deployment
2. **Manual deployment** - Use GitHub Actions "Deploy to Cloud Run" workflow
3. **Pull request** - Runs deployment validation (without actual deployment)

### Deployment Configuration

The Cloud Run service is configured with:
- **Memory**: 2Gi
- **CPU**: 1 vCPU
- **Concurrency**: 1000 requests
- **Timeout**: 3600 seconds (1 hour)
- **Scaling**: 0-10 instances
- **Region**: us-central1

### Monitoring Deployment

1. **GitHub Actions**: Monitor deployment progress in the Actions tab
2. **Cloud Console**: View service status in Google Cloud Console
3. **Logs**: Check Cloud Run logs for runtime issues

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LIVEKIT_URL` | Yes | LiveKit server WebSocket URL |
| `LIVEKIT_API_KEY` | Yes | LiveKit API key for authentication |
| `LIVEKIT_API_SECRET` | Yes | LiveKit API secret for authentication |
| `AGENT_IDENTITY` | Yes | Unique identifier for the agent |
| `ROOM_NAME` | Yes | Default room name for sessions |
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM and TTS |
| `DEEPGRAM_API_KEY` | Yes | Deepgram API key for STT |
| `ELEVEN_API_KEY` | Optional | ElevenLabs API key for enhanced TTS |

## Usage

1. **Connect to LiveKit room** using the configured room name
2. **Start conversation** - IntroAgent will greet and ask for information
3. **Provide details** - Share your name and location when prompted
4. **Enjoy story** - StoryAgent will create a personalized interactive story
5. **Interact** - Respond to story prompts and questions
6. **End session** - Say you're finished when ready to conclude

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify all API keys are correctly set
   - Check LiveKit credentials and URL format

2. **Deployment Failures**
   - Ensure GCP service account has proper permissions
   - Verify GitHub secrets are correctly configured
   - Check Cloud Run quotas and limits

3. **Runtime Errors**
   - Review Cloud Run logs for detailed error messages
   - Verify environment variables are properly set
   - Check API key validity and quotas

### Logs and Monitoring

- **Local logs**: Console output when running locally
- **Cloud Run logs**: Available in Google Cloud Console
- **GitHub Actions logs**: Available in repository Actions tab

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

[Add your license information here]
