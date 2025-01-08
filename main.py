from autogen import ConversableAgent
from dotenv import load_dotenv
import os
from autogen import ConversableAgent, register_function
from tools.read_mail import read_mail_tool
from tools.send_mail import send_mail_tool
from tools.calendar_tool import find_free_time_tool, schedule_meeting_tool
from tools.teams_tool import notify_teams_tool
 
from typing import Dict,Union
from autogen.io.base import IOStream
from autogen.agentchat.agent import Agent
from autogen.formatting_utils import colored
from autogen.oai.client import OpenAIWrapper
from autogen.code_utils import content_str
 
 
# Load environment variables
load_dotenv()
 
# Define environment variable keys for API setup
model = os.getenv('model')
api_type = os.getenv('api_type')
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')
api_version = os.getenv('api_version')
 
config_list = [{"model": model, "api_type": api_type, "api_key": api_key, "base_url": base_url, "api_version": api_version}]
llm_config = {"timeout": 600, "cache_seed": 42, "config_list": config_list, "temperature": 0}
 
def t(r,c):
    # print(f'R:{r}')
    # print(f'C:{c}')
    pass
 
 
class CustomConversableAgent(ConversableAgent):
    def __init__(self, name,system_message,llm_config,is_termination_msg, human_input_mode,max_consecutive_auto_reply):
        super().__init__(name=name,system_message=system_message, llm_config=llm_config,is_termination_msg=is_termination_msg,human_input_mode=human_input_mode,max_consecutive_auto_reply=max_consecutive_auto_reply)
 
    def _print_received_message(self, message: Union[Dict, str], sender: Agent):
        iostream = IOStream.get_default()
       
        # print the message received
        iostream.print(colored(sender.name, "yellow"), "(to", f"{self.name}):\n", flush=True)
        add_e('assistant',f'{sender.name} (to {self.name}):\n')#101
        message = self._message_to_dict(message)
 
        if message.get("tool_responses"):  # Handle tool multi-call responses
            for tool_response in message["tool_responses"]:
                self._print_received_message(tool_response, sender)
            if message.get("role") == "tool":
                return  # If role is tool, then content is just a concatenation of all tool_responses
 
        if message.get("role") in ["function", "tool"]:
            if message["role"] == "function":
                id_key = "name"
            else:
                id_key = "tool_call_id"
            id = message.get(id_key, "No id found")
            func_print = f"***** Response from calling {message['role']} ({id}) *****"
            iostream.print(colored(func_print, "green"), flush=True)
            add_e('assistant',func_print)#101
            iostream.print(message["content"], flush=True)
            add_e('assistant',message["content"])#101
            iostream.print(colored("*" * len(func_print), "green"), flush=True)
            add_e('assistant',"*" * len(func_print))#101
 
        else:
            content = message.get("content")
            if content is not None:
                if "context" in message:
                    content = OpenAIWrapper.instantiate(
                        content,
                        message["context"],
                        self.llm_config and self.llm_config.get("allow_format_str_template", False),
                    )
                iostream.print(content_str(content), flush=True)
                add_e('assistant',f'{content_str(content)}')#101
            if "function_call" in message and message["function_call"]:
                function_call = dict(message["function_call"])
                func_print = (
                    f"***** Suggested function call: {function_call.get('name', '(No function name found)')} *****"
                )
                iostream.print(colored(func_print, "green"), flush=True)
                add_e('assistant',func_print)#101
                iostream.print(
                    "Arguments: \n",
                    function_call.get("arguments", "(No arguments found)"),
                    flush=True,
                    sep="",
                )
                add_e('assistant',f'Arguments: \n{function_call.get("arguments", "(No arguments found)")}')#101
                iostream.print(colored("*" * len(func_print), "green"), flush=True)
                add_e('assistant',"*" * len(func_print))#101
            if "tool_calls" in message and message["tool_calls"]:
                for tool_call in message["tool_calls"]:#111
                    id = tool_call.get("id", "No tool call id found")
                    function_call = dict(tool_call.get("function", {}))
                    func_print = f"***** Suggested tool call ({id}): {function_call.get('name', '(No function name found)')} *****"
                    iostream.print(colored(func_print, "green"), flush=True)
                    add_e('assistant',func_print)#101
                    iostream.print(
                        "Arguments: \n",
                        function_call.get("arguments", "(No arguments found)"),
                        flush=True,
                        sep="",
                    )
                    add_e('assistant',f'Arguments: \n{function_call.get("arguments", "(No arguments found)")}')#101
                    iostream.print(colored("*" * len(func_print), "green"), flush=True)
                    add_e('assistant',"*" * len(func_print))#101
 
        iostream.print("\n", "-" * 80, flush=True, sep="")
        add_e('assistant',"-" * 80)#101
 
 
 
 
 
 
# Define the Assistant Agent with improved system messages for clarity
assistant = CustomConversableAgent(
    name="Assistant",
    system_message = (
        "I am an AI assistant that can help you with various tasks. "
    ),
    llm_config=llm_config,
   
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
 
    max_consecutive_auto_reply=5  # Prevent endless loop by limiting replies
)
 
 
 
user_proxy = CustomConversableAgent(
    name="User",
    system_message="You execute commands and provide responses back to the assistant.",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="Always",
    max_consecutive_auto_reply=1  # Limit consecutive auto-replies to 5
)
 
 
# Register tool functions
register_function(
    read_mail_tool,
    caller=assistant,
    executor=user_proxy,
    name="read_mail",
    description="Fetches a list of emails from the inbox.",
)
register_function(
    send_mail_tool,
    caller=assistant,
    executor=user_proxy,
    name="send_mail",
    description="Sends an email. Requires recipient email, subject, and body.",
)

register_function(
    find_free_time_tool,
    caller=assistant,
    executor=user_proxy,
    name="check_calendar",
    description="Checks calendar availability for scheduling meetings.",
)
register_function(
    schedule_meeting_tool,
    caller=assistant,
    executor=user_proxy,
    name="schedule_meeting",
        description="Schedules a meeting in the calendar and sends a Teams notification.",
)
register_function(
    notify_teams_tool,
    caller=assistant,
    executor=user_proxy,
    name="notify_teams",
    description="Sends a message to a Microsoft Teams chat.",
)
add_e = t
 
 
 
def handle_query(user_input,add_entry):
    global add_e
    add_e = add_entry
    chat_result = user_proxy.initiate_chat(
    assistant,
    message=user_input,
    # clear_history = False
    )
 
