import argparse
import csv

from colorama import Style, init

init()

voters = {}


# check if entered threshold is between 0 and 100
def parse_threshold(thr):
    if thr >= 0 and thr <= 100:
        return thr

    raise argparse.ArgumentTypeError(f"Error: Threshold {thr} is not in range 0 - 100")


# counts how many times somebody has voted and adds them to the voters dictionary. how many times the peron has voted
# is stored as data under name as key
def check_voters(data: dict):
    if not voters or data['Discord tag (UserName#0000)'] not in voters.keys():
        voters[data['Discord tag (UserName#0000)']] = 1
    else:
        voters[data['Discord tag (UserName#0000)']] += 1


# removes older duplicate votes. only the youngest vote remains
def remove_multivotes(data):
    votes = {}

    for key, value in data.items():
        votes[value['Discord tag (UserName#0000)']] = value

    return votes


# prints out result of vote round
def count_priority_votes(parties, priority, max_votes):
    print(f"Results for round {priority}: \n")
    for key, value in parties.items():
        print(f"{key}: {value[str(priority)]} votes, {round(value[str(priority)] / max_votes * 100, 2)}%")


def count_votes(votes):
    parties = {}
    # adds parties to the parties dictionary
    for party in votes[list(votes.keys())[0]].keys():
        if party != 'Discord tag (UserName#0000)' and party != 'Timestamp':
            parties[party] = {'1': 0}

    # stores priorities of votes for parties as data using party and priority as keys
    for party, partydata in parties.items():
        for key, value in votes.items():
            if value[party] not in parties[party].keys():
                parties[party][value[party]] = 1
            else:
                parties[party][value[party]] += 1

    while len(parties.keys()) >= 0:
        count_priority_votes(parties, 1, len(votes))


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('-f', '--file', default='votes.csv', help='file location')
parser.add_argument('-m', '--multivotes', action='store_true', help='Allow Multivotes?')
parser.add_argument('-t', '--threshold', default=50, type=parse_threshold, help='Threshold')

args = parser.parse_args()

votes = {}

with open(args.file, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')

    for row in reader:
        check_voters(row)
        votes[row['Timestamp']] = row

if not args.multivotes:
    votes = remove_multivotes(votes)

count_votes(votes)
