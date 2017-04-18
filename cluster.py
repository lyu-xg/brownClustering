from parser import OUTPUT
from math import log
import os.path
from itertools import chain, combinations, permutations
from collections import Counter
from twoGramModel import TwoGramModel

DEBUG = True
DETAIL = False

class Clusters(object):
    def __init__(self, gramModel, wordlist, K=40):
        self.K = K
        self.M = gramModel
        self.allWords = set(wordlist)
        self.remainingWords = wordlist
        self.C = tuple((self.remainingWords.pop(),) for i in range(self.K+1))
        #self.countCache = {}
        #self.biCountCache = {}
        self.WCache = {}
        self.initL()
        if DEBUG: print('L table initialization complete.')
        self.mergeHistory = []
        self.initActualClusters()
    '''
    def calcAllWordPairs(self):
        pairs = combinations(self.allWords, 2)
        pairs = filter(lambda x:M.count(x[0],x[1]) or M.count(x[1],x[0]), pairs)
        self.wordPairs = tuple(pairs)
    '''

    def initActualClusters(self):
        self.actualClusters = {}
        for c in self.C:
            self.actualClusters[c] = [c]
        if DETAIL: print('initial clusters: {}'.format(self.actualClusters))

    def weight(self,c1,c2):
        biCount = self.BiCount(c1,c2)
        if not biCount:
            return 0
        individualCounts = self.count(c1) * self.count(c2)
        #print(biCount,individualCounts)
        return biCount*log((biCount*self.M.N)/individualCounts, 2)

    def W(self,c1,c2):

        if (c1,c2) in self.WCache:
            return self.WCache[(c1,c2)]

        if DETAIL:
            print('weight of {} and {}: '.format(c1,c2),self.weight(c1,c2)+self.weight(c2,c1))
        result = self.weight(c1,c2)
        if c1!=c2:
            result += self.weight(c2,c1)
        self.WCache[(c1,c2)] = result
        return result

    def count(self, c):
        '''
        if c[:-1] in self.countCache:
            result = self.countCache[c[:-1]]+self.M.count(c[-1])
        else:
            result = sum(self.M.count(w) for w in c)# or 0.1
        self.countCache[c] = result
        return result
        '''
        return sum(self.M.count(w) for w in c)

    def BiCount(self, c1, c2):
        '''
        if (c1[:-1],c2) in self.biCountCache:
            result = self.biCountCache[(c1[:-1],c2)]+sum(self.M.count(c1[-1],j) for j in c2)
        elif (c1,c2[:-1]) in self.biCountCache:
            result = self.biCountCache[(c1,c2[:-1])]+sum(self.M.count(i,c2[-1]) for i in c1)
        #if DETAIL: print('getting BiCount for {} and {}'.format(c1,c2))
        else:
            result = sum(self.M.count(i,j) for i in c1 for j in c2) #or 0.1
        self.biCountCache[(c1,c2)] = result
        return result
        '''
        return sum(self.M.count(i,j) for i in c1 for j in c2)


    def allClusterWords(self):
        return chain.from_iterable(self.C)

    def LFromScratch(self, c1, c2):
        W = self.W
        otherNodes = tuple(x for x in self.C if x!=c1 and x!=c2)
        return -W(c1,c2)-W(c1,c1)-W(c2,c2)+W(c1+c2,c1+c2) - \
                sum(W(c1,w) for w in otherNodes) - \
                sum(W(c2,w) for w in otherNodes) + \
                sum(W(c1+c2,w) for w in otherNodes)

    def recordActualClusters(self, m1, m2):
        C = self.actualClusters
        self.mergeHistory.append((m1,m2))
        if len(C) != 41:
            print('WARNING: actual clusters size {}, while recording {} and {}'.format(len(C),m1,m2))
        if m1 not in C or m2 not in C:
            print('WARNING: m1:{} or m2:{} both not cluster leaders'.format(m1,m2))
            if m1 not in C:
                print('\t\tm1 is not cluster leader')
            if m2 not in C:
                print('\t\tm2 is not cluster leader')
        C[m1]+=C[m2]
        del C[m2]

    def removeFromL(self,c1,c2):
        del self.L[(c1,c2)]
        del self.L[(c2,c1)]

    def MergeClusters(self, m1, m2):
        self.recordActualClusters(m1,m2)
        self.removeFromL(m1,m2)
        newNode = (self.remainingWords.pop(),)
        self.actualClusters[newNode] = [newNode]
        otherNodes = tuple(x for x in self.C if x not in (m1,m2))
        mergedNode = m1

        self.C = otherNodes+(mergedNode, newNode)
        for c1,c2 in combinations(otherNodes, 2):
            self.L[(c1,c2)] = self.LAfterMerge(c1,c2,m1,m2)
        self.M.merge(m1,m2)
        for node in otherNodes:
            self.removeFromL(node,m1)
            self.removeFromL(node,m2)
            self.L[(node,mergedNode)] = self.LFromScratch(node,mergedNode)
            self.L[(node,newNode)] = self.LFromScratch(node,newNode)
        self.L[(mergedNode,newNode)] = self.LFromScratch(mergedNode,newNode)

    def LAfterMerge(self, c1, c2, m1, m2):
        if (c1,c2) in self.L:
            prevValue = self.L[(c1,c2)]
        elif (c2,c1) in self.L:
            prevValue = self.L[(c2,c1)]
        else:
            print('WARNING: {} and {} not found in prevL'.format(c1,c2))
            raise AssertionError
            return self.LFromScratch(c1,c2)
        return prevValue - \
                sum(self.W(c,m) for c in (c1,c2) for m in (m1,m2)) + \
                sum(self.W(c,m1+m2) for c in (c1,c2))


    def MergeHighest(self):
        (winner1,winner2),quality = self.L.most_common(1)[0]
        if DEBUG:
            print('Merging {} and {} at {}'.format(winner1,winner2,quality))
        self.MergeClusters(winner1,winner2)
        self.WCache = {} # evict Weight cache for the next round of merge

    def lastMerge(self):
        (winner1,winner2),_ = self.L.most_common(1)[0]
        self.recordActualClusters(winner1,winner2)

    def initL(self):
        # L = change of Quality if c1 and c2 were to be Merged
        '''
        cacheDir = 'initialL.txt'
        if os.path.exists(cacheDir):
            with open(cacheDir) as infile:
                self.L = eval(infile.read())
            if DEBUG: print('loaded initlialzed L table from disk.')
            return
        '''
        if DEBUG: print('initializing L Table from scratch')

        self.L = Counter()
        clusterPairs = combinations(self.C, 2)
        for c1,c2 in clusterPairs:
            if DETAIL: print('calculating for cluster pair',c1,c2)
            self.L[(tuple(c1),tuple(c2))] = self.LFromScratch(c1,c2)
            if DETAIL: print('value being:',self.L[(tuple(c1),tuple(c2))])
        '''with open(cacheDir,'w') as outfile:
            outfile.write(repr(self.L))'''
        if DEBUG: print('L table initialized from scratch complete:')


    def saveProgress(self):
        with open('savedHistory.pyon','w') as outfile:
            outfile.write(repr(self.mergeHistory))
        with open('savedClusters.pyon','w') as outfile:
            outfile.write(repr(self.actualClusters))

    def keepMerging(self):
        print('initally',self.L.most_common(3))
        mergeNumber = 0
        while self.remainingWords:
        #for _ in range(100):
            if DEBUG:
                print('round',mergeNumber)
            mergeNumber+=1
            self.MergeHighest()
            recordNumber = mergeNumber%20
            if not recordNumber:
                self.saveProgress()

            if DETAIL:
                print('***************************************************')
                print('after merge:')
                print(self.C)
                print('\n\n\n')
        self.lastMerge()
        self.saveProgress()
        if DEBUG: print('All Merges complete.')
        #print('\n\nmerge history:',self.mergeHistory)


def main():
    with open(OUTPUT) as infile:
        WORDLIST = [line[:line.find(' ')] for line in infile]
    M = TwoGramModel(WORDLIST)
    C = Clusters(M, WORDLIST)
    '''
    for _ in range(200):
        C.MergeHighest()
    for c in C.actualClusters:
        print(c)
    print(M.count('a','thing'))
    print(M.count('an','thing'))
    M.merge('an','a')
    print(M.count('an','thing'))
    '''
    C.keepMerging()


if __name__ == '__main__':
    main()
    #print('initialized Clusters',C.C)
    #print('initialized L table',C.L)
