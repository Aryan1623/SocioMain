import requests
import sseclient
import json

class LangflowClient:
    def __init__(self, base_url, application_token):
        self.base_url = base_url
        self.application_token = application_token

    def post(self, endpoint, body, headers=None):
        if headers is None:
            headers = {"Content-Type": "application/json"}

        headers["Authorization"] = f"Bearer {self.application_token}"
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            raise

    def initiate_session(self, flow_id, langflow_id, input_value, input_type='chat', output_type='chat', stream=False, tweaks=None):
        if tweaks is None:
            tweaks = {}

        endpoint = f"/lf/{langflow_id}/api/v1/run/{flow_id}?stream={str(stream).lower()}"
        body = {
            "input_value": input_value,
            "input_type": input_type,
            "output_type": output_type,
            "tweaks": tweaks
        }
        return self.post(endpoint, body)

    def run_flow(self, flow_id_or_name, langflow_id, input_value, input_type='chat', output_type='chat', tweaks=None, stream=False):
        if tweaks is None:
            tweaks = {}

        try:
            init_response = self.initiate_session(flow_id_or_name, langflow_id, input_value, input_type, output_type, stream, tweaks)

            if not stream and init_response and 'outputs' in init_response:
                flow_outputs = init_response['outputs'][0]
                first_component_outputs = flow_outputs['outputs'][0]
                output = first_component_outputs['outputs']['message']

                # Return the final output text
                return output['message']['text']

        except Exception as e:
            print(f"Error running flow: {e}")
            raise


def main(input_value, input_type='chat', output_type='chat', stream=False):
    flow_id_or_name = 'aed37c10-7ac1-4cf5-9fcd-7c08fb469135'
    langflow_id = '04c10269-3dde-497c-b20f-9ecb31f155db'
    application_token = 'AstraCS:CnDgpfCjLZgcxFWZbxbhWsyZ:c374c393102f859c46633a6c919ab7f8bf83b4c4c83e55b331dcfe8b21c6e855'
    langflow_client = LangflowClient('https://api.langflow.astra.datastax.com', application_token)

    try:
        tweaks = {
            "ChatInput-n0p3k": {},
            "Prompt-qJyGE": {},
            "AstraDBToolComponent-2bEY8": {},
            "Agent-XtCvF": {},
            "ChatOutput-g0GbU": {}
        }

        # Get the final output
        final_output = langflow_client.run_flow(
            flow_id_or_name,
            langflow_id,
            input_value,
            input_type,
            output_type,
            tweaks,
            stream
        )

        # Print only the final output
        print(final_output)

    except Exception as e:
        print("Main Error", e)


if __name__ == "__main__":
    # Define sample input for testing
    input_value = "What is the weather today?"
    input_type = "chat"
    output_type = "chat"
    stream = False

    main(input_value, input_type, output_type, stream)
