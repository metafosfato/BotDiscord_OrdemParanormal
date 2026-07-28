import asyncio
import pytest
from src.adapters.audio.edge_tts_adapter import EdgeTTSAdapter

def test_sintetizar_voz_edge_tts():
    adapter = EdgeTTSAdapter()
    texto = "O Paranormal não aceita a razão. Apenas a dor."
    audio_bytes = asyncio.run(adapter.sintetizar_voz(texto))
    
    assert len(audio_bytes) > 0
    assert isinstance(audio_bytes, bytes)
