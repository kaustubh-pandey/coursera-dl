# -*- coding: utf-8 -*-

"""
Test the utility functions.
"""
import datetime
import os
import pytest
import random
from time import time

import requests
import six

from mock import Mock
from coursera import utils
from coursera import coursera_dl


def assertEqual(a, b):
    assert a == b


def assertEquals(a, b):
    assert a == b


def assertTrue(stmt):
    assert stmt


def assertFalse(stmt):
    assert not stmt


def assertRaises(e, f, *a, **kw):
    pytest.raises(e, f, *a, **kw)


def test_clean_filename():
    strings = {
        '(23:90)': '23-90',
        '(:': '-',
        'a téest &and a@noòtheèr': 'a_test_and_another',
        'Lecture 2.7 - Evaluation and Operators (16:25)':
        'Lecture_2.7_-_Evaluation_and_Operators_16-25',
        'Week 3: Data and Abstraction':
        'Week_3-_Data_and_Abstraction',
        '  (Week 1) BRANDING:  Marketing Strategy and Brand Positioning':
        'Week_1_BRANDING-__Marketing_Strategy_and_Brand_Positioning',
        'test &amp; &quot; adfas': 'test___adfas',
        '&nbsp;': ''
    }
    for k, v in six.iteritems(strings):
        actual_res = utils.clean_filename(k)
        assert actual_res == v


def test_clean_filename_minimal_change():
    strings = {
        '(23:90)': '(23-90)',
        '(:': '(-',
        'a téest &and a@noòtheèr': 'a téest &and a@noòtheèr',
        'Lecture 2.7 - Evaluation and Operators (16:25)':
        'Lecture 2.7 - Evaluation and Operators (16-25)',
        'Week 3: Data and Abstraction':
        'Week 3- Data and Abstraction',
        '  (Week 1) BRANDING:  Marketing Strategy and Brand Positioning':
        '  (Week 1) BRANDING-  Marketing Strategy and Brand Positioning',
        'test &amp; &quot; adfas': 'test & " adfas',
        '&nbsp;': u'\xa0'
    }
    for k, v in six.iteritems(strings):
        actual_res = utils.clean_filename(k, minimal_change=True)
        assert actual_res == v


def test_get_anchor_format():
    strings = {
        'https://class.coursera.org/sub?q=123_en&format=txt': 'txt',
        'https://class.coursera.org/sub?q=123_en&format=srt': 'srt',
        'https://d396qusza40orc.cloudfront.net/week7-4.pdf': 'pdf',
        'https://class.coursera.org/download.mp4?lecture_id=123': 'mp4'
    }
    for k, v in six.iteritems(strings):
        assertEquals(utils.get_anchor_format(k), v)


def test_random_string():
    random.seed(0)  # set seed for reproducible tests

    res = utils.random_string(8)
    assertEqual(len(res), 8)

    # Python 2 and Python 3 use different strategies for generation of
    # PRNG, according to the documentation available at
    # https://docs.python.org/3.4/library/random.html#random.seed
    if six.PY2:
        assertEqual(res, '0UAqFzWs')
    else:
        assertEqual(res, '2yW4Acq9')


def test_fix_url_ads_sheme():
    url = "www.coursera.org"
    assertEquals(utils.fix_url(url), 'http://www.coursera.org')


def test_fix_url_removes_sheme():
    url = " www.coursera.org "
    assert utils.fix_url(url) == 'http://www.coursera.org'


def test_format_combine_resource_works_correctly():
    rv = coursera_dl.format_combine_number_resource(5, 4, "Moving_the_furniture", 'The_Basics', "mp4")
    assert '05_04_Moving_the_furniture_The_Basics.mp4' == rv


def test_format_combine_resource_works_correctly_without_title():
    rv = coursera_dl.format_combine_number_resource(5, 1, "Introduction", '', "mp4")
    assert '05_01_Introduction.mp4' == rv


def test_format_resource_works_correctly():
    rv = coursera_dl.format_resource(2, "Washing", "Dishes", "mp9")
    assert '02_Washing_Dishes.mp9' == rv


def test_format_resource_works_correctly_without_title():
    rv = coursera_dl.format_resource(1, "Introduction", '', "mp2")
    assert '01_Introduction.mp2' == rv


def test_format_section_works_correctly():
    rv = coursera_dl.format_section(9, 'bob', 'WEAVING', False)
    assert '09_bob' == rv


def test_format_section_works_correctly_with_verbose():
    rv = coursera_dl.format_section(9, 'bill', 'WEAVING', True)
    assert 'WEAVING_09_bill' == rv


def test_fix_url_doesnt_alters_empty_url():
    url = None
    assert utils.fix_url(url) is None

    url = ""
    assert utils.fix_url(url) == ""


def test_decode_input():
    encoded_inputs = [
        str("/home/user/темп"),
        str("22少女時代22")]

    for encoded_input in encoded_inputs:
        decoded_input = utils.decode_input(encoded_input)
        assert isinstance(decoded_input, six.text_type), "Decoded input is not a text type."


def test_total_seconds():
    ts = coursera_dl.total_seconds(datetime.timedelta(days=30))
    assert ts == 2592000


def test_is_course_complete_should_give_false_if_there_was_recent_update():

    delta = coursera_dl.total_seconds(datetime.timedelta(days=29))
    tm = time() - delta

    rv = coursera_dl.is_course_complete(tm)
    assertFalse(rv)


def test_is_course_complete_should_give_true_if_there_was_no_recent_update():

    delta = coursera_dl.total_seconds(datetime.timedelta(days=31))
    tm = time() - delta

    rv = coursera_dl.is_course_complete(tm)
    assertTrue(rv)


def test_correct_formatting_of_class_URL():

    url = coursera_dl.get_syllabus_url('bob', False)
    assert 'https://class.coursera.org/bob/lecture/index' == url


def test_correct_formatting_of_class_with_preview_URL():

    url = coursera_dl.get_syllabus_url('bill', True)
    assert 'https://class.coursera.org/bill/lecture/preview' == url


def test_parse_args():
    args = coursera_dl.parseArgs(['-u', 'bob', '-p', 'bill', 'posa-001'])

    assert args.about is False
    assert args.class_names == ['posa-001']
    assert args.username == 'bob'
    assert args.password == 'bill'


def get_mock_session(page_text):
    page_obj = Mock()
    page_obj.text = page_text
    page_obj.raise_for_status = Mock()
    session = requests.Session()
    session.get = Mock(return_value=page_obj)
    return page_obj, session


def test_get_page():
    page_obj, session = get_mock_session('<page/>')

    p = coursera_dl.get_page(session, 'http://www.not.here')

    session.get.assert_called_once_with('http://www.not.here')
    page_obj.raise_for_status.assert_called_once()
    assert p == '<page/>'


def test_grab_hidden_video_url():
    filename = os.path.join(
        os.path.dirname(__file__), "fixtures", "html",
        "hidden-videos_2.html")

    page_text = open(filename).read()
    page_obj, session = get_mock_session(page_text)
    p = coursera_dl.grab_hidden_video_url(session,
                                          'http://www.hidden.video')
    assert 'video1.mp4' == p
