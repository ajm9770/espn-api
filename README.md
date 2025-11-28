# Fantasy Football Decision Maker

A comprehensive fantasy football decision-making system powered by **Monte Carlo simulation** and **Gaussian Mixture Models (GMM)** for predictive analytics.

## Features

### 🎯 Core Capabilities

1. **Current Matchup Analysis**
   - Simulate your current week's matchup 10,000+ times
   - Get win probability, projected score ranges, and confidence intervals
   - Understand your chances with data-driven insights

2. **Free Agent Recommendations**
   - Analyze 100s of free agents automatically
   - Get ranked recommendations based on value added to your roster
   - See suggested drop candidates and net value improvement
   - Filter by position or overall roster impact

3. **Trade Opportunity Detection**
   - Automatically scan all teams for asymmetric trade opportunities
   - Find undervalued players on other teams' benches
   - Identify position upgrades where opponent has depth
   - Get 1-for-1 and 2-for-1 trade suggestions with value analysis

4. **Rest of Season Projections**
   - Simulate remaining season 10,000+ times
   - Get playoff odds and championship probability
   - Projected final record for all teams
   - Understand what you need to make playoffs

### 🔬 Advanced Analytics

- **Gaussian Mixture Models**: Players are modeled with multiple performance states (hot streak, normal, cold streak) for realistic variance
- **Player-Level Simulation**: Simulates individual player performance rather than just team averages
- **Caching System**: First run trains models and caches results; subsequent runs are fast (minutes → seconds)
- **State Detection**: Automatically detects if players are trending hot or cold based on recent games

## Installation

```bash
# Clone repository
cd espn-api

# Install dependencies
pip install -r requirements.txt

# Make the script executable (optional)
chmod +x fantasy_decision_maker.py
```

## Quick Start

### Finding Your League ID and Team ID

1. **League ID**: Go to your ESPN Fantasy Football league, look at the URL:
   ```
   https://fantasy.espn.com/football/league?leagueId=123456
                                                      ^^^^^^
   ```

2. **Team ID**: Click on your team, look at the URL:
   ```
   https://fantasy.espn.com/football/team?leagueId=123456&teamId=1
                                                                 ^
   ```

### Option 1: Using Config File (Recommended)

**Setup once:**
```bash
# Copy the template
cp config.template.json config.json

# Edit config.json with your league details
# Add your league_id, team_id, and optionally swid/espn_s2
```

**Use every week:**
```bash
python fantasy_decision_maker.py --config config.json
```

See [CONFIG_USAGE.md](CONFIG_USAGE.md) for complete config file documentation.

### Option 2: Using Command Line

#### For Public Leagues

```bash
python fantasy_decision_maker.py --league-id YOUR_LEAGUE_ID --team-id YOUR_TEAM_ID
```

#### For Private Leagues

You need ESPN cookies:

1. Log into ESPN Fantasy Football
2. Open Developer Tools (F12)
3. Go to Application/Storage → Cookies → espn.com
4. Copy values for `SWID` and `espn_s2`

```bash
python fantasy_decision_maker.py \
  --league-id YOUR_LEAGUE_ID \
  --team-id YOUR_TEAM_ID \
  --swid "{YOUR-SWID-COOKIE}" \
  --espn-s2 "YOUR-ESPN-S2-COOKIE"
```

## Usage Guide

### Interactive Mode (Default)

```bash
python fantasy_decision_maker.py --league-id 123456 --team-id 1
```

You'll get an interactive menu:

```
🏈 FANTASY FOOTBALL DECISION MAKER

What would you like to analyze?
  1. Current Week Matchup
  2. Free Agent Recommendations
  3. Trade Opportunities
  4. Rest of Season Outlook
  5. Generate Full Weekly Report
  6. Exit
```

### Automated Weekly Report

Generate a comprehensive report without interaction:

```bash
python fantasy_decision_maker.py \
  --league-id 123456 \
  --team-id 1 \
  --report-only
```

This creates a text file with:
- Matchup analysis with win probability
- Season outlook with playoff odds
- Top 10 free agent recommendations
- Top 5 trade opportunities

### Advanced Options

```bash
# Increase simulation accuracy (slower but more precise)
python fantasy_decision_maker.py --league-id 123456 --team-id 1 --simulations 50000

# Use different cache directory
python fantasy_decision_maker.py --league-id 123456 --team-id 1 --cache-dir ~/ff_cache

# Different year
python fantasy_decision_maker.py --league-id 123456 --team-id 1 --year 2023
```

