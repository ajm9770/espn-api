from espn_api.football import League
from espn_api.utils.monte_carlo import MonteCarloSimulator
import pandas as pd

def run_simulation(league_id: int, year: int, swid: str = None, espn_s2: str = None):
    """Run Monte Carlo simulation for a league and display results
    
    Args:
        league_id: ESPN league ID
        year: Season year
        swid: ESPN SWID cookie for private leagues
        espn_s2: ESPN_S2 cookie for private leagues
    """
    # Initialize league
    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    
    # Create simulator
    simulator = MonteCarloSimulator(league, num_simulations=10000)
    
    # Run simulations
    results = simulator.run_simulations()
    
    # Create DataFrame for pretty display
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
    print("\nMonte Carlo Simulation Results")
    print("=============================")
    print(df.to_string(index=False))

if __name__ == "__main__":
    # Example usage
    LEAGUE_ID = 123456  # Replace with your league ID
    YEAR = 2024
    
    # For private leagues, add your ESPN cookies
    SWID = None  # Your SWID cookie
    ESPN_S2 = None  # Your ESPN_S2 cookie
    
    run_simulation(LEAGUE_ID, YEAR, SWID, ESPN_S2)
