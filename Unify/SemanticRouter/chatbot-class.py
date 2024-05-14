# -*- coding: utf-8 -*-
"""ChatBot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JPeQACy6WbFueBAfyDe5vm0-a2pUm6Qh

#Build a ChatBot

In this notebook, we will build an interactive chatbot using the `unifyai` python package.

Under the hood, chatbots are very simple to implement. All LLM endpoints are stateless, and therefore the entire conversation history is repeatedly fed as input to the model. All that is required of the local agent is to store this history, and correctly pass it to the model.

#### Install Dependencies

To run this notebook, you will need to install the `unifyai` [python package](https://pypi.org/project/unifyai/). You can do so by running the cell below ⬇️
"""


"""#### The Agent

We define a simple chatbot class below, with the only public function being `run`. Before starting, you should to obtain a UNIFY key from the [console page](https://console.unify.ai/login?callbackUrl=%2F) and assign it to the `UNIFY_KEY` variable below.
"""

from unify import ChatBot
from unify import Unify
from typing import Optional
import sys
UNIFY_KEY = '7wTNz+iEWsWIEdvuCtLR8ov1tjnHkUFfcwE5wLR3YWM='
# pip install Unify

# chatbot class


class ChatBot:
    """Agent class represents an LLM chat agent."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> None:
        """
        Initializes the ChatBot object.

        Args:
            api_key (str, optional): API key for accessing the Unify API.
                If None, it attempts to retrieve the API key from the
                environment variable UNIFY_KEY.
                Defaults to None.

            endpoint (str, optional): Endpoint name in OpenAI API format:
                <uploaded_by>/<model_name>@<provider_name>
                Defaults to None.

            model (str, optional): Name of the model. If None,
            endpoint must be provided.

            provider (str, optional): Name of the provider. If None,
            endpoint must be provided.
        Raises:
            UnifyError: If the API key is missing.
        """
        self._message_history = []
        self._paused = False
        self._client = Unify(
            api_key=api_key,
            endpoint=endpoint,
            model=model,
            provider=provider,
        )

    @property
    def client(self) -> str:
        """
        Get the client object.

        Returns:
            str: The model name.
        """
        return self._client

    def set_client(self, value: Unify) -> None:
        """
        Set the model name.

        Args:
            value: The unify client.
        """
        self._client = value

    @property
    def model(self) -> str:
        """
        Get the model name.

        Returns:
            str: The model name.
        """
        return self._client.model

    def set_model(self, value: str) -> None:
        """
        Set the model name.

        Args:
            value (str): The model name.
        """
        self._client.set_model(value)
        if self._client.provider:
            self._client.set_endpoint("@".join([value, self._client.provider]))
        else:
            mode = self._client.endpoint.split("@")[1]
            self._client.set_endpoint("@".join([value, mode]))

    @property
    def provider(self) -> Optional[str]:
        """
        Get the provider name.

        Returns:
            str: The provider name.
        """
        return self._client.provider

    def set_provider(self, value: str) -> None:
        """
        Set the provider name.

        Args:
            value (str): The provider name.
        """
        self._client.set_provider(value)
        self._client.set_endpoint("@".join([self._model, value]))

    @property
    def endpoint(self) -> str:
        """
        Get the endpoint name.

        Returns:
            str: The endpoint name.
        """
        return self._client.endpoint

    def set_endpoint(self, value: str) -> None:
        """
        Set the model name.

        Args:
            value (str): The endpoint name.
        """
        self._client.set_endpoint(value)
        self._client.set_model(value.split("@")[0])
        self._client.set_provider(value.split("@")[1])

    def _get_credits(self):
        """
        Retrieves the current credit balance from associated with the UNIFY account.

        Returns:
            float: Current credit balance.
        """
        return self._client.get_credit_balance()

    def _process_input(self, inp: str, show_credits: bool, show_provider: bool):
        """
        Processes the user input to generate AI response.

        Args:
            inp (str): User input message.
            show_credits (bool): Whether to show credit consumption.
            show_credits (bool): Whether to show provider used.

        Yields:
            str: Generated AI response chunks.
        """
        self._update_message_history(role="user", content=inp)
        initial_credit_balance = self._get_credits()
        stream = self._client.generate(
            messages=self._message_history,
            stream=True,
        )
        words = ""
        for chunk in stream:
            words += chunk
            yield chunk

        self._update_message_history(
            role="assistant",
            content=words,
        )
        final_credit_balance = self._get_credits()
        if show_credits:
            sys.stdout.write(
                "\n(spent {:.6f} credits)".format(
                    initial_credit_balance - final_credit_balance,
                ),
            )
        if show_provider:
            sys.stdout.write("\n(provider: {})".format(self._client.provider))

    def _update_message_history(self, role: str, content: str):
        """
        Updates message history with user input.

        Args:
            role (str): Either "assistant" or "user".
            content (str): User input message.
        """
        self._message_history.append(
            {
                "role": role,
                "content": content,
            },
        )

    def clear_chat_history(self):
        """Clears the chat history."""
        self._message_history.clear()

    def run(self, show_credits: bool = False, show_provider: bool = False):
        """
        Starts the chat interaction loop.

        Args:
            show_credits (bool, optional): Whether to show credit consumption.
            Defaults to False.
            show_provider (bool, optional): Whether to show the provider used.
            Defaults to False.
        """
        if not self._paused:
            sys.stdout.write(
                "Let's have a chat. (Enter `pause` to pause and `quit` to exit)\n",
            )
            self.clear_chat_history()
        else:
            sys.stdout.write(
                "Welcome back! (Remember, enter `pause` to pause and `quit` to exit)\n",
            )
        self._paused = False
        while True:
            sys.stdout.write("> ")
            inp = input()
            if inp == "quit":
                self.clear_chat_history()
                break
            elif inp == "pause":
                self._paused = True
                break
            for word in self._process_input(inp, show_credits, show_provider):
                sys.stdout.write(word)
                sys.stdout.flush()
            sys.stdout.write("\n")


"""#### Let's Chat