## How It Works

### First Run (Training Phase)

When you run the tool for the first time:

1. **Data Collection**: Fetches your league data from ESPN
2. **Player Model Training**: Trains Gaussian Mixture Models for all players based on weekly performance history
3. **Caching**: Saves trained models to `.cache/` directory
4. **Analysis**: Runs your requested analyses

**Expected time**: 1-3 minutes (depending on league size)

### Subsequent Runs (Fast Mode)

After the first run:

1. **Cache Loading**: Loads pre-trained player models from cache
2. **Quick Update**: Only updates recent data
3. **Analysis**: Immediately runs simulations

**Expected time**: 5-15 seconds

### Cache Refresh

Caches are valid for 24 hours. After that, models are automatically retrained with the latest data.

To force a refresh, delete the `.cache/` directory:

```bash
rm -rf .cache
```

## Understanding the Output

### Matchup Analysis Example

```
📅 WEEK 10 MATCHUP ANALYSIS

Team Alpha vs Team Beta
Your Record: 6-3
Their Record: 5-4

🎲 Running 10,000 matchup simulations...

📊 SIMULATION RESULTS
────────────────────────────────────────────────────────────────────────────────

Team Alpha:
  Win Probability: 64.2%
  Projected Score: 118.3 ± 15.2
  Score Range (10th-90th percentile): 98.5 - 137.8

Team Beta:
  Win Probability: 35.8%
  Projected Score: 109.7 ± 18.3
  Score Range (10th-90th percentile): 86.2 - 133.4

💡 OUTLOOK:
   🟢 Strong favorite - 64% chance to win
```

**What this means**:
- You have a 64% chance to win this matchup
- Expected to score 118 points (±15 standard deviation)
- 80% of simulations had you scoring between 98-138 points
- You're the favorite but not guaranteed (1 in 3 chance of loss)

### Free Agent Recommendations Example

```
🎯 TOP FREE AGENT RECOMMENDATIONS:

Rank  Player              Pos  Value Added  Proj Avg  Drop               Drop Avg  Priority  Own %
1     Josh Downs          WR   +4.2         12.3      Tyler Boyd         8.1       HIGH      45.2%
2     Chuba Hubbard       RB   +3.8         11.5      Roschon Johnson    7.7       HIGH      38.7%
3     Tank Dell           WR   +2.9         10.2      Dontayvion Wicks   7.3       MEDIUM    52.1%
```

**What this means**:
- Adding Josh Downs and dropping Tyler Boyd would add 4.2 points per week to your roster
- Downs projects to 12.3 PPG vs Boyd's 8.1 PPG
- 45% of leagues have Downs rostered (moderate availability)

### Trade Opportunity Example

```
TRADE #1: with Team Gamma
────────────────────────────────────────────────────────────────────────────────

  You Give:    Travis Etienne, Tyler Lockett
  You Receive: Ja'Marr Chase

  📊 Analysis:
     Your Value Change:      +8.3 pts
     Their Value Change:     +1.2 pts
     Advantage Margin:       +7.1 pts
     Points Added Per Week:  +0.8 pts
     Recommendation:         ACCEPT
     Confidence:             78%

  ✅ ASYMMETRIC ADVANTAGE: You gain significantly more value!
```

**What this means**:
- You add 8.3 points of total value; they only add 1.2 points
- You gain 7.1 more points than them (asymmetric!)
- This adds 0.8 points per week to your starting lineup
- High confidence (78%) this improves your team

### Season Outlook Example

```
📊 PROJECTED STANDINGS:

Team                      Current  Proj Wins  Playoff %  Ship %
Team Alpha                6-3      10.2       87.3%      18.4%
Team Beta                 7-2      10.1       85.1%      16.2%
Team Gamma                5-4      8.7        64.2%      8.7%
Your Team                 4-5      7.3        38.9%      3.2%

────────────────────────────────────────────────────────────────────────────────
YOUR TEAM: Team Delta
────────────────────────────────────────────────────────────────────────────────
  Current Record:        4-5
  Projected Final Wins:  7.3
  Playoff Odds:          38.9%
  Championship Odds:     3.2%
```

**What this means**:
- Projected to finish 7-6 (winning 3 of next 8 games)
- 39% chance to make playoffs (need some luck)
- 3% chance to win championship if you make playoffs
- Currently 4th place, fighting for a playoff spot

## Weekly Workflow

Here's a recommended weekly workflow:

