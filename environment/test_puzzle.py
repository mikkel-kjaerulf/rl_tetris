import unittest
import environment.src.puzzle_env as puzzle_env

class TestTetris(unittest.TestCase):

    def test_render(self):
        print("---- test_render ----")
        t = puzzle_env.PuzzleEnv()
        t.render()
    
    def test_step(self):
        print("---- test_step ----")
        t = puzzle_env.PuzzleEnv()
        t.step(3)
        t.step(3)
        t.step(0)
        t.render("terminal")


if __name__ == '__main__':
    unittest.main()