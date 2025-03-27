import pyautogui
import random
import time
import logging

def get_response(issue_type):
    responses = {
        "access": ["Here you go!", "Your access's ready to use", "All set"],
        "template": ["it's here \"link\"", "have you tried to look here \"link\"", "found it for you, here you are \"link\""],
        "error": ["fixed", "try now please, should be OK", "thanks for letting me know, now it's working"],
        "rights": ["All done", "you've got this", "done"]
    }
    return random.choice(responses.get(issue_type, ["No predefined response"]))

def type_response(response):
    time.sleep(1)  
    pyautogui.typewrite(response, interval=0.05)
    pyautogui.press("enter")

logging.basicConfig(
    level=logging.INFO,
    filename="our_logs.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def handle_ticket(issue_type):
    logging.info(f"Processing ticket {ticket_id}: {issue_type}")
    response = get_response(issue_type)
    type_response(response)
    logging.info(f"Response sent: {response}")

try:
    handle_ticket(ticket_data)
except Exception as e:
    logging.error(f"Error processing ticket {ticket_id}: {str(e)}")


issue_example = "access"  
handle_ticket(issue_example)
