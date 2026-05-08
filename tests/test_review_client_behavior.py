from pathlib import Path
import unittest


INDEX_HTML = Path(__file__).resolve().parents[1] / "index.html"


class ReviewClientBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_further_review_clears_chat_context_after_success(self):
        self.assertIn("const wasFurtherReview = reviewCursor > 0;", self.html)
        self.assertIn("if(wasFurtherReview) clearChat();", self.html)

    def test_comment_cards_are_inserted_in_paragraph_order(self):
        self.assertIn("function insertCommentCardInOrder(card)", self.html)
        self.assertIn("existingIdx > cardIdx", self.html)

    def test_comment_quote_marks_the_matching_document_text(self):
        self.assertIn("function highlightCommentTarget(obj, type)", self.html)
        self.assertIn('class="comment-target', self.html)


if __name__ == "__main__":
    unittest.main()
