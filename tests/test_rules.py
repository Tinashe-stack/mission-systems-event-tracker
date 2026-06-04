from rules import calculate_priority_score


def test_critical_link_down_scores_higher_than_info_heartbeat():
    critical_link_down = {
        "severity": "CRITICAL",
        "event_type": "LINK_DOWN",
    }

    info_heartbeat = {
        "severity": "INFO",
        "event_type": "HEARTBEAT",
    }

    critical_score = calculate_priority_score(critical_link_down)
    heartbeat_score = calculate_priority_score(info_heartbeat)

    assert critical_score > heartbeat_score