"""
Emmanuel Malikides
October 2017

Aluga - an abandonded village in the Zlatibor District of Serbia.
Also my memorisation/learning program for breaking up and overcoming hurdles
while coding.
Unfortunately renamed to Ortega.

Also extendable/generaliseable for reading things online. 
- what are the key components of articles and videos?
- memorise them.
- remain confident in your ability to state your abilities and be
aware of your environment. 

Can also include other exercises in this! - exercises from books, physics problems, whatever.

Viewing progress, gaining some placebo certainty. 

Format for input: 
- use csv file.
 key, associations
 csv\ DictReader#-returns and iterable
 neural_net_image\neural.gif
 Question, answers

 * note images -> store file reference instead of associations. Grades are done manually
 * Q/a can work also.

Todo:
 - CLTool.
 - Pandas data structures.
 - print bug when there is no definition.

 - Add parser for json object/direct python code objects. Probably nicer
 - Merging databases functionality
 - How is this so different from a file system?? Could I use a file system?
 Do I need a file system?? 
 - Use it.
    1. identify topic.
    2. Read about topic.
    3. make notes
    4. type quiz and test
 - think about further incorporation with images and data.
 - Add video protocol:
 predominantly I take notes on videos
  - who, when, what are they saying.
 - Would be good to store URls somehow. Perhaps add a reference section for notes?
 

Format of csv inputs:

csvs are read into 'topics' -> each topic is a dictionary.
Everything is stored in the same shelf.

whithin the topic there is a "keyword", then (assessable) words, and - (notes)
The words are meant to be remembered, with their notes.
The keyword is the "prompt" or question.

escape characters:
\ =  divider
_source = source of information
_image = image.
# = devider of assessable answers
- = notes associated with answers.


key\ associations
csv\  csv.open()# DictReader# DictWriter# writerow
iterator object\ __iter__()# - implicitly called in loops# next()# - returns next thing# StopIteration()



"""
from PIL import Image
import shelve
import time
import csv
import sys
import random
import itertools
import matplotlib.pyplot as plt
from collections import defaultdict as dd
# import python_concept

""" database structure:
    shelf: 
    Topic (e.g. python_databases);
                    { key(eg shelf):
                    { associations: [(assble's, [notes]) 
                      grades: [ (date, score), ... ]
                     
                    } 
                    }

    Read from a database:

    key word; associations -notes, -notes, -notes
        

"""

DATAPATH = ""
SPECIAL = {"_sources","_image","_session_scores"}

def fuzzy_match(str1, str2):
    s1 = set(str1)
    s2 = set(str2)
    return float(len(s1&s2))/len(s2)

def score(answer, keyword_dic):
    """
    keyword_dic: {"associations":[(assbl, [notes]),...], "grades":}

    for each answer, count the number that match something in the 
    assessable words, divide by the number of correct answers
    """

    s = 0
    L = len(keyword_dic["associations"])
    correct = list(keyword_dic["associations"].keys())
    if answer:
        # threshold for word match
        threshold = 0.7
        tally = 0
        for a in answer.split("#"):
            scr = 0.0
            i = 0
            while  scr<threshold and i<L:
                scr = fuzzy_match(a,correct[i])
                i += 1
            if scr >= threshold:
                tally += 1
        if len(correct)>0:
            s = tally/len(correct)
        else :
            s = 1.0
    else :
        if len(correct):
            s = 0.0
        else :
            s = 1.0

    keyword_dic["grades"].append((time.time(),s))

def test(topic_db):
    if topic_db:
        stop = False
        print("\n"*50)  
        questions = [key for key in list(topic_db.keys()) if key not in SPECIAL]
        # dictionary of best answer so far of each question
        session_score = {}
        while not stop:
            # print(":s to stop")
            # keys are modules here.
            key = random.choice(questions)
            x = input(key+"??")
            stop = x == ":s"
            if "_image" in key:
                print("This was the image:")
                file = topic_db[key]["associations"].strip()
                img = Image.open(file) 
                img.show()
                x = input("Enter score: ")
                x = str(max(1.0,abs(float(x))))
                topic_db[key]["grades"].append((time.time(), x))
                session_score[key] = x
            elif "_sources" == key or "_session_scores" == key:
                pass
            elif ":s"!= x:
                score(x,topic_db[key])
                print("You scored:", topic_db[key]["grades"][-1][1])
                session_score[key] = topic_db[key]["grades"][-1][1]
                print("Answers:")
                if not stop:
                    # Associations are methods and notes for a 
                    # particular module..
                    stuff = topic_db[key]["associations"]
                    for (thing, notes) in stuff.items():
                        print(thing)
                        input()
                        for n in notes:
                            print(n)

            input()
            print("\n"*50)
        print("Session over. Score: ")
        net_avg_score = sum(session_score.values())/len(questions)
        print(net_avg_score)
        topic_db["_session_scores"].append((time.time(), net_avg_score))
        print("Summary:")
        for (k,v) in session_score.items():
            print(k,":",v)
    else :
        print("Empty dictionary")

