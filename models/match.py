import math

class Player:
    def __init__(self, name):
        self.name = name
        self.runs = 0
        self.balls_faced = 0
        self.fours = 0
        self.sixes = 0
        self.overs_bowled = 0
        self.balls_bowled = 0
        self.runs_conceded = 0
        self.wickets_taken = 0
        self.is_out = False
        self.is_retired = False

    def to_dict(self):
        return {
            "name": self.name,
            "runs": self.runs,
            "balls_faced": self.balls_faced,
            "fours": self.fours,
            "sixes": self.sixes,
            "overs_bowled": self.overs_bowled,
            "balls_bowled": self.balls_bowled,
            "runs_conceded": self.runs_conceded,
            "wickets_taken": self.wickets_taken,
            "is_out": self.is_out,
            "is_retired": self.is_retired,
            "strike_rate": self.strike_rate,
            "economy": self.economy,
            "overs_formatted": self.overs_formatted
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(data["name"])
        p.runs = data.get("runs", 0)
        p.balls_faced = data.get("balls_faced", 0)
        p.fours = data.get("fours", 0)
        p.sixes = data.get("sixes", 0)
        p.overs_bowled = data.get("overs_bowled", 0)
        p.balls_bowled = data.get("balls_bowled", 0)
        p.runs_conceded = data.get("runs_conceded", 0)
        p.wickets_taken = data.get("wickets_taken", 0)
        p.is_out = data.get("is_out", False)
        p.is_retired = data.get("is_retired", False)
        return p

    @property
    def strike_rate(self):
        if self.balls_faced == 0:
            return 0.0
        return round((self.runs / self.balls_faced) * 100, 2)

    @property
    def economy(self):
        overs = self.balls_bowled / 6
        if overs == 0:
            return 0.0
        return round(self.runs_conceded / overs, 2)
    def calculate_motm_points(self, is_winner=False, made_winning_runs=False):
        points = 0
        
        # 1. Batting Impact
        points += self.runs  # +1 per run
        if self.strike_rate > 140:
            points += 10
        if self.runs >= 100:
            points += 20
        elif self.runs >= 50:
            points += 10
        elif self.runs >= 30:
            points += 5
        
        if made_winning_runs:
            points += 15
            
        # 2. Bowling Impact
        points += (self.wickets_taken * 25)
        if self.wickets_taken >= 5:
            points += 20
        elif self.wickets_taken >= 3:
            points += 10
            
        if self.balls_bowled > 0 and self.economy < 6:
            points += 10
            
        # 5. All-Round Performance
        if self.runs >= 50 and self.wickets_taken >= 2:
            points += 25
        elif self.runs >= 30 and self.wickets_taken >= 1:
            points += 15
            
        # 6. Winning Team Advantage
        if is_winner:
            points += 10
            
        return points


    @property
    def overs_formatted(self):
        return f"{self.balls_bowled // 6}.{self.balls_bowled % 6}"

class Team:
    def __init__(self, name):
        self.name = name
        self.runs = 0
        self.wickets = 0
        self.balls = 0
        self.extras = {"wide": 0, "no_ball": 0, "bye": 0, "leg_bye": 0}
        self.players = {}  # name -> Player

    @classmethod
    def from_dict(cls, data):
        t = cls(data["name"])
        t.runs = data.get("runs", 0)
        t.wickets = data.get("wickets", 0)
        t.balls = data.get("balls", 0)
        t.extras = data.get("extras", {"wide": 0, "no_ball": 0, "bye": 0, "leg_bye": 0})
        t.players = {name: Player.from_dict(p_data) for name, p_data in data.get("players", {}).items()}
        return t

    def get_player(self, name):
        if name not in self.players:
            self.players[name] = Player(name)
        return self.players[name]

    def to_dict(self):
        return {
            "name": self.name,
            "runs": self.runs,
            "wickets": self.wickets,
            "balls": self.balls,
            "extras": self.extras,
            "players": {name: player.to_dict() for name, player in self.players.items()},
            "overs_formatted": self.overs_formatted,
            "total_extras": self.total_extras
        }

    @property
    def overs_formatted(self):
        return f"{self.balls // 6}.{self.balls % 6}"

    @property
    def total_extras(self):
        return sum(self.extras.values())

class Match:
    def __init__(self, team_a_name, team_b_name, total_overs, match_mode='double'):
        self.team_a = Team(team_a_name)
        self.team_b = Team(team_b_name)
        self.total_overs = total_overs
        self.match_mode = match_mode # 'single' or 'double'
        self.current_innings = 1
        self.batting_team = None
        self.bowling_team = None
        self.striker = None
        self.non_striker = None
        self.current_bowler = None
        self.is_finished = False
        self.target = None
        self.toss_winner = None
        self.history = []

    @classmethod
    def from_dict(cls, data):
        m = cls(
            data["team_a"]["name"], 
            data["team_b"]["name"], 
            data.get("total_overs", 0), 
            data.get("match_mode", "double")
        )
        m.team_a = Team.from_dict(data["team_a"])
        m.team_b = Team.from_dict(data["team_b"])
        m.current_innings = data.get("current_innings", 1)
        m.is_finished = data.get("is_finished", False)
        m.target = data.get("target")
        
        # Set batting_team and bowling_team correctly
        if data.get("batting_team") == m.team_a.name:
            m.batting_team = m.team_a
            m.bowling_team = m.team_b
        elif data.get("batting_team") == m.team_b.name:
            m.batting_team = m.team_b
            m.bowling_team = m.team_a
            
        if data.get("toss_winner"):
            m.toss_winner = m.team_a if data["toss_winner"] == m.team_a.name else m.team_b
            
        return m

    def to_dict(self):
        return {
            "team_a": self.team_a.to_dict(),
            "team_b": self.team_b.to_dict(),
            "total_overs": self.total_overs,
            "match_mode": self.match_mode,
            "current_innings": self.current_innings,
            "batting_team": self.batting_team.name if self.batting_team else None,
            "bowling_team": self.bowling_team.name if self.bowling_team else None,
            "is_finished": self.is_finished,
            "target": self.target,
            "toss_winner": self.toss_winner.name if self.toss_winner else None,
            "status_message": self.status_message
        }

    def setup_match(self, batting_team_name, striker_name, non_striker_name, bowler_name):
        if self.team_a.name == batting_team_name:
            self.batting_team = self.team_a
            self.bowling_team = self.team_b
        else:
            self.batting_team = self.team_b
            self.bowling_team = self.team_a
        
        self.striker = self.batting_team.get_player(striker_name)
        self.non_striker = self.batting_team.get_player(non_striker_name)
        self.current_bowler = self.bowling_team.get_player(bowler_name)

    def rotate_strike(self):
        if self.match_mode == 'single':
            return
        self.striker, self.non_striker = self.non_striker, self.striker

    def update_score(self, action, value=0):
        if self.is_finished:
            return

        ball_counted = True
        runs_to_add = 0
        extras_to_add = 0
        is_wicket = False

        if action == "runs":
            runs_to_add = value
            self.striker.runs += value
            self.striker.balls_faced += 1
            if value == 4: self.striker.fours += 1
            if value == 6: self.striker.sixes += 1
            if value % 2 != 0:
                self.rotate_strike()

        elif action == "wide":
            extras_to_add = 1 + value
            self.batting_team.extras["wide"] += 1 + value
            ball_counted = False
            # No strike rotation for extras unless value is odd
            if value % 2 != 0:
                self.rotate_strike()

        elif action == "no_ball":
            extras_to_add = 1 + value
            self.batting_team.extras["no_ball"] += 1 + value
            self.striker.runs += value  # runs from no ball go to batsman
            # self.striker.balls_faced += 1? Depending on rules. In most, no ball doesn't count as balls faced.
            ball_counted = False
            if value % 2 != 0:
                self.rotate_strike()

        elif action == "bye":
            extras_to_add = value
            self.batting_team.extras["bye"] += value
            self.striker.balls_faced += 1
            if value % 2 != 0:
                self.rotate_strike()

        elif action == "leg_bye":
            extras_to_add = value
            self.batting_team.extras["leg_bye"] += value
            self.striker.balls_faced += 1
            if value % 2 != 0:
                self.rotate_strike()

        elif action == "wicket":
            is_wicket = True
            self.batting_team.wickets += 1
            self.striker.balls_faced += 1
            self.striker.is_out = True
            self.current_bowler.wickets_taken += 1
            # Striker will be replaced by UI interaction

        elif action == "retire":
            self.striker.is_out = True
            self.striker.is_retired = True
            # No wickets incremented
            # Striker will be replaced by UI interaction

        # Global updates
        self.batting_team.runs += runs_to_add + extras_to_add
        self.current_bowler.runs_conceded += runs_to_add + extras_to_add
        
        if ball_counted:
            self.batting_team.balls += 1
            self.current_bowler.balls_bowled += 1
            
            # End of over
            if self.batting_team.balls % 6 == 0:
                self.rotate_strike()
                # Bowler replacement will be required by UI

        # Check for innings end
        self.check_innings_end()

    def check_innings_end(self):
        overs_completed = (self.batting_team.balls >= self.total_overs * 6)
        all_out = (self.batting_team.wickets >= 10)
        target_achieved = (self.current_innings == 2 and self.batting_team.runs >= self.target)

        if overs_completed or all_out or target_achieved:
            if self.current_innings == 1:
                self.start_second_innings()
            else:
                self.is_finished = True

    def start_second_innings(self):
        self.target = self.batting_team.runs + 1
        self.current_innings = 2
        # Switch teams
        self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
        # Reset striker/non-striker/bowler for new innings
        self.striker = None
        self.non_striker = None
        self.current_bowler = None

    def replace_striker(self, name):
        self.striker = self.batting_team.get_player(name)

    def replace_bowler(self, name):
        self.current_bowler = self.bowling_team.get_player(name)

    @property
    def winner_name(self):
        if not self.is_finished:
            return None
        if self.team_a.runs > self.team_b.runs:
            return self.team_a.name
        elif self.team_b.runs > self.team_a.runs:
            return self.team_b.name
        return "Draw"

    @property
    def loser_name(self):
        if not self.is_finished or self.winner_name == "Draw":
            return None
        return self.team_b.name if self.winner_name == self.team_a.name else self.team_a.name

    @property
    def man_of_the_match(self):
        if not self.is_finished:
            return None
            
        best_player = None
        max_points = -1
        
        all_players = []
        for p in self.team_a.players.values():
             all_players.append((p, self.team_a.name))
        for p in self.team_b.players.values():
             all_players.append((p, self.team_b.name))
             
        for player, team_name in all_players:
            is_winner = (team_name == self.winner_name)
            # Find if this player made the winning runs
            made_winning_runs = False
            if self.is_finished and self.current_innings == 2 and is_winner:
                 if self.striker and self.striker.name == player.name:
                      made_winning_runs = True
            
            points = player.calculate_motm_points(is_winner, made_winning_runs)
            if points > max_points:
                max_points = points
                best_player = player
        
        return best_player, max_points

    @property
    def status_message(self):
        if self.is_finished:
            if self.team_a.runs > self.team_b.runs:
                winner = self.team_a.name
                margin = self.team_a.runs - self.team_b.runs
                return f"{winner} won by {margin} runs!"
            elif self.team_b.runs > self.team_a.runs:
                if self.current_innings == 2 and self.batting_team.name == self.team_b.name:
                     # Chasing team won
                     wickets_left = 10 - self.batting_team.wickets
                     return f"{self.batting_team.name} won by {wickets_left} wickets!"
                else:
                    winner = self.team_b.name
                    margin = self.team_b.runs - self.team_a.runs
                    return f"{winner} won by {margin} runs!"
            else:
                return "Match Drawn (Tie)!"
        
        if self.current_innings == 2:
            runs_needed = self.target - self.batting_team.runs
            balls_left = (self.total_overs * 6) - self.batting_team.balls
            return f"{self.batting_team.name} needs {runs_needed} runs from {balls_left} balls."
        
        if self.batting_team:
            return f"{self.batting_team.name} is batting (1st Innings)"
        return "Match Setup"
