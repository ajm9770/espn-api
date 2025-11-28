from espn_api.football import League
from espn_api.utils.monte_carlo import MonteCarloSimulator
import pandas as pd
from typing import Dict, List
import numpy as np

def preseason_analysis(league_id: int, year: int, swid: str = None, espn_s2: str = None):
    """Run preseason analysis to determine optimal draft strategy
    
    Args:
        league_id: ESPN league ID
        year: Season year
        swid: ESPN SWID cookie for private leagues
        espn_s2: ESPN_S2 cookie for private leagues
    """
    # Initialize league
    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    
    # Create simulator in preseason mode
    simulator = MonteCarloSimulator(league, num_simulations=10000, preseason=True)
    
    # Analyze draft strategies
    strategy_results = simulator.analyze_draft_strategy()
    
    print("\nDraft Strategy Analysis")
    print("=====================")
    
    for strategy, results in strategy_results.items():
        print(f"\n{strategy} Strategy Analysis:")
        
        # Average roster composition of championship teams
        avg_comp = {
            pos: np.mean([r['composition'][pos] for r in results]) * 100
            for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']
        }
        
        print("Championship Roster Composition (Average %):")
        for pos, pct in avg_comp.items():
            print(f"  {pos}: {pct:.1f}%")
            
        # Average number of star players
        avg_stars = np.mean([r['star_players'] for r in results])
        print(f"Average Star Players: {avg_stars:.1f}")
        
        # Average total projection
        avg_proj = np.mean([r['total_projection'] for r in results])
        print(f"Average Total Projection: {avg_proj:.1f}")

def in_season_analysis(league_id: int, year: int, team_id: int, swid: str = None, espn_s2: str = None):
    """Run in-season analysis to optimize team decisions
    
    Args:
        league_id: ESPN league ID
        year: Season year
        team_id: Your team's ID
        swid: ESPN SWID cookie for private leagues
        espn_s2: ESPN_S2 cookie for private leagues
    """
    # Initialize league
    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    
    # Create simulator
    simulator = MonteCarloSimulator(league, num_simulations=10000)
    
    # Get free agents
    free_agents = league.free_agents()
    
    # Run season simulations
    results = simulator.run_simulations()
    
    print("\nSeason Outlook")
    print("=============")
    
    # Print current standings and projections
    data = []
    for team in league.teams:
        team_results = results[team.team_id]
        data.append({
            'Team': team.team_name,
            'Current Record': f"{team.wins}-{team.losses}",
            'Projected Wins': f"{team_results['avg_wins']:.1f}",
            'Playoff Odds': f"{team_results['playoff_odds']:.1f}%",
            'Championship Odds': f"{team_results['championship_odds']:.1f}%"
        })
    
    df = pd.DataFrame(data)
    print("\nLeague Projections:")
    print(df.to_string(index=False))
    
    # Get recommended moves
    recommendations = simulator.get_optimal_moves(team_id, free_agents)
    
    print("\nRecommended Moves:")
    print("=================")
    
    for rec in recommendations:
        if rec['type'] == 'trade':
            print(f"Trade Target: {rec['player'].name} from {rec['target_team']}")
        else:
            print(f"Add Free Agent: {rec['player'].name}")
        print(f"  Projected Value Added: {rec['value_added']:.1f}")
        print(f"  Priority: {rec['priority'].upper()}")
        print()

if __name__ == "__main__":
    # Example usage
    LEAGUE_ID = 123456  # Replace with your league ID
    YEAR = 2024
    TEAM_ID = 1  # Replace with your team ID
    
    # For private leagues, add your ESPN cookies
    SWID = None  # Your SWID cookie
    ESPN_S2 = None  # Your ESPN_S2 cookie
    
    # Run preseason analysis before draft
    preseason_analysis(LEAGUE_ID, YEAR, SWID, ESPN_S2)
    
    # Run in-season analysis during the season
    in_season_analysis(LEAGUE_ID, YEAR, TEAM_ID, SWID, ESPN_S2)
