# Python script
"""
GUI Module
This package handles:
- PyQt5/PySide GUI Interface
- Voice & Text Chat UI
- Cross-Platform Compatibility
"""

from .main_window import AI_GUI
from .voice_gui import VoiceGUI

__all__ = ["AI_GUI", "VoiceGUI"]