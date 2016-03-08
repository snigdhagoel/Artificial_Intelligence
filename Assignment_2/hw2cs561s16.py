# imports 
import argparse
import re
from copy import deepcopy

output = open("output.txt", "w")

class Predicate:
    
    def __init__(self, name, nargs):
        self.name = name
        self.nargs = nargs
        self.negation = False
        self.vargs = []
        
    def isNegation(self):
        return self.negation

class Clause:
    
    def __init__(self, fact=False):
        self.lhs = []
        self.rhs = None
        self.fact = fact
        
    def addLhs(self, predicate):
        self.lhs.append(predicate)
        return
    
    def addRhs(self, predicate):
        self.rhs = predicate
        return

    def isFact(self):
        return self.fact

def printToOutput(qoa, query):
    ostr = query.name + "("
    if query.vargs[0][0].islower():
        ostr = ostr + "_"
    else:
        ostr = ostr + query.vargs[0]
    for i in range(1, query.nargs):
        if query.vargs[i][0].islower():
            ostr = ostr + ", " + "_"
        else:
            ostr = ostr + ", " + query.vargs[i]
    ostr = ostr + ")\n" 
    output.write(qoa + ": " + ostr)


def fol_ask_query(clauses, query):
    for resQuery in fol_or(clauses, query):
        if resQuery == None:
            printToOutput(str(False), query)
            return False
        else:
            printToOutput(str(True), resQuery)
            return True
    printToOutput(str(False), query)
    return False
        
def fol_ask(clauses, queries):
    
    for query in queries:
        if fol_ask_query(clauses, query) == False:
            return False
            
    return True


def fol_or_reverted(matchedClauses, index, query):
    
    return

def fol_or(origClauses, query):
    clauses = deepcopy(origClauses)
    matchedClauses = match_clauses(clauses, query)
    origQuery = deepcopy(query)
    if len(matchedClauses) == 0:
        printToOutput("Ask", query)
        yield None
    for clause in matchedClauses:
        printToOutput("Ask", query)
        # clause is fact
        if clause.isFact() == True:
            #isSubstituted = False
            subMap = {}
            ret = True
            newQuery = deepcopy(query)
            if clause.rhs.nargs == query.nargs and clause.rhs.vargs != query.vargs:
                for i in range(clause.rhs.nargs):
                    if clause.rhs.vargs[i] != query.vargs[i] and query.vargs[i][0].islower():
                        subMap[query.vargs[i]] = clause.rhs.vargs[i]
                        #isSubstituted = True
                    elif clause.rhs.vargs[i] != query.vargs[i] and query.vargs[i][0].isupper():
                        ret = False
                if ret == False:
                    continue
                
                for i in range(newQuery.nargs):
                    if newQuery.vargs[i] in subMap.keys():
                        newQuery.vargs[i] = subMap[query.vargs[i]]
            #return ret, isSubstituted, query
            yield newQuery
        # clause is => : have to perform and search
        else:
            copyClause = deepcopy(clause)
            copyQuery = deepcopy(query)
            unify(copyQuery, copyClause)
            for subMapA in fol_and(copyClause.lhs, origClauses):
#                 if subMapA == None:
#                     query = deepcopy(origQuery)
#                     break
#                 else:
#                     substituteRHS(copyClause.rhs, subMapA)
#                     if equals(query, copyClause.rhs):
#                         substituteQuery(copyClause.rhs, query)
#                         #return True, True, query
#                         yield query
                if subMapA != None:
                    newCopyClause = deepcopy(copyClause)
                    substituteRHS(newCopyClause.rhs, subMapA)
                    if equals(query, newCopyClause.rhs):
                        newQuery = deepcopy(query)
                        substituteQuery(newCopyClause.rhs, newQuery)
                        #return True, True, query
                        yield newQuery
                else:
                    query = deepcopy(origQuery)
                    break
            #if resGot == False:
            #   query = deepcopy(origQuery)
                    
    #yield None
    return            
    #return False, False, query

def substituteQuery(rhs, query):
    for i in range(query.nargs):
        if query.vargs[i][0].islower() and rhs.vargs[i][0].isupper():
            query.vargs[i] = rhs.vargs[i]
    return

def equals(query, rhs):
    for j in range(rhs.nargs):
        if rhs.vargs[j] != query.vargs[j]:
            if rhs.vargs[j].isupper() and query.vargs[j].isupper():
                return False
    return True
    

def fol_and(lhsQueriesOrig, origClauses):
    subMapForAnd = {}
    if len(lhsQueriesOrig) == 0:
        yield subMapForAnd
    else:
        lhsQueries = deepcopy(lhsQueriesOrig)
        firstQuery = lhsQueries[0]
        restAll = lhsQueries[1:]
        oldQuery = deepcopy(firstQuery)
        for resQuery in fol_or(origClauses, firstQuery):
            if resQuery == None:
                printToOutput("False", firstQuery)
                yield None
                return
            else:
                printToOutput("True", resQuery)
                restAllCopy = deepcopy(restAll)
                subMap = substituteLHS(restAllCopy, oldQuery, resQuery)
                subMapForAnd.update(subMap)
                for subMapO in fol_and(restAllCopy, origClauses):
                    if subMapO != None and len(subMapO) > 0:
                        subMapForAnd.update(subMapO)
                    if subMapO == None:
                        firstQuery = deepcopy(oldQuery)
                        break
                    yield subMapForAnd
               
            #yield subMapForAnd
        yield None
        return            

