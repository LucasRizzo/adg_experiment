import pandas as pd
import copy
import time
import math 

CSV_FILE = './bank_sm.csv'
df = pd.read_csv(CSV_FILE,sep=';')
T = []
Y = []

for index, row in df.iterrows():
    T.append(set())
    for i in df.columns:
        if i != 'y':
            T[-1].add((i, row[i]))
        else:
            Y.append(row[i])

print(T)

class ArgumentationDecisionGraph:
    '''
    arguments is a set of tuples of (x, y), 
    relations is a set of tuples of (x1, x2), 
    x is a tuple of (i,vi), i is the feature index and vi is the value of the feature 
    y is the prediction, can be a value or und
    '''
    def __init__(self, ar, r):
        #ar is nodes
        self.arguments = ar
        #r is edges
        self.relations = r
    
    def __str__(self) -> str:

        result = "Arguments\n"
        for arg in self.arguments:
            result += str(arg) + "\n"
        
        result += "\nRelations\n"
        for r in self.relations:
            result += str(r) + "\n"

        return result

'''
verified function, 
2 parameters, 
parameter adg is of class ArgumentationDecisionGraph, 
parameter t is a tuple of (v1,v2,v3,..vi) where v is a tuple of (i,vi), i is the feature index and vi is the value of the feature
return a verified adg
'''
def verified(adg, t):
    verified_ar = set()
    verified_r = set()

    for i in adg.arguments:
        if i[0] in t:
            verified_ar.add(i)
    for j in adg.relations:
        if (j[0] in t) and (j[1] in t):
            verified_r.add(j)

    return ArgumentationDecisionGraph(verified_ar, verified_r)
    

'''
label argumentaion framework according to grounded semantics, 
parameter adg is of class ArgumentationDecisionGraph, 
'''
def grounded(adg):
    #initialize set
    in_set = set()
    #initialize set
    out_set = set()
    #initialize set
    und_set = set()
    '''
    find roots of the graph 
    by iterate through the egdes 
    and put nodes don't have any incoming edges to in_set
    '''
    del_set = set()
    for i in adg.arguments:
        if i[0] not in [x[1] for x in adg.relations]:
            #add new tuple to in_set
            in_set.add(i)
            #remove i from arguments
            # adg.arguments.remove(i)
            del_set.add(i)
    for i in del_set:
        adg.arguments.remove(i)
    '''
    if in_set is empty, 
    put all nodes in und_set, 
    and return {'in': in_set, 'out': out_set, 'und': und_set}
    '''
    if len(in_set) == 0:
        for i in adg.arguments:
            und_set.add(i)
        return {'in': in_set, 'out': out_set, 'und': und_set}
    
    # reapeat 4 steps until no new arguments are added to in_set
    Flag = True
    cnt = 0
    try:
        while Flag:
            cnt += 1
            # print(in_set, out_set, und_set)
            # print(adg.arguments, adg.relations)
            # print('while loop counts:',cnt)
            if(len(adg.arguments) == 0):
                # print('no more arguments')
                break
            # print('After break statement')
            '''
            step 1:
            reject argumetns attacked by accepted arguments:
            iterate through the nodes in in_set,
            and find the nodes that have incoming edges from the nodes in in_set, 
            and put them in out_set
            '''
            for i in in_set:
                for j in adg.relations:
                    if i[0] == j[0]:
                        del_set = set()
                        for k in adg.arguments:
                            if j[1] == k[0]:
                                out_set.add(k)
                                #remove k from arguments
                                # adg.arguments.remove(k)
                                del_set.add(k)
                        for k in del_set:
                            adg.arguments.remove(k)
            # step2: find and remove attack relations outcoming from out_set
            for i in out_set:
                del_set = set()
                for j in adg.relations:
                    if i[0] == j[0]:
                        # adg.relations.remove(j)
                        del_set.add(j)
                for j in del_set:
                    adg.relations.remove(j)
            # step3: find arguments still attacked and store in set atkd
            atkd = set()
            for i in adg.arguments:
                for j in adg.relations:
                    if i[0] == j[1]:
                        atkd.add(i[0])
            # step4: accept arguments attacked only by rejected arguments
            for i in adg.arguments:
                if i[0] not in atkd:
                    in_set.add(i)
                    #remove i from arguments
                    # adg.arguments.remove(i)
                else:
                    # no accepted arguments then stop while loop
                    Flag = False
    except Exception as e:
        print(f"An exception occurred: {e}")

    #put rest of the arguments in und_set
    for i in adg.arguments:
        und_set.add(i)
    return {'in': in_set, 'out': out_set, 'und': und_set}