### Sunday Morning (Before Games)

```bash
# Generate your weekly report
python fantasy_decision_maker.py --league-id XXX --team-id X --report-only
```

Review:
1. Your matchup win probability
2. Free agent recommendations
3. Consider any waiver claims

### Tuesday (After Waivers Clear)

```bash
# Run interactive mode
python fantasy_decision_maker.py --league-id XXX --team-id X
```

Actions:
1. Check updated free agents
2. Make any free agent pickups based on recommendations
3. Review trade opportunities

### Mid-Week (Wednesday-Saturday)

```bash
# Quick matchup check
python fantasy_decision_maker.py --league-id XXX --team-id X
# Select option 1: Current Week Matchup
```

Use this to:
- Monitor your win probability as news develops
- Adjust expectations based on injuries/news
- Decide on risky plays vs safe floor

## Tips for Success

### 🎯 Using Matchup Analysis

- **Win Probability < 40%**: You need upside plays, take calculated risks
- **Win Probability 40-60%**: Even matchup, play your studs
- **Win Probability > 60%**: Play it safe, prioritize floor over ceiling

### 📊 Free Agent Strategy

- **HIGH Priority (+3.0 pts)**: Use waiver priority or FAAB
- **MEDIUM Priority (+1.0 to +3.0 pts)**: Free agent pickup after waivers
- **LOW Priority (< +1.0 pts)**: Only if you have roster space

### 🔄 Trade Evaluation

- **Advantage Margin > +5.0**: Strongly pursue this trade
- **Advantage Margin +3.0 to +5.0**: Good trade, try to execute
- **Advantage Margin +1.0 to +3.0**: Minor upgrade, situational
- **Advantage Margin < +1.0**: Not worth the effort

Look for:
- Players on other teams' benches with starter value
- Consolidation trades (2-for-1) when you're deeper at a position
- Position-scarce players (TE, QB) where opponent has multiples

### 🏆 Playoff Push Strategy

**If playoff odds > 70%**: Focus on playoff schedule (weeks 15-17)
- Target players with easy playoff matchups
- Consider trading current value for playoff upside

**If playoff odds 40-70%**: Focus on win-now
- Maximize points every week
- Don't sacrifice current week for future

**If playoff odds < 40%**: Swing for the fences
- Take high-upside gambles
- Look for breakout candidates
- Pursue asymmetric trades aggressively

## Troubleshooting

### "Team ID not found"

Double-check your team ID in the ESPN URL when viewing your team.

### "401 Unauthorized" for private league

You need to provide ESPN cookies with `--swid` and `--espn-s2`. Make sure to include the curly braces in SWID: `"{12345-6789...}"`

### "Insufficient data for player X"

Some players don't have enough game history for GMM. The system automatically falls back to normal distribution for these players.

### Simulations are slow

- Reduce `--simulations` to 5000 for faster results (default: 10000)
- After first run, cache makes subsequent runs much faster
- Close other applications to free up CPU

### Cache issues

Delete cache and retrain:
```bash
rm -rf .cache
python fantasy_decision_maker.py --league-id XXX --team-id X
```

## Technical Details

### Gaussian Mixture Models (GMM)

Each player is modeled with 3 performance states:
- **Hot streak**: Recent performance above season average
- **Normal**: Performing at season average
- **Cold streak**: Recent performance below season average

The model:
1. Trains on all weekly scores from current season
2. Identifies natural clusters in performance
3. Weights sampling towards recent state (70% current state, 30% other states)

### Monte Carlo Simulation

For each simulation:
1. Sample each starter's performance from their GMM
2. Sum to get team total score
3. Compare to opponent's simulated score
4. Record winner

Repeat 10,000 times to get win probability distribution.

### Value Calculation

Player value considers:
- **Starter value**: Would this player start on my team?
- **Bench depth**: How valuable as a backup?
- **Positional scarcity**: TE, QB valued higher than WR, RB
- **Consistency**: Lower variance = higher value for starters

Trade value = (Starter impact × 1.0) + (Bench impact × 0.3)

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review ESPN API documentation: https://github.com/cwendt94/espn-api
3. Open an issue on GitHub

## License

This tool is built on top of the espn-api package (MIT License).

## Disclaimer

This tool provides data-driven recommendations based on historical performance and statistical modeling. Fantasy football outcomes depend on many unpredictable factors (injuries, game script, weather, etc.). Use this tool as one input in your decision-making process, not as a guarantee of results.

Good luck! 🏈🏆
