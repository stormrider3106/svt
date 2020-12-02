import pandas as pd
import os, json, copy
from shutil import copyfile
import dateutil.parser as dateparser

std_fileloc = "/mnt/c/Vote/votes.csv"
#filestd = input("standard file location? y/n: ")
#if filestd == "y":
#    fileloc = std_fileloc
#elif filestd == "n":
#    fileloc = input("file location?")
#else:
#    raise ValueError("wrong input")
    
threshold = input("enter threshold in %: \n")
df = pd.read_csv(std_fileloc)
#print(df.columns[1])
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
    voters = df.get("Discord tag (UserName#0000)")
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
    println = "total registered voters: %s \n registered voters: %s \n non-voting registered voters: %s \n new voters : %s" % (past_voters, rec_voters, abstain_voters, new_voters)
    print(println)
    with open("voterlist.txt", "w") as file:
        file.write(json.dumps(voterlist))
    print("following people voted multiple times:")
    print(multivoters)

remove = []
rounds = []
def print_result(votes, roundnr):
    print("Results after round " +str(roundnr)+ ":")
    for candidate in candidates:
        print(str(candidate) + ": " + str(votes[candidate][0]) + " votes, " +  str(votes[candidate][1] * 100) + "%")
    
def count_votes(): 
    multivote = {}
    rounds.append(None)
    total_votes = 0
    votes = {}
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
    #df.drop(remove, inplace=True)
    print(df)
    for roundnr in range(1, len(candidates)+1):
        candidate_list = {}
        candidate_list_n = {}
        for candidate in candidates:
            candidate_list[candidate] = 0
        for candidate in candidates:
            candidate_list_n[candidate] = copy.deepcopy(candidate_list)
        if roundnr == 1:
            rounds.insert(roundnr, copy.deepcopy(candidate_list))
        else:
            rounds.insert(roundnr, copy.deepcopy(candidate_list_n))
        for i in df.index:
            for j in range(2, 2+len(candidates)):
                if df.get(columns[j])[i] == roundnr and roundnr == 1:
                    rounds[roundnr][candidates[j-2]] = rounds[roundnr][candidates[j-2]] + 1
                    total_votes = total_votes + 1
                elif df.get(columns[j])[i] == roundnr:
                    for l in range(2, 2+len(candidates)):
                        if df.get(columns[l])[i] == roundnr - 1:
                            prev_candidate = l - 2
                    rounds[roundnr][candidates[prev_candidate]][candidates[j-2]] = rounds[roundnr][candidates[prev_candidate]][candidates[j-2]] + 1
    for candidate in candidates:
        votes[candidate] = [rounds[1][candidate], rounds[1][candidate]/total_votes]
    print_result(votes, 1)
    removed_candidates = []
    print(rounds[3]["Candidate Ranking [Candidate 3]"])
    def tally(roundnr_tally):
        if roundnr_tally > len(candidates):
            exit
        low = 1000000
        low_candidate = None
        for candidate in candidates:
            if roundnr_tally == 2:
                if votes[candidate][0] < low:
                    low = votes[candidate][0]
                    low_candidate = candidate
                    print("new low: " + str(low))
            else:
                if votes[candidate][0] < low and votes[candidate][0] != 0:
                    low = votes[candidate][0]
                    low_candidate = candidate
                    print("new low: " + str(low))
        votes[low_candidate] = [0,0]
        removed_candidates.append(low_candidate)
        for i in df.index:
            def combine(combinelevel):
                if combinelevel > len(candidates):
                    exit
                print("current round: " + str(roundnr_tally))
                for j in range(2, 2+len(candidates)):
                    if df.get(columns[j])[i] == roundnr_tally - 1 + combinelevel and candidates[j-2] in removed_candidates:
                        print("selected vote: " + str(i))
                        print("selected candidate: " +str(candidates[j-2]))
                        for k in range(2, 2+len(candidates)):
                            if df.get(columns[k])[i] == roundnr_tally + combinelevel and candidates[k-2] not in removed_candidates:
                                print("new candidate selection: "+str(candidates[k-2]))
                                new_votes = votes[candidates[k-2]][0]+1
                                votes[candidates[k-2]]= [new_votes, new_votes/total_votes]
                            else:
                                print("new candidate also removed: " +str(candidates[k-2]))
                                combine(combinelevel + 1)
            combine(0)
        print_result(votes, roundnr_tally)
        for candidate in candidates:
            if float(votes[candidate][1]) >= float(threshold)/100:
                break
            else:
                tally(roundnr_tally + 1)
    tally(2)

    
check_voters()
count_votes()