def substituteRHS(rhs, subMapA):
    for j in range(rhs.nargs):
        if rhs.vargs[j] in subMapA.keys():
            rhs.vargs[j] = subMapA[rhs.vargs[j]]

def substituteLHS(lhsQueries, oldQuery, query):
    
    subMap = {}
    for i in range(oldQuery.nargs):
        if oldQuery.vargs[i][0].islower() and query.vargs[i][0].isupper():
            subMap[oldQuery.vargs[i]] = query.vargs[i]
    
    for pred in lhsQueries:
        for j in range(pred.nargs):
            if pred.vargs[j] in subMap.keys():
                pred.vargs[j] = subMap[pred.vargs[j]]
    
    return subMap

def unify(query, clause):
    varMap = {}
    for i in range(query.nargs):
        if query.vargs[i][0].isupper() and clause.rhs.vargs[i][0].islower():
            varMap[clause.rhs.vargs[i]] = query.vargs[i]
            clause.rhs.vargs[i] = query.vargs[i]
            
    for pred in clause.lhs:
        for j in range(pred.nargs):
            if pred.vargs[j] in varMap.keys():
                pred.vargs[j] = varMap[pred.vargs[j]]
    
    return query, clause

def match_clauses(clauses, query):
    matchedClauses = []
    for clause in clauses:
        rhsClause = clause.rhs
        if rhsClause.name == query.name:
            add = True
            for i in range(rhsClause.nargs):
                if rhsClause.vargs[i][0].isupper() and query.vargs[i][0].isupper() and rhsClause.vargs[i] != query.vargs[i]:
                    add = False
            if add:
                matchedClauses.append(clause)
    return matchedClauses

def extractQueries(queryStr):
    
    queries = queryStr.split('&&')
    queryPreds = []
    for i in range(len(queries)):
        qStr = queries[i].strip(' \t\n\r')
        qReg = re.compile(r'(.*)\((.*)\)')
        qu = qReg.search(qStr)
        predName = qu.group(1).strip(' \t\n\r')
        predVar = qu.group(2).strip(' \t\n\r').split(',')
        pred = Predicate(predName, len(predVar))
        for j in range(len(predVar)):
            pred.vargs.append(predVar[j].strip(' \t\n\r'))
        queryPreds.append(pred)
        
    return queryPreds

def parseLHS(lhsStr, clause):
    lhsClauses = lhsStr.split('&&')
    for cStr in lhsClauses:
        cStr = cStr.strip(' \t\n\r')
        cReg = re.compile(r'(.*)\((.*)\)')
        factStr = cReg.search(cStr)
        predName = factStr.group(1).strip(' \t\n\r')
        predVar = factStr.group(2).strip(' \t\n\r').split(',')
        if predName[0] == '~':
            pred = Predicate(predName[1:], len(predVar))
            pred.negation = True
        else:
            pred = Predicate(predName, len(predVar))
        for j in range(len(predVar)):
            pred.vargs.append(predVar[j].strip(' \t\n\r'))
        clause.addLhs(pred)
    return

def parseRHS(rhsStr, clause):
    cReg = re.compile(r'(.*)\((.*)\)')
    factStr = cReg.search(rhsStr)
    predName = factStr.group(1).strip(' \t\n\r')
    predVar = factStr.group(2).strip(' \t\n\r').split(',')
    if predName[0] == '~':
        pred = Predicate(predName[1:], len(predVar))
        pred.negation = True
    else:
        pred = Predicate(predName, len(predVar))
    for j in range(len(predVar)):
        pred.vargs.append(predVar[j].strip(' \t\n\r'))
    clause.addRhs(pred)
    return

# main
if __name__ == "__main__":
    clauses = []
    queries = []
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True)
    args = parser.parse_args()
    inFile = args.i
    inF = open(inFile, 'r')
    dataLines = inF.readlines()
    queries = extractQueries(dataLines[0])
    numClauses = int(dataLines[1])
    for i in range(0, numClauses):
        clauseStr = dataLines[2+i].strip(' \t\n\r').split('=>')
        if len(clauseStr) == 2:
            clause = Clause()
            parseLHS(clauseStr[0].strip(' \t\n\r'), clause)
            parseRHS(clauseStr[1].strip(' \t\n\r'), clause)
            clauses.append(clause)
        else:
            clause = Clause(fact=True)
            parseRHS(clauseStr[0], clause)
            clauses.append(clause)
    
    ret = fol_ask(clauses, queries)
    output.write(str(ret))
    