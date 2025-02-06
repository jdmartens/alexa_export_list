import boto3
import csv
import io
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

class ExportListHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "Task"

    def handle(self, handler_input):
        # Get the list name from the task input
        task = handler_input.request_envelope.request
        if task.name != "get_list":
            return handler_input.response_builder.speak("Invalid task").set_should_end_session(True).response
        
        list_name = task.input['list_name']

        # Fetch the specified Alexa list
        list_client = handler_input.service_client_factory.get_list_management_service()
        lists = list_client.get_lists()
        user_list = next((l for l in lists.lists if l.name.lower() == list_name.lower()), None)
        
        if not user_list:
            return handler_input.response_builder.speak(f"List {list_name} not found").set_should_end_session(True).response

        # Fetch list items
        list_items = list_client.get_list_items(user_list.list_id)
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow(["Item", "Status"])
        for item in list_items.items:
            csv_writer.writerow([item.value, item.status])
        
        # Send email with CSV attachment
        ses_client = boto3.client('ses')
        response = ses_client.send_raw_email(
            Source='sender@example.com',
            Destinations=['recipient@example.com'],
            RawMessage={
                'Data': create_email_with_attachment(csv_buffer.getvalue(), f"{list_name}.csv")
            }
        )
        
        return handler_input.response_builder.speak(f"Your {list_name} list has been exported and sent via email").set_should_end_session(True).response

def create_email_with_attachment(csv_data, filename):
    # Implement email creation with attachment here
    # Return the raw email message
    pass

sb = SkillBuilder()
sb.add_request_handler(ExportListHandler())
lambda_handler = sb.lambda_handler()
