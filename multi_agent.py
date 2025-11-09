import asyncio
import logging
import os
import threading
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from livekit import api
from livekit.agents import (
    Agent,
    AgentSession,
    ChatContext,
    JobContext,
    JobProcess,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    metrics,
)
from livekit.agents.job import get_job_context
from livekit.agents.llm import function_tool
from livekit.agents.voice import MetricsCollectedEvent
from livekit.plugins import deepgram, elevenlabs, openai, silero

# uncomment to enable Krisp BVC noise cancellation, currently supported on Linux and MacOS
# from livekit.plugins import noise_cancellation

## The storyteller agent is a multi-agent that can handoff the session to another agent.
## This example demonstrates more complex workflows with multiple agents.
## Each agent could have its own instructions, as well as different STT, LLM, TTS,
## or realtime models.

logger = logging.getLogger("multi-agent")

load_dotenv()

# Validate required environment variables
required_env_vars = {
    "LIVEKIT_URL": "LiveKit server URL",
    "LIVEKIT_API_KEY": "LiveKit API key", 
    "LIVEKIT_API_SECRET": "LiveKit API secret",
    "OPENAI_API_KEY": "OpenAI API key"
}

optional_env_vars = {
    "DEEPGRAM_API_KEY": "Deepgram API key (fallback to OpenAI STT if missing)",
    "ELEVEN_API_KEY": "ElevenLabs API key"
}

# Check required variables
missing_required = []
for var, description in required_env_vars.items():
    if not os.getenv(var):
        missing_required.append(f"{var} ({description})")

if missing_required:
    logger.error(f"Missing required environment variables: {', '.join(missing_required)}")
    raise ValueError(f"Missing required environment variables: {', '.join(missing_required)}")

# Check optional variables
missing_optional = []
for var, description in optional_env_vars.items():
    if not os.getenv(var):
        missing_optional.append(f"{var} ({description})")

if missing_optional:
    logger.warning(f"Missing optional environment variables: {', '.join(missing_optional)}")

common_instructions = (
    "Your name is Echo. You are a story teller that interacts with the user via voice."
    "You are curious and friendly, with a sense of humor."
)


@dataclass
class StoryData:
    # Shared data that's used by the storyteller agent.
    # This structure is passed as a parameter to function calls.

    name: Optional[str] = None
    location: Optional[str] = None


class IntroAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=f"{common_instructions} Your goal is to gather a few pieces of "
            "information from the user to make the story personalized and engaging."
            "You should ask the user for their name and where they are from."
            "Start the conversation with a short introduction.",
        )

    async def on_enter(self):
        # when the agent is added to the session, it'll generate a reply
        # according to its instructions
        self.session.generate_reply()

    @function_tool
    async def information_gathered(
        self,
        context: RunContext[StoryData],
        name: str,
        location: str,
    ):
        """Called when the user has provided the information needed to make the story
        personalized and engaging.

        Args:
            name: The name of the user
            location: The location of the user
        """

        context.userdata.name = name
        context.userdata.location = location

        story_agent = StoryAgent(name, location)
        # by default, StoryAgent will start with a new context, to carry through the current
        # chat history, pass in the chat_ctx
        # story_agent = StoryAgent(name, location, chat_ctx=self.chat_ctx)

        logger.info(
            "switching to the story agent with the provided user data: %s", context.userdata
        )
        return story_agent, "Let's start the story!"


class StoryAgent(Agent):
    def __init__(self, name: str, location: str, *, chat_ctx: Optional[ChatContext] = None) -> None:
        super().__init__(
            instructions=f"{common_instructions}. You should use the user's information in "
            "order to make the story personalized."
            "create the entire story, weaving in elements of their information, and make it "
            "interactive, occasionally interating with the user."
            "do not end on a statement, where the user is not expected to respond."
            "when interrupted, ask if the user would like to continue or end."
            f"The user's name is {name}, from {location}.",
            # each agent could override any of the model services, including mixing
            # realtime and non-realtime models
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=elevenlabs.TTS(),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self):
        # when the agent is added to the session, we'll initiate the conversation by
        # using the LLM to generate a reply
        self.session.generate_reply()

    @function_tool
    async def story_finished(self, context: RunContext[StoryData]):
        """When you are fininshed telling the story (and the user confirms they don't
        want anymore), call this function to end the conversation."""
        # interrupt any existing generation
        self.session.interrupt()

        # generate a goodbye message and hang up
        # awaiting it will ensure the message is played out before returning
        await self.session.generate_reply(
            instructions=f"say goodbye to {context.userdata.name}", allow_interruptions=False
        )

        job_ctx = get_job_context()
        await job_ctx.api.room.delete_room(api.DeleteRoomRequest(room=job_ctx.room.name))


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Try to use Deepgram STT with fallback to OpenAI Whisper
    try:
        stt_provider = deepgram.STT(model="nova-3")
        logger.info("Using Deepgram STT")
    except Exception as e:
        logger.warning(f"Failed to initialize Deepgram STT: {e}. Falling back to OpenAI Whisper")
        stt_provider = openai.STT()
    
    session = AgentSession[StoryData](
        vad=ctx.proc.userdata["vad"],
        # any combination of STT, LLM, TTS, or realtime API can be used
        llm=openai.LLM(model="gpt-4o-mini"),
        stt=stt_provider,
        tts=elevenlabs.TTS(),
        userdata=StoryData(),
    )

    # log metrics as they are emitted, and total usage after session is over
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    await session.start(
        agent=IntroAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # uncomment to enable Krisp BVC noise cancellation
            # noise_cancellation=noise_cancellation.BVC(),
        ),
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )


def start_simple_health_server():
    """Start a very simple health server in a separate thread.
    
    WARNING: This approach can cause event loop conflicts with LiveKit.
    Only use if you absolutely need custom health endpoints.
    The built-in LiveKit health server is recommended instead.
    """
    try:
        # Uncomment these imports at the top of the file first:
        # from fastapi import FastAPI
        # import uvicorn
        
        health_port = int(os.getenv("HEALTH_PORT", "8080"))

        app = FastAPI(title="Voice Agent Health", docs_url=None, redoc_url=None, openapi_url=None)

        @app.get("/")
        @app.get("/health")
        def health():
            return {"status": "healthy"}

        @app.get("/ready")
        def ready():
            return {"status": "ready"}

        def run_server():
            uvicorn.run(app, host="0.0.0.0", port=health_port, log_level="error")

        # Start in background thread
        health_thread = threading.Thread(target=run_server, daemon=True)
        health_thread.start()
        logger.info(f"Health server started on port {health_port}")

    except Exception as e:
        logger.warning(f"Failed to start health server: {e}")


if __name__ == "__main__":
    start_simple_health_server()
    import sys
    
    # Configure port based on environment
    # Cloud Run sets PORT environment variable, default to 8081 for local development
    health_port = int(os.environ.get('PORT', 8081))
    
    logger.info(f"Starting LiveKit agent with health check on port {health_port}")
    logger.info(f"Environment: PORT={os.environ.get('PORT', 'not set')}")
    logger.info(f"LiveKit URL: {os.environ.get('LIVEKIT_URL', 'not set')}")
    
    # For both Cloud Run and local development, use the same approach
    # Cloud Run will handle health checks via the LiveKit agent's built-in endpoints
    try:
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=entrypoint,
                prewarm_fnc=prewarm,
                port=health_port,
                initialize_process_timeout=60
            ),
        )
    except Exception as e:
        logger.error(f"Failed to start LiveKit agent: {e}")
        raise