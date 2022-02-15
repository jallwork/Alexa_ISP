# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import joke

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from ask_sdk.standard import StandardSkillBuilder

from ask_sdk_model.services.monetization import (
    EntitledState, PurchasableState, InSkillProductsResponse, Error,
    InSkillProduct)
from ask_sdk_model.interfaces.monetization.v1 import PurchaseResult
from ask_sdk_model import Response, IntentRequest
from ask_sdk_model.interfaces.connections import SendRequestDirective

skill_name = "johns joke skill"

def in_skill_product_response(handler_input):
    """Get the In-skill product response from monetization service."""
    # type: (HandlerInput) -> Union[InSkillProductsResponse, Error]
    locale = handler_input.request_envelope.request.locale
    ms = handler_input.service_client_factory.get_monetization_service()
    return ms.get_in_skill_products(locale)

def get_all_entitled_products(in_skill_product_list):
    """Get list of in-skill products in ENTITLED state."""
    # type: (List[InSkillProduct]) -> List[InSkillProduct]
    entitled_product_list = [
        l for l in in_skill_product_list if (
                l.entitled == EntitledState.ENTITLED)]
    return entitled_product_list

def get_speakable_list_of_products(entitled_products_list):
    """Return product list in speakable form."""
    # type: (List[InSkillProduct]) -> str
    product_names = [item.name for item in entitled_products_list]
    if len(product_names) > 1:
        # If more than one, add and 'and' in the end
        speech = " and ".join(
            [", ".join(product_names[:-1]), product_names[-1]])
    else:
        # If one or none, then return the list content in a string
        speech = ", ".join(product_names)
    return speech

class TellMeMoreHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("TellMeMoreIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In TellMeMoreHandler")

        # Tell the user about the product(s)
        speak_output = 'You can upgrade to hear more jokes. Just say, "Upgrade" to purchase this product.'
        
        reprompt = "I didn't catch that. What can I help you with?"
        return handler_input.response_builder.speak(speak_output).ask(
                reprompt).response

class BuyHandler(AbstractRequestHandler):
    """Handler for letting users buy the product.
    User says: Alexa, buy <category>.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BuyIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In BuyHandler")

        product_id = 'amzn1.adg.product.d0aed689-6761-483c-baf9-9d282ab7b788'
        return handler_input.response_builder.add_directive(
            SendRequestDirective(
                name="Buy",
                payload={
                    "InSkillProduct": {
                        "productId": product_id
                    }
                },
                token="buyToken")
        ).response


class BuyResponseHandler(AbstractRequestHandler):
    """This handles the Connections.Response event after a buy occurs."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_request_type("Connections.Response")(handler_input) and
                handler_input.request_envelope.request.name == "Buy")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In BuyResponseHandler")
        if handler_input.request_envelope.request.status.code == "200":
            speech = None
            reprompt = None
            purchase_result = handler_input.request_envelope.request.payload.get(
                "purchaseResult")
            if purchase_result == PurchaseResult.ACCEPTED.value:
                session_attr = handler_input.attributes_manager.session_attributes
                session_attr["paid_jokes"] = True
                handler_input.attributes_manager.session_attributes = session_attr

                speech = "You have bought the access to more jokes, enjoy"
                reprompt = "You can ask for more jokes"
            elif purchase_result in (
                    PurchaseResult.DECLINED.value,
                    PurchaseResult.ERROR.value,
                    PurchaseResult.NOT_ENTITLED.value):
                speech = "Thanks for your interest. Ask for another free joke"
                reprompt = "Ask for a joke"
            elif purchase_result == PurchaseResult.ALREADY_PURCHASED.value:
                logger.info("Already purchased product")
                speech = " You've already purchased more jokes, just ask for another joke"
                reprompt = "Ask for a joke, help or exit"
            else:
                # Invalid purchase result value
                logger.info("Purchase result: {}".format(purchase_result))
                speech = "Sorry, there was an error, please try again"
                reprompt = "Ask for a joke, help or exit"

            return handler_input.response_builder.speak(speech).ask(
                reprompt).response
        else:
            logger.log("Error: {}".format(
                handler_input.request_envelope.request.status.message))

            return handler_input.response_builder.speak(
                "There was an error handling your purchase request. "
                "Please try again or ask for help")

