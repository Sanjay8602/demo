import streamlit as st
from unify import Unify

st.set_page_config(page_title="Debate App built with Unify")


def start_interaction():
    st.session_state.continue_interaction = True


def stop_interaction():
    st.session_state.continue_interaction = False


def clear_history():
    st.session_state.continue_interaction = False
    st.session_state.model1_messages = []
    st.session_state.model2_messages = []

endpoints = ["llama-2-13b-chat@anyscale", "mistral-7b-instruct-v0.1@deepinfra", "gpt-4@deepinfra", "codellama-7b-instruct@octoai",
             "gpt-3.5-turbo@openai", "pplx-70b-chat@perplexity-ai", "llama-3-8b-chat@together-ai", "gemma-2b-it@together-ai", "gpt-4-turbo@openai",
             "deepseek-coder-33b-instruct@together-ai", "mistral-large@mistral-ai", "llama-3-8b-chat@fireworks-ai"]

def input_fields():
    with st.sidebar:
        st.session_state.unify_key = st.text_input("UNIFY KEY", type="password")
        st.image("robot_icon_green.png", width=20)
        st.session_state.llm_1 = st.selectbox(
            "Select LLM to debate supporting the topic",
            endpoints,
            key="endpoints_1_llm",
            
        )
        personas = ["factual", "funny", "silly", "serious", "angry"]
        st.session_state.llm_1_persona = st.selectbox(
            "Select the LLMs persona",
            personas,
            key="llm1_persona"
        )
        
        st.image("robot_icon_yellow.png", width=20)
        st.session_state.llm_2 = st.selectbox(
            "Select LLM to debate opposing the topic",
            endpoints,
            key= "endpoints_2_llm",
            
        )
        
        st.session_state.llm_2_persona = st.selectbox(
            "Select the LLMs persona",
            personas,
            key="llm2_persona"
        )
        # Initialize stop button
        if st.button("Stop debate", help="stop the debate at "
                                         "the last complete "
                                         "reply-response "
                                         "cycle"):
            stop_interaction()
        else:
            pass

        # Clear history
        if st.button("Clear chat history"):
            clear_history()
        else:
            pass


def initialize_model(llm_endpoint, unify_key):
    model = Unify(
        api_key=unify_key,
        endpoint=llm_endpoint
    )
    return model


# Function to generate response from a model given a prompt
def generate_response(model, topic, position, persona, prompt):
    messages = [
        {"role": "system", "content": f"You are debating {position} the following topic: {topic}. "
                                      f"Consider the opposing points and provide a response. "
                                      f"Adopt a {persona} persona when responding."},
    ]
    messages.extend(prompt)
    return model.generate(messages=messages, stream=True)


def main():
    st.title("Debate App built with Unify")
    st.text("Choose two LLMs to debate each other on a given topic.")

    input_fields()

    if 'continue_interaction' not in st.session_state:
        st.session_state.continue_interaction = True

    if "model1_messages" not in st.session_state:
        st.session_state.model1_messages = []

    if "model2_messages" not in st.session_state:
        st.session_state.model2_messages = []

    with st.form(key='my_form'):
        topic = st.text_input(label='Enter the debate topic here:')
        submit = st.form_submit_button(label='Start debate')

    if len(st.session_state.model1_messages) > 0 and len(st.session_state.model2_messages) > 0:
        for _i, (model1_message, model2_message) in enumerate(
                zip(st.session_state.model1_messages, st.session_state.model2_messages)):
            with st.chat_message(name="model1", avatar="robot_icon_green.png"):
                st.write(model1_message)
            with st.chat_message(name="model2", avatar="robot_icon_yellow.png"):
                st.write(model2_message)

    model1 = initialize_model(st.session_state.llm_1, st.session_state.unify_key)
    model2 = initialize_model(st.session_state.llm_2, st.session_state.unify_key)
    if submit:
        st.session_state.continue_interaction = True
        model1_messages = []
        model2_messages = []
        while st.session_state.continue_interaction:
            with st.chat_message(name="model1", avatar="robot_icon_green.png"):
                if len(model1_messages) == 0:
                    stream = generate_response(model1, topic, "for", st.session_state.llm_1_persona,
                                               [{"role": "user", "content": "start debate."}])
                else:
                    model1_messages.append({"role": "user", "content": model2_response})
                    stream = generate_response(model1, topic, "for", st.session_state.llm_1_persona, model1_messages)
                model1_response = st.write_stream(stream)
            model1_messages.append({"role": "assistant", "content": model1_response})
            st.session_state.model1_messages.append(model1_response)

            with st.chat_message(name="model2", avatar="robot_icon_yellow.png"):
                model2_messages.append({"role": "user", "content": model1_response})
                stream = generate_response(model2, topic, "against", st.session_state.llm_2_persona, model2_messages)
                model2_response = st.write_stream(stream)
            model2_messages.append({"role": "assistant", "content": model2_response})
            st.session_state.model2_messages.append(model2_response)


if __name__ == "__main__":
    main()
