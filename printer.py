def getPYON(path):
    with open(path) as infile:
        return eval(infile.read())

def readBiCodes():
    return getPYON('savedBinaryStrings.pyon')

def readClusters():
    def reduceTuple(t):
        return tuple(map(lambda x:x[0], t))
    clusters = getPYON('savedClusters.pyon')
    return map(reduceTuple,clusters.values())

def clusterPrinter(c):
    for index,item in enumerate(c):
        print("{}. {}".format(index+1,item,len(item)))

def bicodePrinter(b):
    for word,code in b.items():
        print('{} - {}\n'.format(word,code))

def main():
    clusterPrinter(readClusters())
    bicodePrinter(readBiCodes())

if __name__ == '__main__':
    main()
