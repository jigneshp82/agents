from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests



class NotificationToolInput(BaseModel):
    """Input schema for Notification Tool."""
    message: str = Field(..., description="message we want to send to user as notification.")

class NotificationTool(BaseTool):
    name: str = "Pushover notification tool"
    description: str = (
        "This tool is to notify user the output of stock picker. "
        "This tool send a notification using push over application to users phone."
    )
    args_schema: Type[BaseModel] = NotificationToolInput

    def _run(self, message: str) -> str:
        # Implementation goes here
        print (f'message : {message}')
        payload = {"user":os.getenv("PUSHOVER_USER"),"token": os.getenv("PUSHOVER_TOKEN"), "message": message}
        requests.post(os.getenv("PUSHOVER_URL"),payload)
        return '{"Notification":"ok"}'
