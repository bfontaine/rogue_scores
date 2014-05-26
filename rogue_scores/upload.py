# -*- coding: UTF-8 -*-

import json
import requests

def post_scores(scores, **kwargs):
    """
    Post some scores to a remote server. Optional keyword arguments are:

    Keyword arguments:
            - ``protocol`` (``string``, default: ``http``)
            - ``target`` (``string``, default: ``localhost:5000/scores``)
    """
    url = '%s://%s' % (kwargs.get('protocol', 'http'),
                       kwargs.get('target', 'localhost:5000/scores'))

    payload = {'scores': json.dumps(scores)}
    r = requests.post(url, data=payload)
    return r.text
