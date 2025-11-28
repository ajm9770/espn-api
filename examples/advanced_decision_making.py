"""
Advanced Fantasy Football Decision Making Example

This example demonstrates how to use the advanced simulator for:
1. Analyzing current matchup with Monte Carlo simulation
2. Finding trade opportunities with asymmetric value
3. Getting free agent recommendations
4. Projecting rest of season
"""

from espn_api.football import League
from espn_api.utils.advanced_simulator import AdvancedFantasySimulator
import pandas as pd


def example_matchup_analysis():
    """Example: Analyze current week's matchup"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Current Matchup Analysis")
    print("=" * 80)

    # Initialize league
    league = League(league_id=123456, year=2024)  # Replace with your league ID
    my_team = league.teams[0]  # Replace with your team

    # Create simulator
    simulator = AdvancedFantasySimulator(league, num_simulations=10000)

    # Get current opponent
    current_week = league.current_week
    opponent = my_team.schedule[current_week - 1]

    # Simulate matchup
    results = simulator.simulate_matchup(my_team, opponent, week=current_week)

    print(f"\n{my_team.team_name} vs {opponent.team_name}")
    print(f"\nWin Probability: {results['team1_win_probability']:.1f}%")
    print(f"Projected Score: {results['team1_avg_score']:.1f} ± {results['team1_score_std']:.1f}")
    print(f"Score Range (10th-90th): {results['team1_score_range'][0]:.1f} - {results['team1_score_range'][1]:.1f}")


def example_free_agent_analysis():
    """Example: Analyze free agents"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Free Agent Analysis")
    print("=" * 80)

    # Initialize league
    league = League(league_id=123456, year=2024)
    my_team = league.teams[0]

    # Create simulator
    simulator = AdvancedFantasySimulator(league, num_simulations=10000)

    # Get free agents
    free_agents = league.free_agents(size=100)

    # Get recommendations
    recommendations = simulator.recommend_free_agents(
        my_team,
        free_agents,
        top_n=10
    )

    # Display as DataFrame
    data = []
    for rec in recommendations:
        data.append({
            'Player': rec['player'].name,
            'Position': rec['position'],
            'Value Added': f"+{rec['value_added']:.1f}",
            'Drop': rec['drop_candidate'],
            'Priority': rec['priority']
        })

    df = pd.DataFrame(data)
    print("\nTop Free Agent Recommendations:")
    print(df.to_string(index=False))


def example_trade_analysis():
    """Example: Find trade opportunities"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Trade Opportunity Analysis")
    print("=" * 80)

    # Initialize league
    league = League(league_id=123456, year=2024)
    my_team = league.teams[0]

    # Create simulator
    simulator = AdvancedFantasySimulator(league, num_simulations=10000)

    # Find trade opportunities
    opportunities = simulator.find_trade_opportunities(
        my_team,
        min_advantage=3.0,
        max_trades_per_team=2
    )

    print(f"\nFound {len(opportunities)} trade opportunities\n")

    for i, opp in enumerate(opportunities[:5], 1):
        print(f"\nTrade #{i}: with {opp['other_team']}")
        print(f"  Give:    {', '.join(opp['give'])}")
        print(f"  Receive: {', '.join(opp['receive'])}")
        print(f"  Value Change: {opp['analysis']['my_value_change']:+.1f} points")
        print(f"  Recommendation: {opp['analysis']['recommendation']}")


def example_specific_trade_evaluation():
    """Example: Evaluate a specific trade"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Evaluate Specific Trade")
    print("=" * 80)

    # Initialize league
    league = League(league_id=123456, year=2024)
    my_team = league.teams[0]
    other_team = league.teams[1]

    # Create simulator
    simulator = AdvancedFantasySimulator(league, num_simulations=10000)

    # Specify the trade (example: trading your RB for their WR)
    my_player = [p for p in my_team.roster if p.position == 'RB'][0]  # First RB
    their_player = [p for p in other_team.roster if p.position == 'WR'][0]  # First WR

    # Analyze trade
    analysis = simulator.analyze_trade(
        my_team,
        other_team,
        [my_player],
        [their_player],
        weeks_remaining=10
    )

    print(f"\nTrade Analysis:")
    print(f"  You Give: {my_player.name}")
    print(f"  You Get:  {their_player.name}")
    print(f"\n  Your Value Change:     {analysis['my_value_change']:+.1f} pts")
    print(f"  Their Value Change:    {analysis['their_value_change']:+.1f} pts")
    print(f"  Advantage Margin:      {analysis['advantage_margin']:+.1f} pts")
    print(f"  Recommendation:        {analysis['recommendation']}")
    print(f"  Confidence:            {analysis['confidence']:.0f}%")


