# -*- coding: UTF-8 -*-

import json
import requests

def post_scores(scores, **kwargs):
    """
    Post some scores to a remote server and return a boolean depending on the
    request's success. Optional keyword arguments are:

    Keyword arguments:
            - ``protocol`` (``string``, default: ``http``)
            - ``target`` (``string``, default: ``localhost:5000``)
    """
    url = u'%s://%s/scores' % (kwargs.get('protocol', 'http'),
                               kwargs.get('target', 'localhost:5000'))

    payload = {'scores': json.dumps(scores)}
    try:
        r = requests.post(url, data=payload)
    except requests.exceptions.ConnectionError:
        return False

    try:
        return r.status_code == 200 and r.text.strip() == 'ok'
    except ValueError:
        return False