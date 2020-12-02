import pandas as pd
import os, json, copy
from shutil import copyfile
import dateutil.parser as dateparser
from colorama import Fore,Back,Style,init
from termcolor import colored

init()

std_fileloc = "/mnt/c/svt/votes.csv"
filestd = input("standard file location? y/n: ")
if filestd == "y":
   fileloc = std_fileloc
elif filestd == "n":
   fileloc = input("file location?")
else:
   raise ValueError("wrong input")
   
multivote_remove = input("remove multiple votes? (uses newest vote from voter) y/n: ")
if multivote_remove == "y":
   multivote_remover = True
elif multivote_remove == "n":
   multivote_remover = False
else:
   raise ValueError("wrong input")
    
threshold = input("enter threshold in %: ")
print()
df = pd.read_csv(std_fileloc)
columns = df.columns
candidates = []
multivoters = []
for i in range(2, len(columns)):
    candidates.append(columns[i])

def check_voters():
    if os.path.exists("voterlist.txt"):
        with open("voterlist.txt", "r") as file:
            try:
                voterlist = json.loads(file.read())
            except ValueError:
                print("error loading voter list. running without and recreating list")
                copyfile("voterlist.txt",  "bad_voterlist.txt")
                os.remove("voterlist.txt")
    else: 
        voterlist = []
    voters = df.get(columns[1])
    has_voted = []
    for voter in voters:
        if voter in has_voted:
            if voter not in multivoters:
                multivoters.append(voter)
        else:
            has_voted.append(str(voter))
    past_voters = len(voterlist)
    rec_voters = 0
    new_voters = 0
    for voter in voters:
        if voter in voterlist and voter not in multivoters:
            rec_voters = rec_voters + 1
        elif voter not in multivoters:
            new_voters = new_voters + 1
            voterlist.append(str(voter))
    for voter in multivoters:
        if voter not in voterlist:
            new_voters = new_voters + 1
            voterlist.append(voter)
        else:
            rec_voters = rec_voters + 1
    abstain_voters = past_voters - rec_voters
    println = "total registered voters: %s \nregistered voters: %s \nnon-voting registered voters: %s \nnew voters : %s" % (past_voters, rec_voters, abstain_voters, new_voters)
    print(println)
    with open("voterlist.txt", "w") as file:
        file.write(json.dumps(voterlist))
    print()
    print("following people voted multiple times:")
    print(multivoters)
    print()

remove = []
rounds = []
def print_result(votes, roundnr, total_votes):
    header = "Results after round " +str(roundnr)+ ":"
    high = 0
    high_candidates = []
    low_candidates = []
    low = 1000000
    dim = []
    for candidate in candidates:
        if votes[candidate][0] >= high:
            if votes[candidate][0] == high:
                high_candidates.append(candidate)
            else:
                high = votes[candidate][0]
                high_candidates = [candidate]
        if votes[candidate][0] <= low and votes[candidate][0] != 0:
            if votes[candidate][0] == low:
                low_candidates.append(candidate)
            else:
                low = votes[candidate][0]
                low_candidates = [candidate]
        if votes[candidate][0] == 0:
            dim.append(candidate)
    print("\033[4m"+Style.BRIGHT+header+Style.RESET_ALL)
    for candidate in candidates:
        candidate_out =  str(candidate) + ": " + str(votes[candidate][0]) + " votes, " +  str(round(votes[candidate][0] / total_votes * 100, 2)) + "%"
        if candidate in high_candidates:
            print("\033[1;92m"+candidate_out+Style.RESET_ALL)
        elif candidate in low_candidates:
            print("\033[1;91m"+candidate_out+Style.RESET_ALL)
        elif candidate in dim:
            print("\033[1;90m"+candidate_out+Style.RESET_ALL)
        else:
            print(Style.BRIGHT+candidate_out)
    print()
votes = {}  
total_votes = 0
removed_candidates = [] 

def count_individual(votes, roundnr, removed_candidates):
    global total_votes
    if roundnr == 1:
        for i in df.index:
            for j in range(2, len(candidates)+2):
                if df.get(columns[j])[i] == roundnr and candidates[j-2] not in removed_candidates:
                    try:
                        new_votes = votes[candidates[j-2]][0] + 1
                        total_votes = total_votes+1
                        votes[candidates[j-2]] = [new_votes, new_votes/total_votes]
                    except KeyError:
                        total_votes = total_votes+1
                        votes[candidates[j-2]] = [1, 1/total_votes]
    elif roundnr == len(candidates):
        high = 0
        high_candidates = []
        for candidate in candidates:
            if votes[candidate][0] >= high:
                if votes[candidate][0] == high:
                    high_candidates.append(candidate)
                else:
                    high = votes[candidate][0]
                    high_candidates = [candidate]
            votes[candidate] = [0,0]
        if len(high_candidates) > 1:
            for candidate in high_candidates:
                votes[candidate] = [int(total_votes/len(high_candidates)), 1/len(high_candidates)]
        else:
            votes[high_candidates[0]] = [total_votes,1]
    else:
        for candidate in candidates:
            votes[candidate]=[0,0]
        for i in df.index:
            limit = len(candidates)
            limit_candidate = None
            for j in range(2, len(candidates)+2):
                if df.get(columns[j])[i] < limit and candidates[j-2] not in removed_candidates:
                    limit = df.get(columns[j])[i]
                    limit_candidate = candidates[j-2]
            try:
                new_votes = votes[limit_candidate][0] + 1
                votes[limit_candidate] = [new_votes, new_votes/total_votes]
            except KeyError:
                total_votes = total_votes+1
                votes[limit_candidate] = [1, 1/total_votes]    
        for candidate in removed_candidates:
            votes[candidate] = [0,0]
                        
def threshold_test(votes, candidates):
    for candidate in candidates:
        try:    
            if float(votes[candidate][1]) >= float(threshold)/100:
                return False
            else:
                return True
        except KeyError:
            return True

def count_votes(): 
    multivote = {}
    rounds.append(None)
    for i in range(0,len(df.get(columns[1]))):
        voter = df.get(columns[1])[i]
        date = dateparser.parse(df.get(columns[0])[i])
        if voter in multivoters:
            if voter in multivote.keys():
                if date > multivote[voter][0]:
                    remove.append(multivote[voter][1])
                    multivote[voter] = [date, i]
                else :
                    remove.append(i)
            else:
                multivote[voter] = [date, i]
    if multivote_remover:
        df.drop(remove, inplace=True)
    roundnr = 1
    while (threshold_test(votes, candidates)):
        if roundnr > len(candidates):
            break
        if roundnr != 1:
            low = 1000000
            low_candidate = None
            for candidate in candidates:
                    if votes[candidate][0] < low and candidate not in removed_candidates:
                        low = votes[candidate][0]
                        low_candidate = candidate
            votes[low_candidate] = [0,0]
            removed_candidates.append(low_candidate)
        count_individual(votes, roundnr, removed_candidates)
        for candidate in candidates:
            if candidate not in votes.keys():
                votes[candidate] = [0,0]
        print_result(votes, roundnr, total_votes)
        roundnr = roundnr+1

    
check_voters()
count_votes()