class RefundPurchaseHandler(AbstractRequestHandler):
    #
    #Deal with refund requests
    #User says: Alexa, refund
    #
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RefundPurchase")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In RefundPurchaseHandler")

        product_id= 'amzn1.adg.product.d0aed689-6761-483c-baf9-9d282ab7b788'

        return handler_input.response_builder.add_directive(
            SendRequestDirective(
                name="Cancel",
                payload={
                    "InSkillProduct": {
                        "productId": product_id
                    }
                },
                token="correlationToken")
        ).response

class CancelResponseHandler(AbstractRequestHandler):
    #This handles the Connections.Response event after a cancel occurs.
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_request_type("Connections.Response")(handler_input) and
                handler_input.request_envelope.request.name == "Cancel")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelResponseHandler")
        in_skill_response = in_skill_product_response(handler_input)
        product_id = handler_input.request_envelope.request.payload.get("productId")

        if in_skill_response:
            product = [l for l in in_skill_response.in_skill_products
                       if l.product_id == product_id]
            if handler_input.request_envelope.request.status.code == "200":
                speech = None
                reprompt = None
                purchase_result = handler_input.request_envelope.request.payload.get(
                        "purchaseResult")
                purchasable = product[0].purchasable
                if purchase_result == PurchaseResult.ACCEPTED.value:
                    session_attr = handler_input.attributes_manager.session_attributes
                    session_attr["paid_jokes"] = False
                    handler_input.attributes_manager.session_attributes = session_attr
                    speech = ("You have successfully cancelled your paid joke access.")
                    reprompt = "Ask for a free joke"

                if purchase_result == PurchaseResult.DECLINED.value:
                    if purchasable == PurchasableState.PURCHASABLE:
                        speech = ("You don't currently have paid joke access.")
                    else:
                        speech = "Ask for a free joke"
                    reprompt = "Ask for a free joke"

                return handler_input.response_builder.speak(speech).ask(
                    reprompt).response
            else:
                logger.log("Connections.Response indicated failure. "
                           "Error: {}".format(
                    handler_input.request_envelope.request.status.message))

                return handler_input.response_builder.speak(
                        "There was an error handling your cancellation "
                        "request. Please try again or contact us for "
                        "help").response


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome, you can ask for a joke or say hello"

        in_skill_response = in_skill_product_response(handler_input)
        if isinstance(in_skill_response, InSkillProductsResponse):
            entitled_prods = get_all_entitled_products(in_skill_response.in_skill_products)
            if entitled_prods and len(entitled_prods) > 0:
                session_attr = handler_input.attributes_manager.session_attributes
                session_attr["paid_jokes"] = True
                handler_input.attributes_manager.session_attributes = session_attr

            in_skill_response = in_skill_product_response(handler_input)
        if isinstance(in_skill_response, InSkillProductsResponse):
            entitled_prods = get_all_entitled_products(in_skill_response.in_skill_products)
            if entitled_prods and len(entitled_prods) > 0:
                session_attr = handler_input.attributes_manager.session_attributes
                session_attr["paid_jokes"] = True
                handler_input.attributes_manager.session_attributes = session_attr
            if entitled_prods:
                speak_output = (
                    "Welcome to {}. You currently own {} products. "
                    "To hear a paid joke, say, 'Tell me a joke.").format(
                        skill_name,
                        get_speakable_list_of_products(entitled_prods))
            else:
                logger.info("No entitled products")
                speak_output = (
                    "Welcome to {}. To hear a joke you can say "
                    "'Tell me a joke', or to hear about the paid for jokes "
                    "for purchase, say 'What can I buy', or ask for help"
                ).format(skill_name)
            reprompt = "I didn't catch that. What can I help you with?"
        else:
            logger.info("Error calling InSkillProducts API: {}".format(
                in_skill_response.message))
            speak_output = "Something went wrong in loading your purchase history."
            reprompt = speak_output

        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )



class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        ask_output = "Here's a free joke: " + joke.freejokes() 
        speak_output = "Here's your free joke: " + joke.freejokes() + ". You can purchase more jokes, just say 'What can I buy'"
        session_attr = handler_input.attributes_manager.session_attributes
        if "paid_jokes" in session_attr:
            if session_attr["paid_jokes"] == True:
                speak_output = "Here's your paid joke: " +joke.paidjokes()

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


#sb = SkillBuilder()
sb = StandardSkillBuilder() 

sb.add_request_handler(TellMeMoreHandler())
sb.add_request_handler(BuyHandler())
sb.add_request_handler(BuyResponseHandler())
sb.add_request_handler(RefundPurchaseHandler())
sb.add_request_handler(CancelResponseHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()