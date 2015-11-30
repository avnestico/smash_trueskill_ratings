import argparse
import sys
import calcs
import scraping_functions as sf


def arg_parser(argv):
    """Process args passed in."""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Computes Glicko2 ratings of Super Smash Bros competitors')
    parser.add_argument('--scrape', dest='scrape', action='store_true',
                        help='Set this flag to re-scrape all tournaments')
    parser.set_defaults(scrape=False)
    parser.add_argument('--scrape_tournament', '--scrape-tournament', dest='tournaments', default=None,
                        help="Comma-separated list of tournaments to scrape, by filename")
    parser.add_argument('--format', dest='output_format', default='human',
                        help="Format of output: 'human' (human-readable) or 'tab' (tab-separated). Default: human")
    parser.add_argument('--game', dest='game', default=None,
                        help="Select a single game to process: 'SSB', 'Melee', 'Brawl', 'PM', or 'Sm4sh'")
    parser.add_argument('--top_amount', '--top-amount', dest='top_amount', default=100,
                        help="The number of players to be displayed. Default value: 100")

    args = parser.parse_args(argv)
    return args


def display_game_rankings(game, output_format, top_amount):
    """Display rankings for a single game as defined by format."""
    if output_format == "human" or "tab":
        calcs.show_rankings(game, number=top_amount, format=output_format)
    else:
        print("Format '" + output_format + "' not valid.")
        exit(1)


def display_all_rankings(output_format, top_amount):
    if output_format == "human" or "tab":
        for game in sf.get_valid_games():
            calcs.show_rankings(game, number=top_amount, format=output_format)
    else:
        print("Format '" + output_format + "' not valid.")
        exit(1)


def main(args):
    """Process Glicko2 ratings."""
    scrape = args.scrape
    tournaments = args.tournaments
    output_format = args.output_format
    game = args.game
    top_amount = int(args.top_amount)

    if scrape:
        sf.scrape_all_tournaments()

    if tournaments:
        tournaments = tournaments.split(",")
        for tournament in tournaments:
            sf.scrape_tournament_by_filename(tournament)

    # If a specific game is not set, process all games. Otherwise, process only that one game.
    if not game:
        calcs.process_all_games()
        display_all_rankings(output_format, top_amount)
    else:
        calcs.process_game_by_date(game)
        display_game_rankings(game, output_format, top_amount)

    return 0


if __name__ == "__main__":
    parsed_args = arg_parser(sys.argv[1:])
    sys.exit(main(parsed_args))