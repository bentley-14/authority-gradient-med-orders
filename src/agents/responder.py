"""Responder agent: the order-entry assistant being tested."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from environment.isolated_claude import call_claude
from src.prompts.prompt_builder import read_text


def respond(user_prompt, model, effort):
    """Returns the full call record. The response text is record["raw_output"]["result"]."""
    return call_claude(read_text("responder_system.txt"), user_prompt, model, effort)
