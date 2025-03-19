from abc import ABC, abstractmethod
from typing import Any, List, Optional
from colorama import Fore
import asyncio

class ResponseStreamListener(ABC):
    """Abstract base class for response stream listeners"""
    @abstractmethod
    async def on_stream(self, text: str):
        """Called when new text is available"""
        pass

class ConsoleStreamer(ResponseStreamListener):
    """A simple console-based streamer that prints responses in color"""
    async def on_stream(self, text: str):
        print(Fore.RED + f"{text}" + Fore.RESET)

class ResponseStreamer:
    """Manages multiple response stream listeners"""
    def __init__(self):
        self.listeners: List[ResponseStreamListener] = []

    def add_listener(self, listener: ResponseStreamListener):
        self.listeners.append(listener)

    def remove_listener(self, listener: ResponseStreamListener):
        self.listeners.remove(listener)

    async def stream(self, text: str):
        """Stream text to all listeners asynchronously"""
        for listener in self.listeners:
            await listener.on_stream(text) 