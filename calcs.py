import math
import operator
import trueskill
from trueskill.backends import cdf


trueskill.setup(draw_probability=0, sigma=4.166, beta=2.0833)


class Player:
    def __init__(self):
        self.Rating = trueskill.Rating()
        self.match_count = 0

    def get_rating(self):
        return self.Rating.mu, self.Rating.sigma

    def add_match(self):
        self.match_count += 1

    def get_match_count(self):
        return self.match_count


class Players:
    def __init__(self):
        self.table = {}

    def add_player(self, name):
        self.table[name] = Player()

    def check_player(self, name):
        try:
            self.table[name]
        except KeyError:
            self.add_player(name)

    def rate_1vs1(self, winner, loser):
        self.check_player(winner)
        self.check_player(loser)

        self.table[winner].Rating, self.table[loser].Rating = \
            trueskill.rate_1vs1(self.table[winner].Rating, self.table[loser].Rating)

        self.add_matches([winner, loser])

    def add_matches(self, players):
        for player in players:
            self.table[player].add_match()

    def win_stdev(self, player, opp=None):
        player_rating = self.table[player].Rating
        if not opp:
            opp_rating = trueskill.Rating()
        else:
            opp_rating = self.table[opp].Rating

        delta_mu = player_rating.mu - opp_rating.mu
        rsss = math.sqrt(player_rating.sigma**2 + opp_rating.sigma**2)
        return delta_mu/rsss

    def win_pct(self, player, opp=None):
        return cdf(self.win_stdev(player, opp))

    def calculate_ratings(self, filename):
        with open(filename, "r") as match_file:
            for line in match_file:
                winner, loser = line.strip().split(",")
                self.rate_1vs1(winner.title(), loser.title())

    def get_trueskill_pct(self):
        pct_table = {}
        for player in self.table:
            pct_table[player] = self.rate_player(player)
        ordered_table = sorted(pct_table.items(), key=operator.itemgetter(1), reverse=True)
        i = 0
        for pair in ordered_table:
            player_rating = self.table[pair[0]].Rating
            num_matches = self.table[pair[0]].get_match_count()
            if i < 100:
                print(pair[0], format_score(pair[1]), format_score(player_rating.mu), format_score(player_rating.sigma), num_matches, sep='\t')
                i += 1

    def rate_player(self, player):
        p_rating = self.table[player].Rating
        return p_rating.mu - 3 * p_rating.sigma


def format_score(score):
    return round(score, 6)


def show_rankings(game, number=100, format="human"):
    pass

if __name__ == "__main__":
    ranking = Players()
    ranking.calculate_ratings("matches.txt")
    ranking.get_trueskill_pct()
