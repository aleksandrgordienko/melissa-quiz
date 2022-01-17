from behave import given, when, then
import os
import sys
import json
sys.path.append('..')
from src.texts import Texts


@given('a Texts instance')
def step_impl(context):
    context.texts_obj = Texts()


@when('loading language files')
def step_impl(context):
    context.dicts = {}
    for file_name in [x for x in os.listdir('language/') if x.endswith('.json')]:
        with open(f'language/{file_name}') as json_file:
            context.dicts[file_name[0:2]] = json.loads(json_file.read())


@when('invoking get_text() for each key')
def step_impl(context):
    context.get_texts = {}
    for lang, texts in context.dicts.items():
        context.get_texts[lang] = {}
        for key in texts:
            context.get_texts[lang][key] = context.texts_obj.get_text(text_id=key, lang=lang)


@then('the values are the same as in JSON files')
def step_impl(context):
    for lang, texts in context.dicts.items():
        for key, value in texts.items():
            got_value = context.get_texts[lang][key]
            assert value == got_value


@when('invoking check_bad()')
def step_impl(context):
    context.words = {'bad': {}, 'good': {}}
    for lang, texts in context.dicts.items():
        context.words['bad'][lang] = []
        context.words['good'][lang] = []
        for key, value in texts.items():
            if key == 'bad_words':
                context.words['bad'][lang] += value.split()
            else:
                context.words['good'][lang] += value.split()


@when('with {words_type} words')
def step_impl(context, words_type):
    context.results = {}
    for lang, words in context.words[words_type].items():
        context.results[lang] = []
        for word in words:
            context.results[lang].append(context.texts_obj.check_bad(word, lang=lang))


@then('{value_type} returned for each word')
def step_impl(context, value_type):
    for lang_results in context.results.values():
        for result in lang_results:
            assert str(result) == value_type


@when('invoking get_joke()')
def step_impl(context):
    context.rand_jokes = {}
    for lang in context.dicts.keys():
        context.rand_jokes[lang] = context.texts_obj.get_joke(lang=lang)
    context.rand_jokes['default'] = context.texts_obj.get_joke(lang='en')


@then('jokes returned from texts')
def step_impl(context):
    for lang in context.dicts.keys():
        if lang == 'default':
            assert context.rand_jokes[lang] in context.dicts['en']['jokes']
        else:
            assert context.rand_jokes[lang] in context.dicts[lang]['jokes']
