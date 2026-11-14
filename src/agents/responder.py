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


def respond_two_turns(user_prompt, second_turn, model, effort):
    """Sends user_prompt, waits for the reply, then sends second_turn in the same
    conversation. Returns the full record. The two reply texts are
    record["results"][0]["result"] and record["results"][1]["result"]."""
    from environment.isolated_claude import call_claude_conversation
    return call_claude_conversation(read_text("responder_system.txt"),
                                    [user_prompt, second_turn], model, effort)


def respond_with_tool(user_prompt, next_turn, model, effort, ledger_path):
    """Conversation in which the responder can call the enter_order tool.
    next_turn(n) returns the next user message after n turns, or None to stop."""
    from environment.isolated_claude import call_claude_tool_conversation
    return call_claude_tool_conversation(read_text("responder_tool_system.txt"), user_prompt,
                                         next_turn, model, effort, ledger_path)
