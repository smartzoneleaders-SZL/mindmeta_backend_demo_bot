
import asyncio
import logging




from utils.for_telephonic.opensips_ws_lib import OpenSIPSClient
from utils.for_telephonic.elevenlabs_streamer import ElevenLabsStreamer

logger = logging.getLogger(__name__)


BOT_SCRIPT = [
    "Hello! I'm an AI assistant calling from our system. How are you doing today?",
    "I'm calling to confirm your upcoming appointment scheduled for tomorrow at 2 PM. Is this time still convenient for you?",
    "Great! Just to confirm, we have your appointment set with Dr. Smith at our main office location. Is that correct?",
    "Perfect! Do you have any questions before your appointment tomorrow?",
    "Excellent. We look forward to seeing you tomorrow at 2 PM. Please remember to bring your insurance card and arrive 15 minutes early to complete any necessary paperwork. Thank you and have a great day!"
]


async def voice_bot_demo(args):
    """Demonstrate the voice AI bot functionality with ElevenLabs TTS"""
    # Create client instance
    client = OpenSIPSClient(
        server_uri=args.server,
        username=args.username,
        password=args.password,
        domain=args.domain,
        debug_level=args.debug_level
    )
    
    try:
        # Connect to server
        logger.info(f"Connecting to OpenSIPS WebSocket server: {args.server}")
        connected = await client.connect()
        
        if not connected:
            logger.error("Failed to connect to OpenSIPS WebSocket server")
            return
        
        # Register with server
        logger.info("Registering with SIP server...")
        registered = await client.register()
        
        if not registered:
            logger.error("Failed to register with SIP server")
            return
        
        logger.info("Successfully registered!")
        
        # Place a call to the destination
        logger.info(f"Placing call to extension {args.destination}...")
        result = await client.place_call(args.destination, timeout=30)
        
        if not result["success"]:
            logger.error(f"Call failed: {result['state']}")
            return
            
        # Call was answered
        call_id = result["call_id"]
        logger.info(f"Call answered! Call-ID: {call_id}")
        
        # Create ElevenLabs streamer
        streamer = ElevenLabsStreamer(client, call_id)
        
        # Play welcome message
        logger.info("Starting conversation...")
        
        # Process each message in the script
        for message in BOT_SCRIPT:
            logger.info(f"Bot saying: {message}")
            
            # Stream message to the call
            await streamer.stream_from_elevenlabs(
                text=message,
                voice_id=args.voice_id,
                optimize_streaming_latency=args.latency
            )
            
            # Wait for user response (simulated)
            logger.info("Waiting for user response...")


            await asyncio.sleep(5)  # In a real system, you'd use speech recognition here
        
        # End streaming
        streamer.stop_streaming()
        
        # Wait a moment before ending call
        await asyncio.sleep(1)
        
        # End the call
        logger.info("Ending call...")
        await client.end_call(call_id)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Disconnect from the server
        if hasattr(client, 'disconnect') and client.connection:
            await client.disconnect()
        logger.info("Exiting...")