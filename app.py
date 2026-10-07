"""Chat with a webpage using retrieval-augmented generation."""
import os
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import get_token
from netchat import load_page, answer_question

load_dotenv()
st.set_page_config(page_title='NetChat', page_icon='🐦')
st.title('NetChat 🐦')
st.caption('Load a webpage, then ask questions about its content.')

def setting(name, default=''):
    try:
        return os.getenv(name) or st.secrets.get(name, default)
    except FileNotFoundError:
        return os.getenv(name, default)

with st.sidebar:
    st.header('Connection')
    token = st.text_input('Hugging Face token', value=setting('HF_TOKEN') or get_token() or setting('HUGGINGFACEHUB_API_TOKEN'),
                          type='password', help='Uses your local Hugging Face login when available. You can override it with an Inference Providers token.')
    model = st.text_input('Model', value=setting('HF_MODEL', 'meta-llama/Llama-3.1-8B-Instruct'))
    st.caption('Hosted inference requires an authorized token and available provider quota.')
    if st.button('Clear conversation'):
        st.session_state.messages = []

with st.form('load_page'):
    url = st.text_input('Website URL', placeholder='https://example.com/article')
    submitted = st.form_submit_button('Load webpage')
if submitted:
    try:
        with st.spinner('Reading webpage…'):
            page = load_page(url)
        st.session_state.page = page
        st.session_state.messages = []
    except Exception as exc:
        st.error(f'Could not load this webpage: {exc}')
page = st.session_state.get('page')
if not page:
    st.info('Enter a public webpage URL to begin.')
else:
    st.success(f"Loaded: {page['title']}")
    st.caption(f"Active source: {page['url']}")
    with st.expander('Page preview'):
        st.write(page['text'][:3000])
    messages = st.session_state.setdefault('messages', [])
    for message in messages:
        with st.chat_message(message['role']):
            st.write(message['content'])
            if message.get('sources'):
                with st.expander('Source passages'):
                    for passage in message['sources']:
                        st.write(passage)
    question = st.chat_input('Ask about this webpage', disabled=not bool(token))
    if not token:
        st.info('Add your Hugging Face token in the sidebar to enable answers.')
    if question:
        try:
            with st.spinner('Finding an answer…'):
                answer, passages = answer_question(page, question, messages, token, model)
            messages.extend([{'role': 'user', 'content': question}, {'role': 'assistant', 'content': answer, 'sources': passages}])
            st.rerun()
        except Exception:
            st.error("The model request failed. Check your token's Inference Providers permission, model availability, and provider quota, then retry.")
