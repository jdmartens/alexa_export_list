import boto3
import csv
import io
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

class ExportListIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and \
               handler_input.request_envelope.request.intent.name == "ExportListIntent"

    def handle(self, handler_input):
        # Get the list name from the user's input
        list_name = handler_input.request_envelope.request.intent.slots["list_name"].value

        # Fetch the specified Alexa list
        list_client = handler_input.service_client_factory.get_list_management_service()
        lists = list_client.get_lists()
        user_list = next((l for l in lists.lists if l.name.lower() == list_name.lower()), None)
        
        if not user_list:
            speech_text = f"I couldn't find a list named {list_name}. Please try again with a valid list name."
            return handler_input.response_builder.speak(speech_text).response

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
        
        speech_text = f"Your {list_name} list has been exported and sent via email."
        return handler_input.response_builder.speak(speech_text).response

def create_email_with_attachment(csv_data, filename):
    # Implement email creation with attachment here
    # Return the raw email message

sb = SkillBuilder()
sb.add_request_handler(ExportListIntentHandler())
lambda_handler = sb.lambda_handler()

