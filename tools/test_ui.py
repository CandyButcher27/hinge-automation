import ui


def test_pending_reads_run_questions():
    assert ui.pending("stopped here, 2 photo(s) on screen. like one? [y/n/q] ") == {
        "kind": "decide", "question": "stopped here, 2 photo(s) on screen. like one?"}
    q = "comment: \"it's lovely - really\" - enter to keep, type a new one, or - for none: "
    assert ui.pending(q) == {"kind": "comment", "suggestion": "it's lovely - really"}


def test_prompts_error_rejects_untypeable_lines():
    assert ui.prompts_error("hi there\n\nnice photo\n") is None
    assert "not printable ASCII" in ui.prompts_error("hi\nnice ❤\n")
