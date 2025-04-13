import unittest
from query_parser import parse_query

class TestQueryParser(unittest.TestCase):

    def test_1_path_and_content_terms(self):
        query = "path:/Users/ionutcornea12/Documents/GitHub content:buna ziua"
        path_terms, content_terms = parse_query(query)
        print("Test 1:\n","Path terms: ", path_terms, "\nContent terms:", content_terms)
        self.assertEqual(path_terms, ["/Users/ionutcornea12/Documents/GitHub"])
        self.assertEqual(content_terms, ["buna", "ziua"])
        #test that the function correctly separates a path filter and a content filter from a mixed query string.
    def test_2_only_content(self):
        query = "the quick brown dog"
        path_terms, content_terms = parse_query(query)
        print("Test 2:\n","Path terms: ", path_terms, "\nContent terms:", content_terms)
        self.assertEqual(path_terms, [])
        self.assertEqual(content_terms, ["the", "quick", "brown", "dog"])

    def test_3_only_path(self):
        query = "path:/Users/ionutcornea12/Documents/GitHub/Search_Engine/Search_Engine_App/TestDir path:/Users/ionutcornea12/Documents/GitHub/GP_Project/GP Project"
        path_terms, content_terms = parse_query(query)
        print("Test 3:\n","Path terms: ", path_terms, "\nContent terms:", content_terms)
        expected = [
            "/Users/ionutcornea12/Documents/GitHub/Search_Engine/Search_Engine_App/TestDir",
            "/Users/ionutcornea12/Documents/GitHub/GP_Project/GP Project"
        ]
        self.assertEqual(path_terms, expected)
        self.assertEqual(content_terms, [])

if __name__ == '__main__':
    unittest.main()