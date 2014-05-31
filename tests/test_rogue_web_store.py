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
from rogue_scores.web.store import parse_text, Score, ScoresStore, \
    BadScoreFormatException

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

    def test_parse_text_won(self):
        # I don't know what the winning text looks like
        self.assertEquals({'status': 'won'}, parse_text('won ...'))


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

    def test_lt_int(self):
        self.assertTrue(Score(score=3) < 4)

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
        with open(self.scores, 'w') as f:
            f.write(json.dumps([]))

        self.store = ScoresStore(self.scores)

    def tearDown(self):
        self.rmScores()

    def getScores(self):
        with open(self.scores) as f:
            return json.loads(f.read())

    def setScores(self, scs):
        with open(self.scores, 'w') as f:
            f.write(json.dumps(scs))

    def rmScores(self):
        if os.path.isfile(self.scores):
            os.unlink(self.scores)

    # == .__init__ == #

    def test_init_with_no_path(self):
        s = ScoresStore(path=None)
        self.assertEquals(None, s.path)
        self.assertSequenceEqual([], s.scores)

    def test_init_with_no_file(self):
        self.rmScores()
        s = ScoresStore(self.scores)
        self.assertTrue(os.path.isfile(self.scores))
        self.assertSequenceEqual([], self.getScores())

    def test_init_without_dir(self):
        path = tempfile.mkdtemp()
        os.rmdir(path)
        self.assertFalse(os.path.exists(path))
        name = '%s/scores' % path
        s = ScoresStore(name)
        self.assertTrue(os.path.isdir(path))
        self.assertTrue(os.path.isfile(name))
        self.assertSequenceEqual([], self.getScores())

    # == .json == #

    def test_empty_json(self):
        self.assertEquals(json.dumps([]), self.store.json())

    def test_json(self):
        s = Score()
        s.__dict__ = {'user': 'foo', 'level': 12}
        self.store.scores = [s]

        self.assertEquals(json.dumps([s.__dict__]), self.store.json())

    # == ._load == #

    def test_load_scores_no_path(self):
        try:
            self.store._load()
        except:
            self.assertFalse(True, 'loading without file should fail silently')

    def test_load_scores_old_format(self):
        self.setScores([['user', 42, 'killed on level 1 by a foo']])
        self.store._load()
        s = Score(user='user', score=42, level=1, status='killed', cause='foo')
        self.assertSequenceEqual([s], self.store.scores)

    def test_load_scores(self):
        s = Score(user='user', score=42, level=1, status='killed', cause='foo')
        self.setScores([s.__dict__])
        self.store._load()
        self.assertSequenceEqual([s], self.store.scores)

    # == .save == #

    def test_save_no_file(self):
        s = ScoresStore()
        try:
            s.save()
        except:
            self.assertFalse(True, 'saving without file should not fail')

    def test_save_no_previous_file(self):
        self.rmScores()
        self.store.save()
        self.assertTrue(os.path.isfile(self.scores))

    def test_save_override_previous_file(self):
        with open(self.scores, 'w') as f:
            f.write(json.dumps([1, 2, 3]))
        self.store.save()
        self.assertTrue(os.path.isfile(self.scores))
        self.assertSequenceEqual([], self.getScores())

    # == ._insert == #

    def test_insert_empty_scores(self):
        s = Score(user='foo', score=42)
        self.assertTrue(self.store._insert(s))
        self.assertFalse(self.store.saved)
        self.assertSequenceEqual([s], self.store.scores)

    def test_insert_no_duplicate(self):
        s = Score(user='foo', score=42)
        self.assertTrue(self.store._insert(s))
        self.store.saved = True
        self.assertFalse(self.store._insert(Score(user=s.user, score=s.score)))
        self.assertTrue(self.store.saved)
        self.assertSequenceEqual([s], self.store.scores)

    def test_insert_append(self):
        self.store.scores = [Score(score=20), Score(score=10)]
        s = Score(user='foo', score=2)
        self.assertTrue(self.store._insert(s))
        self.assertEquals(3, len(self.store.scores))
        self.assertEquals(s, self.store.scores[-1])
        self.assertFalse(self.store.saved)

    def test_insert_first(self):
        self.store.scores = [Score(score=20), Score(score=10)]
        s = Score(user='foo', score=40)
        self.assertTrue(self.store._insert(s))
        self.assertEquals(3, len(self.store.scores))
        self.assertEquals(s, self.store.scores[0])
        self.assertFalse(self.store.saved)

    def test_insert(self):
        self.store.scores = [Score(score=20), Score(score=10)]
        s = Score(user='foo', score=15)
        self.assertTrue(self.store._insert(s))
        self.assertEquals(3, len(self.store.scores))
        self.assertEquals(s, self.store.scores[1])
        self.assertFalse(self.store.saved)

    # == ._add == #

    def test_internal_add_empty(self):
        self.assertFalse(self.store._add({}))

    def test_internal_add_no_score(self):
        self.assertFalse(self.store._add({'user': 'foo', 'cause': 'abc'}))
        self.assertFalse(self.store._add({'user': 'foo', 'text': 'quit'}))

    def test_internal_add_bad_score(self):
        self.assertFalse(self.store._add({'user': 'a', 'cause': 'abc',
                                          'score': '0x2A'}))
        self.assertFalse(self.store._add({'user': 'a', 'text': 'quit',
                                          'score': []}))

    def test_internal_add_no_user(self):
        self.assertFalse(self.store._add({'score': 42, 'cause': 'abc'}))

    def test_internal_add_bad_user(self):
        self.assertFalse(self.store._add({'score': 2, 'user': '',
                                          'level': 'x'}))
        self.assertFalse(self.store._add({'score': 2, 'user': '&#!',
                                          'level': 'x'}))

    def test_internal_add_bad_level(self):
        self.assertFalse(self.store._add({'score': 42, 'user': 'a',
                                          'level': 'x'}))
        self.assertFalse(self.store._add({'score': 42, 'user': 'a',
                                          'level': -5}))

    def test_internal_add_parse_text(self):
        d = {'score': 12, 'user': 'foo', 'text': 'killed on level 14 by bar'}
        self.assertTrue(self.store._add(d))
        self.assertEquals(1, len(self.store.scores))
        s = self.store.scores[0]
        self.assertEquals(12, s.score)
        self.assertEquals('foo', s.user)
        self.assertEquals('died', s.status)
        self.assertEquals(14, s.level)
        self.assertEquals('bar', s.cause)

    def test_internal_add_sanitize_attrs(self):
        d = {'score': '0012', 'user': '**yo**!', 'level': '42', 'cause': 'q$'}
        self.assertTrue(self.store._add(d))
        self.assertEquals(1, len(self.store.scores))
        s = self.store.scores[0]
        self.assertEquals(12, s.score)
        self.assertEquals('yo', s.user)
        self.assertEquals(42, s.level)
        self.assertEquals('q', s.cause)

    def test_internal_add_insert(self):
        self.store.scores = [Score(score=20), Score(score=10)]
        s = {'user': 'foo', 'score': 15}
        self.assertTrue(self.store._add(s))
        self.assertEquals(3, len(self.store.scores))
        self.assertEquals(15, self.store.scores[1].score)
        self.assertFalse(self.store.saved)

    # == .add == #

    def test_add_wrong_format(self):
        self.assertRaises(BadScoreFormatException, lambda: self.store.add(42))
        self.assertRaises(BadScoreFormatException, lambda: self.store.add([]))

    def test_add_old_format(self):
        t = ['foo', 17, 'quit on level 19.']
        self.assertEquals(1, self.store.add(t))
        s = self.store.scores[0]
        self.assertEquals('foo', s.user)
        self.assertEquals(17, s.score)
        self.assertEquals(19, s.level)

    def test_add_old_format_multiple(self):
        self.assertEquals(2, self.store.add(
            ['foo', 17, 'quit on level 19.'],
            ['bar', 18, 'quit on level 42.']
        ))

    def test_add_multiple(self):
        self.assertEquals(2, self.store.add(
            {'user': 'foo', 'score': 17, 'status': 'quit', 'level': 19},
            {'user': 'bar', 'score': 18, 'status': 'quit', 'level': 42}
        ))

    # == .__iter__ == #

    def test_iter(self):
        l = ['foo', 42, {}]
        self.store.scores = l
        self.assertSequenceEqual(l, list(self.store))

    # == .__getitem__ == #

    def test_getitem(self):
        self.store.scores = ['foo', 42, {}]
        self.assertEquals('foo', self.store[0])
        self.assertEquals({}, self.store[2])
        self.assertEquals({}, self.store[-1])

    # == .__len__ == #

    def test_len_empty(self):
        self.assertEquals(0, len(self.store))

    def test_len(self):
        self.store.scores = [1, 2, 3, 4]
        self.assertEquals(4, len(self.store))


    # == .__del__ == #

    def test_del_with_no_previous_saving(self):
        self.store.saved = False
        self.rmScores()
        del self.store
        self.assertTrue(os.path.isfile(self.scores))

    def test_del_with_previous_saving(self):
        self.store.saved = True
        self.rmScores()
        del self.store
        self.assertFalse(os.path.isfile(self.scores))

    def test_del_override_file_with_no_previous_saving(self):
        self.store.scores.append('foo')
        self.store.saved = False
        del self.store
        self.assertTrue(os.path.isfile(self.scores))
        self.assertSequenceEqual(['foo'], self.getScores())

    def test_del_override_file_with_previous_saving(self):
        self.store.scores.append('foo')
        self.store.saved = True
        del self.store
        self.assertTrue(os.path.isfile(self.scores))
        self.assertSequenceEqual([], self.getScores())

    def test_del_no_file(self):
        s = ScoresStore()
        try:
            del s
        except:
            self.assertFalse(True, 'it should not try to write on a file')

    # == .__empty__ == #

    def test_empty_yes(self):
        self.assertTrue(self.store.__empty__())
        self.assertTrue(not self.store)

    def test_empty_no(self):
        self.store.scores.append('a score')
        self.assertFalse(self.store.__empty__())
        self.assertFalse(not self.store)

    # == .__repr__ == #

    def test_repr_empty(self):
        self.assertEquals('ScoresStore([])', repr(ScoresStore()))
