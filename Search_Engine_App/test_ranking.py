import unittest

from database import compute_lenght_score,compute_depth_score

class TestRanking(unittest.TestCase):

    def test_1_txt_bonus(self):
        score = compute_lenght_score("/short/file.txt")
        print(f"Test 1:\nComputed score for short path: {score}")
        print("Manually calculated score:",100 - len("/short/file.txt") * 0.5 + 10)
        self.assertGreaterEqual(score, 100 - len("/short/file.txt") * 0.5 + 10)
    def test_2_long_path_penalty(self):
        path = "/very/long/path/to/a/file/that/will/produce/low/score/file.txt"
        score = compute_lenght_score(path)
        depth = compute_depth_score(path)
        print(f"Test 2:\nComputed score for long path: {score}")
        print(f"Compute depth for long path: {depth}")
        self.assertLess(score, 100)
        self.assertLess(depth, 100)
        self.assertGreater(depth, 1)
    def test_3_min_score(self):
        path = "/x" * 300 #/x/x/x/x/x
        score = compute_lenght_score(path)
        depth = compute_depth_score(path)
        print(f"Test 3:\nComputed score for very long path: {score}")
        print(f"Computed depth for very long path: {depth}")
        self.assertGreaterEqual(score, 1.0)
        self.assertGreaterEqual(depth, 1.0)

    def test_4_no_slash(self):
        path = "file.txt"
        depth = compute_depth_score(path)
        print(f"Test 4:\nComputed score for relative path (no slash): {depth}")
        self.assertEqual(depth, 100.0)
if __name__ == '__main__':
    unittest.main()