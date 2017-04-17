
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
    return map(reduceTuple, clusters)

def printer(someIterable):
    for index,item in enumerate(someIterable):
        print("{}. {}\n\n".format(index,item))


def main():
    readHistory()
    printer(readClusters())


if __name__ == '__main__':
    main()
