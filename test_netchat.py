import unittest
from types import SimpleNamespace
from unittest.mock import patch
from netchat import load_page, retrieve, answer_question, validate_url

PAGE = {'url': 'https://example.com', 'title': 'Example', 'text': 'Example content', 'chunks': ['The rocket launches in October from Florida.', 'The garden grows roses and tulips.']}

class BackendTests(unittest.TestCase):
    def test_retrieval_and_followup(self):
        self.assertIn('rocket', retrieve(PAGE['chunks'], 'When does the rocket launch?', [])[0])
        self.assertIn('rocket', retrieve(PAGE['chunks'], 'Where?', [{'role': 'user', 'content': 'When does the rocket launch?'}])[0])

    def test_invalid_and_private_urls(self):
        for url in ['file:///etc/passwd', 'hello', 'http://127.0.0.1', 'http://[::1]']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url)

    def test_page_extraction(self):
        response = SimpleNamespace(is_redirect=False, headers={'Content-Type': 'text/html'}, raise_for_status=lambda: None,
            iter_content=lambda size: [b'<title>Rocket</title><nav>Noise</nav><main>The rocket launches in October from Florida. Tickets open in September.</main><script>bad()</script>'])
        with patch('netchat.validate_url'), patch('netchat.requests.get') as get:
            get.return_value.__enter__.return_value = response
            page = load_page('https://example.com')
        self.assertEqual(page['title'], 'Rocket')
        self.assertNotIn('Noise', page['text'])
        self.assertNotIn('bad()', page['text'])

    def test_answer_context_history_and_sources(self):
        client = SimpleNamespace(chat_completion=lambda **kwargs: SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='October [1]'))]))
        answer, sources = answer_question(PAGE, 'When?', [], 'test', 'test', client=client)
        self.assertEqual(answer, 'October [1]')
        self.assertEqual(len(sources), 2)

    def test_empty_answer_fails(self):
        client = SimpleNamespace(chat_completion=lambda **kwargs: SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=None))]))
        with self.assertRaises(ValueError):
            answer_question(PAGE, 'When?', [], 'test', 'test', client=client)

class AppTests(unittest.TestCase):
    def test_startup_and_page_switch(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file('app.py').run(timeout=30)
        self.assertEqual(len(at.exception), 0)
        with patch('netchat.load_page', return_value=PAGE):
            at.text_input[-1].set_value('https://example.com')
            next(b for b in at.button if b.label == 'Load webpage').click().run()
        self.assertEqual(at.session_state.page['title'], 'Example')
        at.session_state.messages = [{'role': 'user', 'content': 'Old question'}]
        newer = dict(PAGE, title='New page', url='https://example.org')
        with patch('netchat.load_page', return_value=newer):
            at.text_input[-1].set_value('https://example.org')
            next(b for b in at.button if b.label == 'Load webpage').click().run()
        self.assertEqual(at.session_state.page['title'], 'New page')
        self.assertEqual(at.session_state.messages, [])
        self.assertEqual(len(at.exception), 0)

    def test_model_failure_can_be_retried(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file('app.py')
        at.secrets['HF_TOKEN'] = 'test-token'
        at.session_state.page = PAGE
        at.run(timeout=30)
        with patch('netchat.answer_question', side_effect=RuntimeError('provider failed')):
            at.chat_input[0].set_value('When is launch?').run()
        self.assertEqual(at.session_state.messages, [])
        self.assertEqual(len(at.error), 1)
        with patch('netchat.answer_question', return_value=('October [1]', PAGE['chunks'])):
            at.chat_input[0].set_value('When is launch?').run()
        self.assertEqual(at.session_state.messages[-1]['content'], 'October [1]')
        self.assertEqual(len(at.exception), 0)

if __name__ == '__main__':
    unittest.main()
