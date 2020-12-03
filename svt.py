import argparse
import csv

from colorama import Style, init

init()

voters = {}


def parse_threshold(thr):
    if thr >= 0 and thr <= 100:
        return thr

    raise argparse.ArgumentTypeError(f"Error: Threshold {thr} is not in range 0 - 100")


def check_voters(data: dict):
    if not voters or data['Discord tag (UserName#0000)'] not in voters.keys():
        voters[data['Discord tag (UserName#0000)']] = 1
    else:
        voters[data['Discord tag (UserName#0000)']] += 1


def remove_multivotes(data):
    votes = {}

    for key, value in data.items():
        votes[value['Discord tag (UserName#0000)']] = value

    return votes


def count_priority_votes(parties, priority, max_votes):
    print(f"Results for round {priority}: \n")
    for key, value in parties.items():
        print(f"{key}: {value[str(priority)]} votes, {value[str(priority)] / max_votes}")


def count_votes(votes):
    parties = {}
    for party in votes[list(votes.keys())[0]].keys():
        if party != 'Discord tag (UserName#0000)' and party != 'Timestamp':
            parties[party] = {'1': 0}

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
