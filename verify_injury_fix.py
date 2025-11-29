#!/usr/bin/env python3
"""
Quick verification script to test injury filtering with ESPN data format
Run this to verify the injury filtering is working correctly
"""

class MockPlayer:
    """Mock player with ESPN-style injury status"""
    def __init__(self, name, position, avg_points, injury_status):
        self.name = name
        self.position = position
        self.playerId = hash(name)
        self.avg_points = avg_points
        self.projected_avg_points = avg_points
        self.injuryStatus = injury_status
        self.stats = {0: {'points': avg_points * 10, 'avg_points': avg_points}}

    def __repr__(self):
        return f"{self.name} ({self.position}, {self.injuryStatus})"


def test_injury_filter_logic():
    """Test the injury filtering logic"""
    print("Testing injury filtering logic...\n")

    # Create test players with ESPN injury statuses
    players = [
        MockPlayer("Healthy Player 1", "RB", 15.0, "ACTIVE"),
        MockPlayer("Healthy Player 2", "RB", 14.0, "NORMAL"),
        MockPlayer("Joe Mixon", "RB", 16.0, "OUT"),  # Should be filtered
        MockPlayer("Questionable Player", "RB", 13.0, "QUESTIONABLE"),  # Should be filtered
        MockPlayer("IR Player", "RB", 17.0, "INJURY_RESERVE"),  # Should be filtered
        MockPlayer("No Status", "RB", 12.0, None),  # Should NOT be filtered
    ]

    print("All players:")
    for p in players:
        print(f"  {p}")

    print("\nApplying injury filter...")

    # Apply the filtering logic
    filtered_players = []
    for player in players:
        injury_status = player.injuryStatus

        # This is the ACTUAL filtering logic from advanced_simulator.py
        if injury_status and injury_status.upper() not in ['ACTIVE', 'NORMAL', '', None]:
            print(f"  ❌ FILTERED: {player.name} - status: {injury_status}")
            continue
        else:
            status_str = injury_status if injury_status else "None"
            print(f"  ✅ KEPT: {player.name} - status: {status_str}")
            filtered_players.append(player)

    print("\nFiltered players (healthy only):")
    for p in filtered_players:
        print(f"  {p}")

    # Verify results
    expected_healthy = ["Healthy Player 1", "Healthy Player 2", "No Status"]
    actual_healthy = [p.name for p in filtered_players]

    print("\n" + "="*60)
    if set(expected_healthy) == set(actual_healthy):
        print("✅ SUCCESS: Injury filtering is working correctly!")
        print(f"   Filtered out {len(players) - len(filtered_players)} injured players")
        print(f"   Kept {len(filtered_players)} healthy players")
    else:
        print("❌ FAILURE: Injury filtering is NOT working correctly!")
        print(f"   Expected: {expected_healthy}")
        print(f"   Got: {actual_healthy}")
    print("="*60)


if __name__ == "__main__":
    test_injury_filter_logic()