def clear_grades(topic_db):
    if topic_db:
        for key in topic_db.keys():
            topic_db[key]["grades"] = []
    else :
        print("Empty dictionary")

def revise(topic_db):
    stop = False
    while not stop:
        key = random.choice(list(topic_db.keys()))
        primary = key
        info = topic_db[key]
        if "_image" in primary:
            print("Image!")
            print(primary)
            img = Image.open(info["associations"].strip())
            img.show()
        elif "_sources" == primary or "_session_scores" == primary:
            pass
        else :
            print("\n"*50)
            print(primary + ":")
            x = input()
            stop = x == ":s"
            for (assble, notes) in info["associations"].items(): 
                print(assble)
                if notes:
                    print("".join([n+'\n' for n in notes]))
        
        x = input()            

def parse_associations(associations_str):
    """
        returns {assessable keyword: [notes, if any...]), ...}
    """

    associations = dd(list)
    note_lst = []
    assble = ''
    info = associations_str.strip('[]').split('#')
    for i in range(len(info)):
        part = info[i]

        if part.strip() and part.strip()[0] == '-' and assble:
            # if we are after an information point add to notes
            note_lst.append(part.strip())
        else :
            # Now we are either at the beginning of a new note
            # or we are at the very beginning
            if assble : 
                associations[assble]=note_lst
                if not note_lst:
                    print("Error? No associations for:",assble)
                note_lst = []
                assble = part.strip()
            else:
                assble = part.strip()
                note_lst = []
    # store the last point
    associations[assble]=note_lst
    return associations

def parsenwrite_concepts_csv(topic_db, filename, overwrite=False):
    with open(filename) as fp:
        reader = csv.DictReader(fp, fieldnames = ["key","associations"], delimiter="""\\""")
        next(reader)
        for row in reader:
            
            key = row["key"]
            if "_image" in key:
                # image protocol: - have _image in name. assocaitions are the filename. grading done manually
                if key in topic_db:
                    topic_db[key]["associations"] = row["associations"]
                else :
                    topic_db[key] = {}
                    topic_db[key]["associations"] = row["associations"]
                    topic_db[key]["grades"] = []
            elif "_sources" in key:
                topic_db["_sources"] = row["associations"].strip().split("#")
            else :
                associations = parse_associations(row["associations"])    
                if key in topic_db:
                    if overwrite:
                        topic_db[key]["associations"] = associations        
                    else :
                        curr_associations = topic_db[key]["associations"]
                        for k in associations.keys():
                            curr_associations[k] = associations[k]
                else :
                    topic_db[key] = {}
                    topic_db[key]["associations"] = associations
                    topic_db[key]["grades"] = []

def parsenwrite_concepts_struct(topic_db, filename, overwrite=False):
    # NOT TESTED.
    with open(filename) as fp:
        questions = eval(fp.read())
        for (key, struct) in questions.items():
            topic_db[key]["grades"] = []
            topic_db[key]["associations"] = struct

def add_question(topic_db):
    print("Not implemented")
    # stop = False
    # stop2 = False
    # while not stop:
    #     question = input("Question?")
    #     ans = []
    #     while not stop2:
    #         ans = input("Answer? (or :s)")
                

def plot_scores(topic_db, topic):
    """
    Plot the results over time for concepts.
    """
    
    # plot each question
    times  = [s[0] for s in topic_db["_session_scores"]]
    scores = [s[1] for s in topic_db["_session_scores"]]
    plt.plot(times,scores)
    plt.xlabel('time')
    plt.ylabel('grade')
    plt.title('net average score over time for: '+topic)
    plt.show()


    # plot each question
    # l_plot = []
    # questions = [key for key in list(topic_db.keys()) if key not in SPECIAL]
    # for key in questions:
    #     times = [t for (t,g) in topic_db[key]["grades"] ]
    #     scores = [g for (t,g) in topic_db[key]["grades"] ]
    #     l_plot.append(plt.plot(times, scores,'+-'))
    # plt.legend([item[0] for item in l_plot], questions)
    # plt.xlabel('time')
    # plt.ylabel('grade')
    # plt.title('grades over time for selected topic')

    # plot sum of grades within time bins.
    # (grades are answered at different times.)
    # N_BINS = 10
    # min_time = 0
    # max_time = 0
    # plt.legend([item[0] for item in l_plot], questions)
    # plt.xlabel('time')
    # plt.ylabel('grade')
    # plt.title('grades over time for selected topic')
    # plt.show()

