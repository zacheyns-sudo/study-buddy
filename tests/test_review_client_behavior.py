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

    def test_planner_start_tab_and_streaming_hooks_exist(self):
        self.assertIn('data-start-tab="plan"', self.html)
        self.assertIn('id="planner-assignment"', self.html)
        self.assertIn("async function generateOutline()", self.html)
        self.assertIn("fetch('/api/plan'", self.html)

    def test_planner_upload_and_copy_hooks_exist(self):
        self.assertIn('id="planner-file-input"', self.html)
        self.assertIn("handlePlannerUpload", self.html)
        self.assertIn("copyPlannerOutline", self.html)

    def test_pasted_draft_entry_and_editable_review_hooks_exist(self):
        self.assertIn('id="draft-textarea"', self.html)
        self.assertIn("async function handleDraftStart()", self.html)
        self.assertIn("fetch('/api/draft'", self.html)
        self.assertIn('id="draft-editor"', self.html)
        self.assertIn("syncDraftFromEditor", self.html)
        self.assertIn("Draft changed", self.html)


if __name__ == "__main__":
    unittest.main()
