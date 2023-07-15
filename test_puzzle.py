import unittest
import puzzle

class TestTetris(unittest.TestCase):

    def test_render(self):
        print("---- test_render ----")
        t = puzzle.PuzzleEnv()
        t.render()


if __name__ == '__main__':
    unittest.main()