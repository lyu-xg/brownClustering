
def getPYON(path):
    with open(path) as infile:
        return eval(infile.read())

def reduceTuple(t):
    return tuple(map(lambda x:x[0], t))

def readHistory():
    history = getPYON('savedHistory.pyon')
    return map(reduceTuple, history)

def readClusters():
    clusters = getPYON('savedClusters.pyon')
    return map(reduceTuple,clusters.values())

def printer(someIterable):
    for index,item in enumerate(someIterable):
        print("{}. {}\n with length {}".format(index+1,item,len(item)))

def generateClusters(history):
    print('got {} history entries'.format(len(history)))
    C = {}
    for m1,m2 in history:
        if   m1 not in C and m2 in C:
            C[m2] += [m1]
        elif m1 not in C and m2 not in C:
            C[m1] = [m1,m2]
        elif m1 in C     and m2 not in C:
            C[m1].append(m2)
        elif m1 in C     and m2 in C:
            C[m1] += C[m2]
            del C[m2]
    print('got {} clusters in total'.format(len(C)))
    return C

def main():
    #history = readHistory()
    #c = generateClusters(history)
    printer(readClusters())


if __name__ == '__main__':
    main()
