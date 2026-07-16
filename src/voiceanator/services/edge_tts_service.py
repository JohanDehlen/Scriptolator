import asyncio
from typing import List

import edge_tts


class EdgeTTSService:
    """
    Service responsible for interacting with Microsoft Edge TTS.

    This class hides all communication with the edge-tts library from the UI,
    keeping the project architecture clean and maintainable.
    """

    @staticmethod
    def get_voices() -> List[str]:
        """
        Retrieve all available Microsoft Edge voices.

        Returns:
            A sorted list of voice short names.
        """

        try:
            return asyncio.run(EdgeTTSService._load_voices())
        except RuntimeError:
            # If an event loop is already running (future-proofing),
            # create a temporary one.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                return loop.run_until_complete(
                    EdgeTTSService._load_voices()
                )
            finally:
                loop.close()

    @staticmethod
    async def _load_voices() -> List[str]:
        """
        Internal async method that communicates with Edge TTS.
        """

        manager = await edge_tts.VoicesManager.create()

        voices = manager.voices

        names = sorted(
            voice["ShortName"]
            for voice in voices
        )

        return names