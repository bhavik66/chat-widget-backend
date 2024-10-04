
from typing import Dict


def generate_ai_response(user_message: str) -> Dict:
    # Example logic to include actions based on user message
    if "start" in user_message.lower():
        response = {
            "content": "Let's get started! What would you like to do next?",
            "actions": {
                "action1": "Learn More",
                "action2": "Get Help"
            }
        }
    elif "help" in user_message.lower():
        response = {
            "content": "How can I assist you today?",
            "actions": {
                "action1": "Account Issues",
                "action2": "Technical Support"
            }
        }
    else:
        response = {
            "content": f"AI response to: {user_message}",
            "actions": None
        }
    return response
