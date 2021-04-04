from rasa_core.channels.facebook import FacebookInput
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
import os
from rasa_core.utils import EndpointConfig

# load your trained agent
interpreter = RasaNLUInterpreter("models/nlu/default/horoscopebot/")
MODEL_PATH = "models/dialogue"
action_endpoint = EndpointConfig(url="https://horoscopebot1212-actions.herokuapp.com/webhook")

agent = Agent.load(MODEL_PATH, interpreter=interpreter)

input_channel = FacebookInput(
    fb_verify="CX5F8U27",
    # you need tell facebook this token, to confirm your URL
    fb_secret="290b5f0dfd2944199a503f2a6cbff8f5",  # your app secret
    fb_access_token="EAAGU2kp7jm0BALoF2ZBIs9zOqkSLgI9QM4256aZCkZAN86zsB7o3IoOTW76DpEPpNJlDMvyIYmm8VQd4l5E3kDZAukVxyoZCglOMw5s9CMqkQ3pIiaev82uVHRzDK0Wp2IpM8V3vEnJmu6gZCCRfOrZCm698BHZC5F2JVYp5SMrg4x79A0ngnC9P3MilFid9k6AZD"
    # token for the page you subscribed to
)
# set serve_forever=False if you want to keep the server running
s = agent.handle_channels([input_channel], int(os.environ.get('PORT', 5004)), serve_forever=True)
