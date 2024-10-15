def test_orchestrator():
    from tomo.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    result = orchestrator.handle_message("Hello", "session-123")
    assert result is not None
