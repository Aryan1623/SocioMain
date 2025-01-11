from django.shortcuts import render
from django.http import JsonResponse
import requests
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
            raise Exception(f"Langflow API request failed: {e.response.text if e.response else str(e)}")

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
                return output['message']['text']
        except Exception as e:
            raise Exception(f"Error running Langflow flow: {e}")


def chat(request):
    if request.method == "POST":
        try:
            # Parse input JSON from POST request
            data = json.loads(request.body)
            input_value = data.get("input_value", "").strip()

            if not input_value:
                return JsonResponse({"error": "Input value is required."}, status=400)

            # Langflow setup
            flow_id_or_name = 'aed37c10-7ac1-4cf5-9fcd-7c08fb469135'
            langflow_id = '04c10269-3dde-497c-b20f-9ecb31f155db'
            application_token = 'AstraCS:CnDgpfCjLZgcxFWZbxbhWsyZ:c374c393102f859c46633a6c919ab7f8bf83b4c4c83e55b331dcfe8b21c6e855'
            langflow_client = LangflowClient('https://api.langflow.astra.datastax.com', application_token)

            # Prepare tweaks (if any)
            tweaks = {
                "ChatInput-n0p3k": {},
                "Prompt-qJyGE": {},
                "AstraDBToolComponent-2bEY8": {},
                "Agent-XtCvF": {},
                "ChatOutput-g0GbU": {}
            }

            # Run the Langflow flow
            output_value = langflow_client.run_flow(
                flow_id_or_name,
                langflow_id,
                input_value,
                "chat",
                "chat",
                tweaks,
                stream=False
            )

            # Print output to the terminal
            print(f"Output: {output_value}")

            # Return response
            return JsonResponse({"output": output_value}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

    # Simulate a sample POST request with input value
    sample_input = {
        "input_value": "Hello, how are you?"
    }
    return render(request, "window/chat.html", {"sample_input": json.dumps(sample_input)})


def index(request):
    return render(request,"window/index.html")


# API constants
API_URL = "https://api.langflow.astra.datastax.com/lf/04c10269-3dde-497c-b20f-9ecb31f155db/api/v1/run/a7c93c55-0a3e-4f15-817c-c9dfd5e59cc4?stream=false"
AUTH_TOKEN = "Bearer AstraCS:UcgmqraZQknXpDqsZaLgJEmW:ca8b23d24eee57556d40ddd491e7af04f9b2809d54a04cc2927cf3faae9c5e41"

def fetch_chart_script(user_input):
    headers = {
        "Content-Type": "application/json",
        "Authorization": AUTH_TOKEN,
    }
    payload = {
        "input_value": user_input,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "ChatInput-uWTJc": {},
            "ChatOutput-nULdU": {},
            "Agent-gSvFc": {},
            "AstraDBToolComponent-tejXG": {},
        },
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()  # Raise error for bad response
    response_data = response.json()

    # Extract the Chart.js script from the response
    try:
        chart_script = response_data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
        return chart_script
    except KeyError as e:
        return None

def chart_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('query')
        if user_input.strip():
            try:
                chart_script = fetch_chart_script(user_input)
                if chart_script:
                    return JsonResponse({'chart_script': chart_script})
                else:
                    return JsonResponse({'error': 'Chart script not found in response.'}, status=500)
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Please enter a valid input!'}, status=400)
    return render(request, 'window/graphs.html')