def predict(adg, t):
    v = verified(adg, t)
    l = grounded(v)
    if len(l['in']) > 0:
        for i in l['in']:
            if i[1] != 'und':
                return i[1]
    else:
        if (len(l['und']) > 0):
            return 'und'
    return 'unk'

# read from csv to pandas dataframe and then extract and return distinct feature_value pairs 
def read_data_to_pairs(file):
    #feature_value pairs of tuple (feature_name,value)
    feature_value_pairs = set()
    df = pd.read_csv(file,sep=';')

    #print titles of the dataframe
    print(df.columns)
    print(df.shape)
    #print first few entries of the dataframe
    print(df.head())

    # for i in df.columns:
    #     if (i == 'y'):
    #         print('y is found')

    #remove column 'y' from the dataframe
    df = df.drop(columns=['y'])
    
    #extract distinct feature_value pairs
    for i in df.columns:
        # cnt = 0
        for j in df[i].unique():
            feature_value_pairs.add((i,j))
            #print(i,j)
            # cnt += 1
            # if cnt > 5:
            #     break
    return feature_value_pairs

def evaluate(adg, t=T, y=Y):
    correct = 0

    #print(t)

    for i in range(len(t)):
        if y[i] == 'yes':
            if (predict(adg, t[i]) == 1):
                correct += 1
        elif y[i] == 'no':
            if (predict(adg, t[i]) == 0):
                correct += 1
    return correct / df.shape[0]

def add_argument(adg, a):
    print('trying to add_argument:', a)
    for b in adg.arguments:
        
        adg_in = copy.deepcopy(adg)
        adg_out = copy.deepcopy(adg)
        adg_bi = copy.deepcopy(adg)
        
        adg_in.arguments.add(a)
        adg_in.relations.add((a, b))
        
        adg_out.arguments.add(a)
        adg_out.relations.add((b, a))
        
        adg_bi.arguments.add(a)
        adg_bi.relations.add((a,b))
        adg_bi.relations.add((b,a))
        
        print("eval relations between:", a, b)
        
        if (a[0][0] != b[0][0]) and (a[1] != b[1]) and (a[1] != 'und') and (b[1] != 'und'):
            # evaluate adg_in, adg_out, and adg_bi, return the best one of these 3
            if evaluate(adg_in) > evaluate(adg_out):
                adg = adg_in
            else:
                adg = adg_out
            if evaluate(adg_bi) > evaluate(adg):
                adg = adg_bi
        elif (a[0][0] != b[0][0]):
            # evaluate adg_in, adg_out, adg_bi and adg, return the best one of these 4
            if evaluate(adg_in) > evaluate(adg):
                adg = adg_in    
            if evaluate(adg_out) > evaluate(adg):    
                adg = adg_out
            if evaluate(adg_bi) > evaluate(adg):
                adg = adg_bi
    return adg

def train(threshold, dataset=CSV_FILE):
    # get current timestamp
    ts = time.time()

    perf = 0
    arg = set()
    fvps = read_data_to_pairs(dataset)

    # print nums of args to be added
    print(len(fvps)*3, "arguments to be added")

    #iterate thru fvp
    for fvp in fvps:
        arg.add((fvp, 1))
        arg.add((fvp, 0))
        arg.add((fvp, 'und'))
    adg_old = ArgumentationDecisionGraph(set(), set())
    adg_old.arguments.add((('age', 30), 0))
    while len(arg) > 0:
        adg_best = copy.deepcopy(adg_old)
        del_list = set()
        print(math.factorial(len(fvps)*3 - len(arg))/math.factorial(len(fvps)*3)*100, "% done")
        for a in arg:
            #calc time passsed in seconds
            print("time passed: ", time.time() - ts, " seconds")

            adg_old = copy.deepcopy(adg_best)
            adg_new = add_argument(adg_best, a)
            perf_new = evaluate(adg_new)
            if perf_new > perf + threshold:
                perf = perf_new
                adg_best = adg_new
                print("perf_new: ", perf_new)
                # arg.remove(a)
                del_list.add(a)

        for a in del_list:
            arg.remove(a)
        
        if (adg_best.arguments == adg_old.arguments) and (adg_best.relations == adg_old.relations):
            return adg_best
        
        return adg_best

    

# if is executed as a script run main
if __name__ == '__main__':
    #print('hello')
    model = train(0.005, CSV_FILE)
    print(model.arguments, model.relations)
    pass