Now, we can instantiate and chat with this agent. For this demo, we'll utilize the `llama-2-7b-chat` model from `anyscale`. However, you have the flexibility to select any model and provider from our supported options on the [benchmarks interface](https://unify.ai/hub).
"""

agent = ChatBot(api_key=UNIFY_KEY,
                endpoint="llama-2-13b-chat@lowest-input-cost")
agent.run()

"""You can also see how many credits your prompt used. This option is set in the constructor, but it can be overwritten during the run command. When enabled, each response from the chatbot will then be appended with the credits spent:


"""

agent.run(show_credits=True)

"""Finally, you can switch providers half-way through the conversation easily. This can be useful to handle prompt of varying complexity.

For example we can start with a small model for answering simple questions, such as recalling facts, and then move to a larger model for a more complex task, such as creative writing.
"""

agent = ChatBot(api_key=UNIFY_KEY,
                endpoint="llama-2-13b-chat@lowest-input-cost")
agent.run(show_credits=True)

agent.set_endpoint("gpt-4-turbo@openai")
agent.run(show_credits=True)

"""Switching between providers mid-conversation makes it much easier to maximize quality and runtime performance based on the latest metrics, and also save on costs!

In fact, you can automatically optimize for a metric of your choice with our [dynamic routing modes](https://unify.ai/docs/hub/concepts/runtime_routing.html#available-modes). For example, you can optimize for speed as follows:
"""

agent.set_endpoint("llama-2-70b-chat@highest-tks-per-sec")
agent.run(show_provider=True)

"""The flag `show_provider` ensures that the specific provider is printed at the end of each response. For example, sometimes `anyscale` might be the fastest, and at other times it might be `together-ai` or `fireworks-ai`. This flag enables you to keep track of what provider is being used under the hood.

If the task is to summarize a document or your chat history grows, typically the input-cost becomes the primary cost driver. You can use our `lowest-input-cost` mode to direct queries to the provider with the lowest input cost automatically.
"""

agent = ChatBot(api_key=UNIFY_KEY,
                endpoint="llama-2-13b-chat@lowest-input-cost")
agent.run(show_provider=True)

"""# Python Package

The python package already contains the `ChatBot` agent and you may use it directly as follows:
"""

chatbot = ChatBot(api_key=UNIFY_KEY,
                  endpoint="llama-2-13b-chat@lowest-input-cost")
chatbot.run()

"""#Round Up
 Congratulations! 🚀 You are now capable of building ChatBot Agents for your application using our LLM endpoints. If you're a contributor and want to earn a cool badge, you should fill out this [form](https://docs.google.com/forms/d/e/1FAIpQLSdTd0U5czFNY3aNFHHbjizd4a9gz-oTINMrHMnopOgZzajs9g/viewform?usp=sf_link) which contains a few quiz questions about the concepts you learnt in this tutorial. Happy
"""
