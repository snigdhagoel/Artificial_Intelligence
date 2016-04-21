import argparse
from math import pow
from copy import deepcopy

positionMapping = {"+":0, "-":1, "++":0, "+-":1, "-+":2, "--":3, "+++":0, "++-":1, "+-+":2, "+--":3, "-++":4, "-+-":5, "--+":6, "---":7}
output = open("output.txt", "w")
utilityNode = []
decisionNodes = []

class Query:
    
    type = ""
    variables = []
    evidences = []
    variableMap = {}
    evidenceMap = {}
    
    def __init__(self):        
        self.type = ""
        self.variables = []
        self.evidences = []
        self.variableMap = {}
        self.evidenceMap = {}
    

class Node:
    
    def __init__(self, name):
        self.name = name
        self.parents = []
        self.children = []
        self.CPT = []
        self.decision = False
        
    def addchild(self, child):
        if not child in self.children:
            self.children.append(child)

    def addParent(self, parent):
        if not parent in self.parents:
            self.parents.append(parent)
    
    def addTable(self, inputProbs):
        if len(self.parents) == 0:
            self.CPT.append(float(inputProbs[0].strip(' \t\r\n')))
        else:
            size = int(pow(2, len(self.parents)))
            self.CPT = [None] * size
            for idx in range(size):
                if not inputProbs[idx].strip(' \t\n\r') == "":
                    pRow = inputProbs[idx].strip(' \t\n\r').split(' ')
                    tableIdx = positionMapping[''.join(pRow[1:])]
                    self.CPT[tableIdx] = float(pRow[0])
    
    def setDecisionTrue(self):
        self.decision = True
                
    def isDecision(self):
        return self.decision
        
    def printNode(self):
        print self.name
        pstr = ""
        for parent in self.parents:
            pstr += (parent.name + " ")
        print pstr
        cstr = ""
        for child in self.children:
            cstr += (child.name + " ")
        print cstr
        print self.CPT

class BayesNet:
    
    def __init__(self):
        self.nodeMap = {}
        self.nodeList = []
        
    def parseAndAddNode(self, inputs):
        nodeNames = inputs[0].split('|')
        name = nodeNames[0].strip(' \t\r\n')
        newNode = Node(name)
        if len(nodeNames) == 2:
            parentNodes = nodeNames[1].strip(' \t\r\n').split(' ')
            for parent in parentNodes:
                pNode = self.nodeMap[parent.strip(' \t\n\r')]
                newNode.addParent(pNode)
                pNode.addchild(newNode)
        if inputs[1].strip(' \t\r\n') == "decision":
            newNode.setDecisionTrue()
            decisionNodes.append(newNode)
        else:
            newNode.addTable(inputs[1:])
        self.nodeMap[name] = newNode
        self.nodeList.append(newNode)
        if newNode.name == "utility":
            utilityNode.append(newNode)

    def parseInputGraph(self, data):
        
        startIdx = 0;
        for idx in range(len(data)):
            if data[idx].startswith("***"):
                self.parseAndAddNode(data[startIdx:idx])
                startIdx = idx + 1
        
        if startIdx < idx:
            self.parseAndAddNode(data[startIdx:])
        
    def calculate_probability(self, varNode, evidenceMap):

        if varNode.isDecision():
            return 1
        indexesToBeAdded = []
        if len(varNode.parents) == 0:
            indexesToBeAdded.append("+")
        else:
            indexesToBeAdded.append("")
        for parent in varNode.parents:
            indexesNew = []
            if parent.name in evidenceMap.keys():
                valParent = evidenceMap[parent.name]
                for index in range(len(indexesToBeAdded)):
                    indexesNew.append(indexesToBeAdded[index] + valParent)
            else:
                for index in range(len(indexesToBeAdded)):
                    indexesNew.append(indexesToBeAdded[index] + "+")
                    indexesNew.append(indexesToBeAdded[index] + "-")
            indexesToBeAdded = indexesNew
        totalProb = 0
        for stri in indexesToBeAdded:
            totalProb += varNode.CPT[positionMapping[stri]]
        if evidenceMap[varNode.name] == "+":
            return totalProb
        else:
            return 1 - totalProb
    
    def displayNodes(self):
        for node in self.nodeList:
            node.printNode()

def enumeration_ask(query, bayes_net):
        
    queryNum, queryDen = convertToJoint(query)
    evidence_vars = deepcopy(queryNum.evidenceMap)
    evidence_vars.update(queryNum.variableMap)
    queryNumMap = deepcopy(evidence_vars)
    if query.type == "EU":
        evidence_vars[utilityNode[0].name] = "+"
    prob = enumerate_all(bayes_net, bayes_net.nodeList, evidence_vars)
    if queryDen != None:
        evidence_vars = deepcopy(queryDen.evidenceMap)
        evidence_vars.update(queryDen.variableMap)
        for dNode in decisionNodes:
            evidence_vars[dNode.name] = queryNumMap[dNode.name]
            
        if query.type == "EU":
            probDen = enumerate_all(bayes_net, bayes_net.nodeList[:-1], evidence_vars)
        else:
            probDen = enumerate_all(bayes_net, bayes_net.nodeList, evidence_vars)
        prob = prob / probDen
    print prob
    if query.type == "P":
        prob += 0.000000000000001
        prob = format(prob, '.2f')
    else:
        prob = int(prob + 0.5)
    print prob
    output.write(str(prob) + "\n")

def allCombinations(query):
    combinations = [{}]
    for variable in query.variables:
        if variable in query.variableMap.keys():
            continue
        newList = []
        for idx in range(len(combinations)):
            newMapT = dict(combinations[idx])
            newMapT[variable] = "+"
            newList.append(newMapT)
            newMapF = dict(combinations[idx]) 
            newMapF[variable] = "-"
            newList.append(newMapF)
        combinations = newList
    return combinations
            