def example_season_projection():
    """Example: Project rest of season"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Rest of Season Projection")
    print("=" * 80)

    # Initialize league
    league = League(league_id=123456, year=2024)
    my_team = league.teams[0]

    # Create simulator
    simulator = AdvancedFantasySimulator(league, num_simulations=10000)

    # Simulate rest of season
    results = simulator.simulate_season_rest_of_season()

    # Display results
    data = []
    for team in league.teams:
        team_results = results[team.team_id]
        data.append({
            'Team': team.team_name,
            'Current': f"{team.wins}-{team.losses}",
            'Projected Wins': f"{team_results['projected_wins']:.1f}",
            'Playoff %': f"{team_results['playoff_odds']:.1f}%",
            'Championship %': f"{team_results['championship_odds']:.1f}%"
        })

    df = pd.DataFrame(data)
    df = df.sort_values('Projected Wins', ascending=False)

    print("\nProjected Standings:")
    print(df.to_string(index=False))

    # Highlight my team
    my_results = results[my_team.team_id]
    print(f"\n{'─' * 80}")
    print(f"Your Team: {my_team.team_name}")
    print(f"  Current: {my_team.wins}-{my_team.losses}")
    print(f"  Projected Wins: {my_results['projected_wins']:.1f}")
    print(f"  Playoff Odds: {my_results['playoff_odds']:.1f}%")
    print(f"  Championship Odds: {my_results['championship_odds']:.1f}%")


def example_player_performance_analysis():
    """Example: Analyze individual player performance models"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Player Performance Model Analysis")
    print("=" * 80)

    # Initialize league
    league = League(league_id=123456, year=2024)
    my_team = league.teams[0]

    # Create simulator
    simulator = AdvancedFantasySimulator(league, num_simulations=1000)

    # Analyze your star players
    print("\nYour Players' Performance States:\n")

    for player in my_team.roster[:10]:  # Top 10 players
        state = simulator.player_model.get_player_state(player)

        if state:
            print(f"{player.name} ({player.position}):")
            print(f"  Season Average: {state['season_avg']:.1f} PPG")
            print(f"  Std Deviation:  {state['season_std']:.1f}")
            print(f"  Current State:  {state.get('current_state', 'Unknown').upper()}")

            if 'recent_scores' in state:
                recent = state['recent_scores']
                print(f"  Last 3 Weeks:   {recent[-3:]}")

            print()


def example_custom_simulation():
    """Example: Custom simulation with different parameters"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Custom Simulation Parameters")
    print("=" * 80)

    # Initialize league
    league = League(league_id=123456, year=2024)

    # Create simulator with custom parameters
    simulator = AdvancedFantasySimulator(
        league,
        num_simulations=50000,  # More simulations for higher accuracy
        cache_dir='.custom_cache',  # Custom cache directory
        use_gmm=True  # Enable Gaussian Mixture Models
    )

    print("\nSimulator initialized with:")
    print(f"  Simulations: 50,000")
    print(f"  GMM Enabled: Yes")
    print(f"  Cache Directory: .custom_cache")
    print("\nReady for analysis!")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║                                                                        ║
    ║        Advanced Fantasy Football Decision Making Examples             ║
    ║                                                                        ║
    ║  This script demonstrates various analysis capabilities.              ║
    ║  Update league_id and team indices with your actual values!           ║
    ║                                                                        ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)

    # Note: Uncomment the examples you want to run
    # Make sure to update league_id and team selections!

    # example_matchup_analysis()
    # example_free_agent_analysis()
    # example_trade_analysis()
    # example_specific_trade_evaluation()
    # example_season_projection()
    # example_player_performance_analysis()
    # example_custom_simulation()

    print("""
    To run these examples:
    1. Update league_id (line 23, 47, etc.) with your ESPN league ID
    2. Update team selection (league.teams[0]) to your team
    3. Uncomment the example(s) you want to run
    4. Run: python examples/advanced_decision_making.py

    For a complete interactive experience, use:
        python fantasy_decision_maker.py --league-id YOUR_ID --team-id YOUR_TEAM_ID
    """)