def grade_info(topic_db):
    questions = [q for q in list(topic_db.keys()) if q not in SPECIAL]
    print(questions)
    N = len(questions)
    latest_grades = [topic_db[q]["grades"][-1] for q in questions if topic_db[q]["grades"]]
    ag = float(sum([g[1] for g in latest_grades]))/N if N else 0
    if (latest_grades):
        at = float(sum([g[0] for g in latest_grades if g[0]>1]))/(len(latest_grades))
    else :
        at = 0
        
    print("Of", N, "Questions:")
    print("You answered:", len(latest_grades))
    print("average grade:", ag)
    print("average latest answer (if answered):", time.ctime(at))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("*** USAGE ***\n")
        sys.stderr.write("ortega "
                        "<database_name>\n")
        sys.exit(1)

    database_name = sys.argv[1]
    
    print("Command usage:")
    message = \
    """        
        Welcome to Ortega! Your friendly learning companion!!
        Hierarchy:
        Database (group of topics)
            Topic (group of factoids/questions)
                (fact: (asseble keywords and notes)) 
        E.g.
        Database: Deepmind interview
            Topics: 
                Interview: random interview questions
                Computer science: stuff from Computer science
                Machine learning:   "
                Statistics:         "

        :r <topic>            = revise topic
        :r <topic> <question> = revise question
        :t <topic>            = test topic
        :a <topic> <filename> overwrite = add csv file of notes to database, with option to overwrite if set flag
        :aq <topic>           = add question
        :c <topic>            = clear grades for topic
        :cl <topic>           = remove duplicate associations (soon to be removed)
        :q                    = quit
        :l                    = List topics in this database.
        :l <topic>            = List questions for a topic.
        :h                    = display this message
        :p <topic>            = plot grades over time for questions in topic
        :g <topic>            = print average grade for questions in topic
        ^                     = rerun last command
    During test:
        :s            = stop
        " "           = next 
        <str>         = answer a question
    """

    print(message)
    command = ""

    s    = shelve.open(database_name, writeback=True)
    skip = False
    last = ""
    while command != ":q":
        if not skip:
            last = command
            command = input("?")
        else :
            command = last
            print(command)
            input("?")
            skip = False

        if command[:3] ==":aq":
            print("Entering question adding mode:")
            topic = command.split()[1]
            if topic in s.keys():
                topic_db = s[topic]
                add_question(topic_db)
            else :
                print("Not a valid topic.")

        elif command[:2] == ":a":
            commands = command.split()
            if not len(commands) >= 3 :
                print('invalid command')
            else :
                print("updating database...")
                filename = commands[2]
                topic = commands[1]

                OR_flag = False
                if topic in s.keys():
                    topic_db = s[topic]
                else :
                    s[topic] = {}
                    topic_db = s[topic]
                    topic_db["_session_scores"] = []
                if len(commands) == 4:
                    OR_flag = commands[3]   
                parsenwrite_concepts_csv(topic_db, filename, overwrite=OR_flag)
        
        if command[:2] == ":l":
            args = command.split()
            if len(args) == 2:
                topic = command.split()[1]
                UNSPECIAL = set(SPECIAL) - {"_image"}
                questions = [k for k in s[topic].keys() if k not in SPECIAL]
                for k in questions:
                    print(k)
                print("There are:",len(questions),"questions for this topic.")
            else:
                for k in s.keys():
                    print(k)

        if command[:2] == ":g":
            topic = command.split()[1]
            if topic in s.keys():
                topic_db = s[topic]
                grade_info(topic_db)

        if command[:2] == ":h":
            print(message)

        if command[:2] == ":r":
            args = command.split()
            if len(args) == 2:
                topic = command.split()[1]
                if topic in s.keys():
                    topic_db = s[topic]
                    revise(topic_db)
            elif len(args) == 3:
                topic = command.split()[1]
                question = command.split()[2]
                
                if question in s[topic].keys():
                    print(question,":")
                    for (assble, notes) in s[topic][question]["associations"].items():
                        print(assble)
                        for n in notes:
                            print(n)
                else :
                    print("Not a question in this topic.")

        if command[:2] == ":t":
            topic = command.split()[1]
            if topic in s.keys():
                topic_db = s[topic]
                test(topic_db)

        if command[:3] == ":cl":
            topic = command.split()[1]
            if topic in s.keys():
                clean_associations(s[topic])
            else :
                print("No such topic.")

        elif command[:2] == ":c":
            topic = command.split()[1]
            if topic in s.keys():
                topic_db = s[topic]
                clear_grades(topic_db)

        if command[:2] == ":p":
            topic = command.split()[1]
            if s[topic]["_session_scores"]:
                plot_scores(s[topic], topic)
            else :
                print('no scores.')

        if command[:1] == "^":
            skip = True

    s.close()