def enumeration_ask_MEU(query, bayes_net):
    
    allCombs = allCombinations(query)
    maxUtilValue = float('-inf')
    for comb in allCombs:
        queryNum, queryDen = convertToJoint(query)
        evidence_vars = deepcopy(queryNum.evidenceMap)
        evidence_vars.update(queryNum.variableMap)
        evidence_vars.update(comb)
        evidence_vars[utilityNode[0].name] = "+"
        queryNumMap = deepcopy(evidence_vars)
        prob = enumerate_all(bayes_net, bayes_net.nodeList, evidence_vars)
        if queryDen != None:
            evidence_vars = {}
            evidence_vars.update(queryDen.variableMap)
            evidence_vars.update(comb)
            evidence_vars[utilityNode[0].name] = "+"
            probDen = enumerate_all(bayes_net, bayes_net.nodeList[:-1], evidence_vars)
            prob = prob / probDen
        if prob > maxUtilValue:
            maxUtilValue = prob
            decisionQueryMap = comb
    stro = ""
    #print maxUtilValue
    for variable in query.variables:
        if variable not in query.variableMap.keys():
            stro += decisionQueryMap[variable] + " "
    stro += str(int(maxUtilValue + 0.5))
    output.write(stro + "\n")


def convertToJoint(query):
    if len(query.evidences) == 0:
        return query, None
    queryDen = Query()
    queryDen.variables = deepcopy(query.evidences)
    queryDen.variableMap = deepcopy(query.evidenceMap)
    
    return query, queryDen

def enumerate_all(bayes_net, variablesRem, evidenceMap):
    if len(variablesRem) == 0:
        return 1;
    else:
        var = variablesRem[0]
        if var.name in evidenceMap.keys():
            prob = bayes_net.calculate_probability(var, evidenceMap)
            return prob * enumerate_all(bayes_net, variablesRem[1:], evidenceMap)
        else:
            evidence_clone = deepcopy(evidenceMap)
            evidence_clone[var.name] = "+"
            probTrue = bayes_net.calculate_probability(var, evidence_clone)
            second_term = enumerate_all(bayes_net, variablesRem[1:], evidence_clone)
            true_probability_var = probTrue * second_term
            evidence_clone[var.name] = "-"
            probFalse = bayes_net.calculate_probability(var, evidence_clone)
            second_term = enumerate_all(bayes_net, variablesRem[1:], evidence_clone)
            false_probability_var = probFalse * second_term
            return true_probability_var + false_probability_var


def parseQuery(query, inp):
    vars = inp.split('|')
    queryVars = vars[0].strip(' \t\n\r').split(',')
    for queryVar in queryVars:
        eqSplit = queryVar.strip(' \t\n\r').split('=')
        query.variables.append(eqSplit[0].strip(' \t\n\r'))
        query.variableMap[eqSplit[0].strip(' \t\n\r')] = eqSplit[1].strip(' \t\n\r')
    if len(vars) > 1:
        evidenceVars = vars[1].strip(' \t\n\r').split(',')
        for evVar in evidenceVars:
            eqSplit = evVar.strip(' \t\n\r').split('=')
            query.evidences.append(eqSplit[0].strip(' \t\n\r'))
            query.evidenceMap[eqSplit[0].strip(' \t\n\r')] = eqSplit[1].strip(' \t\n\r')

def parseMEUQuery(query, inp):
    vars = inp.split('|')
    queryVars = vars[0].strip(' \t\n\r').split(',')
    for queryVar in queryVars:
        eqSplit = queryVar.strip(' \t\n\r').split('=')
        query.variables.append(eqSplit[0].strip(' \t\n\r'))
        if len(eqSplit) > 1:
            query.variableMap[eqSplit[0].strip(' \t\n\r')] = eqSplit[1].strip(' \t\n\r')
    if len(vars) > 1:
        evidenceVars = vars[1].strip(' \t\n\r').split(',')
        for evVar in evidenceVars:
            eqSplit = evVar.strip(' \t\n\r').split('=')
            query.evidences.append(eqSplit[0].strip(' \t\n\r'))
            query.evidenceMap[eqSplit[0].strip(' \t\n\r')] = eqSplit[1].strip(' \t\n\r')


def parseQueries(input):
    queries = []
    for str in input:
        query = Query()
        if str.startswith("P"):
            query.type = "P"
            parseQuery(query, str.strip(' \t\n\r')[2:-1])
        elif str.startswith("EU"):
            query.type = "EU"
            parseQuery(query, str.strip(' \t\r\n')[3:-1])
        elif str.startswith("MEU"):
            query.type = "MEU"
            parseMEUQuery(query, str.strip(' \t\r\n')[4:-1])
        
        queries.append(query)
    return queries

# main
if __name__ == "__main__":
    nodeMap = {}
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True)
    args = parser.parse_args()
    inFile = args.i
    inF = open(inFile, 'r')
    dataLines = inF.readlines()
    bayes_net = BayesNet()
    for index in range(len(dataLines)):
        if dataLines[index].strip(' \t\r\n') == "******":
            break
    queries = parseQueries(dataLines[0:index])
    bayes_net.parseInputGraph(dataLines[index+1:])
    for query in queries:
        if query.type == "MEU":
            enumeration_ask_MEU(query, bayes_net)
        else:
            enumeration_ask(query, bayes_net)
    
    output.seek(0,2)
    nsize = output.tell()
    output.truncate(nsize-2)
        
    