from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import AskForPermissionsConsentCard
from ask_sdk_model.services import ServiceException

from auxilary import get_a_question, send_email

import requests

sb = StandardSkillBuilder(
        table_name='interview_me_users',
        auto_create_table=True,
        )
help_text = """Please tell me a topic. I will ask a question from that topic."""
skill_name = "Interview Me"
NOTIFY_MISSING_PERMISSIONS = """
Please enable email permissions in the Amazon Alexa app.
"""
ERROR = """
Something wen't bad. Please try again in a while.
"""
permissions = ["alexa::profile:email:read"]

class LaunchRequestHandler(AbstractRequestHandler):
     def can_handle(self, handler_input):
         # type: (HandlerInput) -> bool
         return is_request_type("LaunchRequest")(handler_input)

     def handle(self, handler_input):
         # type: (HandlerInput) -> Response
         speech_text = "Welcome, Which topic should I ask you about ?"

         handler_input.response_builder.speak(
                speech_text
            )
         handler_input.response_builder.ask(
                help_text
            )
         handler_input.response_builder.set_should_end_session(
                False
            )
         return handler_input.response_builder.response

class TopicIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("TopicIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        req_envelope = handler_input.request_envelope
        attrib_manager = handler_input.attributes_manager

        requested_topic = slots.get("TopicSlot").resolutions.resolutions_per_authority[0].values[0].value.name
        print(requested_topic)
        # ["resolutionsPerAuthority"][0].value.name

        perma_attrs = attrib_manager.persistent_attributes
        session_attrs = attrib_manager.session_attributes
        if not session_attrs:
            session_attrs = {}

        d_list = perma_attrs.get('done')
        cur_question = get_a_question(d_list if d_list else [], [requested_topic])
        if not cur_question:
            speech_text = "Sorry, I don't have any more questions on {}. Try another topic ?".format(requested_topic)
        else:
            cur_question['problem'].replace('&', 'and')
            session_attrs['cur_q'] = cur_question
            speech_text = cur_question['title'] + "\n" + cur_question['problem']
            if perma_attrs.get('done'):
                perma_attrs['done'].append(cur_question['qlink'])
            else:
                perma_attrs['done'] = [cur_question['qlink']]
            attrib_manager.save_persistent_attributes()

        handler_input.response_builder.speak(
                speech_text
            ).set_should_end_session(
                False
            )
        return handler_input.response_builder.response

class EmailIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("EmailIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attrib_manager = handler_input.attributes_manager
        req_envelope = handler_input.request_envelope
        session_attrs = attrib_manager.session_attributes
        intent_context = req_envelope.context.system

        if not (req_envelope.context.system.user.permissions and
                req_envelope.context.system.user.permissions.consent_token):
            handler_input.response_builder.speak(NOTIFY_MISSING_PERMISSIONS)
            handler_input.response_builder.set_card(
                AskForPermissionsConsentCard(permissions=permissions)
                )
            return handler_input.response_builder.response
        try:
            uri = intent_context.api_endpoint
            api_access = intent_context.api_access_token
            geter = "/v2/accounts/~current/settings/Profile.email"
            headers = {
                'Content-type': 'application/json',
                'Authorization': 'Bearer {}'.format(api_access),
            }
            x = requests.get(uri+geter, headers=headers)
            to_email = x.text
            print(x)
            # print(to_email)
            send_email(to_email, session_attrs['cur_q'])
            speech_text = "Your email is on the way. It will reach you at {}".format(to_email)

            handler_input.response_builder.speak(
                    speech_text
                ).set_should_end_session(
                    False
                )
        except Exception as e:
            raise e

        return handler_input.response_builder.response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "You can tell me a topic and I'll ask you questions from that !"
        "For example, I can ask you about linked list, stack, queue etc."

        handler_input.response_builder.speak(speech_text).ask(speech_text)
        return handler_input.response_builder.response

class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input)
                         or is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text)
        return handler_input.response_builder.response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # any cleanup logic goes here

        return handler_input.response_builder.response

class AllExceptionHandler(AbstractExceptionHandler):

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        # Log the exception in CloudWatch Logs
        print(exception)

        speech = "Sorry, I didn't get it. Can you please say it again!!"
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(TopicIntentHandler())
sb.add_request_handler(EmailIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(AllExceptionHandler())

handler = sb.lambda_handler()
