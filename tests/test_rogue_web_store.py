# -*- coding: UTF-8 -*-

import os
import os.path
import json
import platform
import tempfile
import logging

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from rogue_scores.web import store
from rogue_scores.web.store import parse_text, Score, ScoresStore

class TestRogueStoreHelpers(unittest.TestCase):

    # == .parse_text == #

    def test_parse_text_killed_by_a_monster_old_version(self):
        self.assertEquals({'status': 'killed', 'cause': 'dragon', 'level': 24},
                          parse_text('killed by a dragon on level 24'))
        self.assertEquals({'status': 'killed', 'cause': 'vampire', 'level': 19},
                          parse_text('killed by a vampire on level 19'))
        self.assertEquals({'status': 'killed', 'cause': 'centaur', 'level': 8},
                          parse_text('killed by a centaur on level 8'))

    def test_parse_text_killed_by_a_monster_new_version(self):
        self.assertEquals({'status': 'killed', 'cause': 'hobgoblin', 'level': 1},
                          parse_text('killed on level 1 by a hobgoblin.'))

    def test_parse_text_quit_old_version(self):
        self.assertEquals({'status': 'quit', 'level': 9},
                          parse_text('quit on level 9'))

    def test_parse_text_quit_new_version(self):
        self.assertEquals({'status': 'quit', 'level': 1},
                          parse_text('quit on level 1.'))

    def test_parse_text_died_old_version(self):
        self.assertEquals({'status': 'died', 'cause': 'hypothermia', 'level': 6},
                          parse_text('died of hypothermia on level 6'))
        self.assertEquals({'status': 'died', 'cause': 'starvation', 'level': 5},
                          parse_text('died of starvation on level 5'))

    def test_parse_text_died_new_version(self):
        self.assertEquals({'status': 'died', 'cause': 'hypothermia', 'level': 3},
                          parse_text('killed on level 3 by hypothermia.'))


class TestRogueScore(unittest.TestCase):

    def setUp(self):
        self.s = Score()


    # == init == #

    def test_score_init(self):
        self.assertEquals(0, self.s.level)
        self.assertEquals(0, self.s.score)
        self.assertEquals(None, self.s.user)
        self.assertEquals(None, self.s.cause)
        self.assertEquals(None, self.s.status)

    def test_score_init_with_args(self):
        s = Score(user='foo', score=12)
        self.assertEquals(0, s.level)
        self.assertEquals(12, s.score)
        self.assertEquals('foo', s.user)
        self.assertEquals(None, s.cause)
        self.assertEquals(None, s.status)

    def test_score_init_with_args_more_attrs(self):
        s = Score(user='foo', score=12, foobar=45)
        self.assertEquals(45, s.foobar)

    # == .__int__ == #:

    def test_int_empty_score(self):
        self.assertEquals(0, int(self.s))

    def test_int(self):
        n = 43419
        self.assertEquals(n, int(Score(score=n)))

    # == .__eq__ == #

    def test_not_eq_other_type(self):
        self.assertNotEquals(self.s, 0)
        self.assertNotEquals(self.s, [])
        self.assertNotEquals(self.s, self.s.__dict__)

    def test_not_eq_other_score(self):
        self.assertNotEquals(Score(score=1), Score(score=3))

    def test_eq_empty_score(self):
        self.assertEquals(Score(), Score())

    def test_eq(self):
        self.assertEquals(Score(user='foo', score=2),
                          Score(score=2, user='foo'))

    # == .__gt__ == #

    def test_gt(self):
        self.assertTrue(Score(score=3) > Score(score=2))
        self.assertFalse(Score(score=3) > Score(score=3))
        self.assertFalse(Score(score=3) > Score(score=4))

    def test_gt_int(self):
        self.assertTrue(Score(score=42) > 17)

    # == .__ge__ == #

    def test_ge(self):
        self.assertTrue(Score(score=3) >= Score(score=2))
        self.assertTrue(Score(score=3) >= Score(score=3))
        self.assertFalse(Score(score=3) >= Score(score=4))

    # == .__lt__ == #

    def test_lt(self):
        self.assertFalse(Score(score=3) < Score(score=2))
        self.assertFalse(Score(score=3) < Score(score=3))
        self.assertTrue(Score(score=3) < Score(score=4))

    # == .__le__ == #

    def test_lt(self):
        self.assertFalse(Score(score=3) <= Score(score=2))
        self.assertTrue(Score(score=3) <= Score(score=3))
        self.assertTrue(Score(score=3) <= Score(score=4))

    # == .__getitem__ == #

    def test_getitem(self):
        n = 42
        self.s.foo = n
        self.assertEquals(n, self.s['foo'])

    # == .__repr__ == #

    def test_repr_empty(self):
        self.assertEquals('Score(%s)' % str(self.s.__dict__), repr(self.s))


