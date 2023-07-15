import unittest
import puzzle

class TestTetris(unittest.TestCase):


    def test_render(self):
        t = puzzle.PuzzleEnv()
        t.render()

if __name__ == '__main__':
    unittest.main()