from gemini_wrapper import GeminiWrapper


def test_check_unfinished_promises_true(gemini: GeminiWrapper):
    sample_conversation_with_unfulfilled_promise = """
        [2024-01-01 10:00:00] Manager: I'll send you the price calculation by the end of today.
        [2024-01-01 10:05:00] Customer: Great, thank you! """
    result = gemini.check_unfinished_promises(sample_conversation_with_unfulfilled_promise)
    assert isinstance(result, bool)
    assert result

    sample_conversation_with_unfulfilled_promise = """
    [06/10 10:00] Manager: I'll calculate the cost and send it to you by the end of today
    [06/10 10:01] Client: Great, thanks! Looking forward to it
    [06/10 17:00] Client: Any updates on the calculation?
    """
    result = gemini.check_unfinished_promises(sample_conversation_with_unfulfilled_promise)
    assert isinstance(result, bool)
    assert result


def test_check_unfinished_promises_false(gemini: GeminiWrapper):
    sample_conversation_with_fulfilled_promise = """
    [2024-01-01 10:00:00] Manager: I'll send you the price calculation by the end of today.
    [2024-01-01 10:05:00] Customer: Great, thank you!
    [2024-01-01 16:00:00] Manager: Here's your calculation: $1000
    """
    result = gemini.check_unfinished_promises(sample_conversation_with_fulfilled_promise)
    assert isinstance(result, bool)
    assert not result

    sample_conversation_with_fulfilled_promise = """
    [06/10 10:00] Client: Getting error code 404 on login
    [06/10 10:05] Manager: I'll help you resolve this. Could you try clearing your browser cache first?
    [06/10 10:10] Client: Done, still same error
    [06/10 10:15] Manager: Let me check with our technical team
    [06/10 10:30] Manager: We found the issue. There was a temporary server problem. Should be fixed now, please try again
    [06/10 10:32] Client: Works now, thanks!
    """
    result = gemini.check_unfinished_promises(sample_conversation_with_fulfilled_promise)
    assert isinstance(result, bool)
    assert not result