class TestRogueScoresStore(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.scores = self.tmp.name
        self.store = ScoresStore(self.scores)

    def tearDown(self):
        if os.path.isfile(self.scores):
            os.unlink(self.scores)


# 
# 
#     # == .init_scores == #
# 
#     def test_init_scores_with_dir_without_file(self):
#         os.unlink(self.scores)
#         self.assertFalse(os.path.isfile(self.scores))
#         init_scores(self.scores)
#         self.assertTrue(os.path.isfile(self.scores))
#         with open(self.scores) as f:
#             self.assertEquals('[]', f.read())
# 
#     def test_init_scores_with_dir_with_file(self):
#         s = 's$@%r9'
#         with open(self.scores, 'w') as f:
#             f.write(s)
#         init_scores(self.scores)
#         with open(self.scores) as f:
#             self.assertEquals(s, f.read())
# 
#     def test_init_scores_without_dir(self):
#         path = tempfile.mkdtemp()
#         os.rmdir(path)
#         self.assertFalse(os.path.exists(path))
#         name = '%s/scores' % path
#         init_scores(name)
#         self.assertTrue(os.path.isdir(path))
#         self.assertTrue(os.path.isfile(name))
#         with open(name) as f:
#             self.assertEquals('[]', f.read())
# 
#     # == .sanitize_score == #
# 
#     def test_sanitize_score_wrong_types(self):
#         self.assertSequenceEqual(('12', 0, '25'),
#                                  sanitize_score((12, None, 25)))
#         self.assertSequenceEqual(('', 0, 'foo'),
#                                  sanitize_score(({}, 'hello', ['foo'])))
# 
#     def test_sanitize_score_special_chars(self):
#         self.assertSequenceEqual(('fooc', 25, 'killed.'),
#                                  sanitize_score(('foo@c', 25, 'killed<.$@')))
# 
#     def test_sanitize_score(self):
#         self.assertSequenceEqual(('foo', 25, 'killed.'),
#                                  sanitize_score(('foo', 25, 'killed.')))
# 
#     # == .sanitize_scores == #
# 
#     def test_sanitize_scores_empty_list(self):
#         self.assertSequenceEqual([], sanitize_scores([]))
# 
#     def test_sanitize_scores_remove_null_scores(self):
#         self.assertSequenceEqual([], sanitize_scores([('foo', 0, 'bar')]))
# 
#     def test_sanitize_scores_remove_negative_scores(self):
#         self.assertSequenceEqual([], sanitize_scores([('foo', -3, 'bar')]))
# 
#     def test_sanitize_scores_remove_empty_usernames(self):
#         self.assertSequenceEqual([], sanitize_scores([('', 42, 'bar')]))
# 
#     def test_sanitize_scores_remove_bad_usernames(self):
#         self.assertSequenceEqual([], sanitize_scores([('$@', 42, 'bar')]))
# 
#     def test_sanitize_scores(self):
#         self.assertSequenceEqual([('a', 42, 'b')],
#                                  sanitize_scores([('a', 42, 'b')]))
# 
# 
# class TestRogueWebScoresMerging(unittest.TestCase):
# 
#     def setUp(self):
#         self.tmp = tempfile.NamedTemporaryFile(delete=False)
#         self.scores = self.tmp.name
#         self.tmp.write(json.dumps([
#             ['foo', 42, 'bar'],
#             ['foo', 41, 'qux'],
#             ['foo', 41, 'qax'],
#             ['moo', 25, 'qwe']
#         ]).encode('utf-8'))
#         self.tmp.close()
# 
#     def tearDown(self):
#         if os.path.isfile(self.scores):
#             os.unlink(self.scores)
# 
#     def getScores(self):
#         with open(self.scores) as f:
#             return json.loads(f.read())
# 
#     # == .merge_scores == #
# 
#     def test_merge_scores_create_file(self):
#         os.unlink(self.scores)
#         merge_scores([], self.scores)
#         self.assertTrue(os.path.isfile(self.scores))
# 
#     def test_merge_scores_empty_list(self):
#         initial = self.getScores()
#         merge_scores([], self.scores)
#         self.assertSequenceEqual(initial, self.getScores())
# 
#     def test_merge_scores_wrong_scores(self):
#         initial = self.getScores()
#         merge_scores([
#             ('@$', 300, 'lolz'),
#             ('me', -50, 'im a hackerz'),
#         ], self.scores)
#         self.assertSequenceEqual(initial, self.getScores())
# 
#     def test_merge_scores_no_duplicates(self):
#         initial = self.getScores()
#         merge_scores([('foo', 42, 'bar')], self.scores)
#         self.assertSequenceEqual(initial, self.getScores())
# 
#     def test_merge_scores_at_the_end(self):
#         initial = self.getScores()
#         merge_scores([('foo', 1, 'bar')], self.scores)
#         self.assertSequenceEqual(['foo', 1, 'bar'], self.getScores()[-1])
# 
#     def test_merge_scores_same_user_score_but_different_text(self):
#         initial = self.getScores()
#         merge_scores([('foo', 42, 'barz')], self.scores)
#         scs = self.getScores()
#         self.assertSequenceEqual(['foo', 42, 'bar'], scs[0])
#         self.assertSequenceEqual(['foo', 42, 'barz'], scs[1])
# 
#     def test_merge_scores(self):
#         initial = self.getScores()
#         merge_scores([('wxs', 35, 'zzz')], self.scores)
#         scs = self.getScores()
#         self.assertSequenceEqual(['wxs', 35, 'zzz'], scs[3])
