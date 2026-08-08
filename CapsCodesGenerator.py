import numpy as np 
import pandas as pd # for making useful tables later, if we need them for the paper to provide exs 
from itertools import combinations
from isomorphicSolver import *

########################################
########### Helper Functions ###########
########################################

class AffineVector(list):
    def __add__(self, other):
        if not isinstance(other, AffineVector):
            return NotImplemented

        # Elements that appear in exactly one of the lists
        result = [x for x in self if x not in other]
        result.extend(x for x in other if x not in self)

        result.sort()

        return AffineVector(result)

    # compares 2 affine vectors and returns a list of elements common between them 
    def overlap(self, other):
        if not isinstance(other, AffineVector):
            return NotImplemented
        
        result = [x for x in self if x in other]
        result.sort()
        return AffineVector(result)

def capCheck(dependentSet):
    # Should iterate through each combination of 2, 3, or 4 vectors (can assume they will only be 5, 7 or 9 sums) within a list of AffineVectors and, if any of them make a quad, will return False.
    # Otherwise will return True.
    # dependentSet must have at least two vectors
    isCap = True

    #Check pairs
    for i in range(len(dependentSet)):
        for j in range(i+1, len(dependentSet)):
            if (len(dependentSet[i]+dependentSet[j]) == 2) or (len(dependentSet[i]+dependentSet[j]) == 0):
                isCap = False

    #Check triples
    if len(dependentSet) >= 3:
        for i in range(len(dependentSet)):
            for j in range(i+1, len(dependentSet)):
                for k in range(j+1, len(dependentSet)):
                    if len(dependentSet[i] + dependentSet[j] + dependentSet[k]) == 1:
                        isCap = False
    
    #Check quadruples
    if len(dependentSet) >= 4:
        for i in range(len(dependentSet)):
            for j in range(i+1, len(dependentSet)):
                for k in range(j+1, len(dependentSet)):
                    for l in range(k+1, len(dependentSet)):
                        if len(dependentSet[i] + dependentSet[j] + dependentSet[k]+dependentSet[l]) == 0:
                            isCap = False

    return isCap

def findOverlap(vectorList):
    if len(vectorList) == 1:
        return vectorList[0]
    out = AffineVector.overlap(vectorList[0], vectorList[1])
    for i in range(2, len(vectorList)):
        out = AffineVector.overlap(vectorList[i], out)
    return out

# As we are testing for quad-256 caps, we are in dimension 8, so our affine basis contains 9 elements. 
# compiles the lists of every possible combinations of vectors with 5, 7, and 9 elements in reference to our 9 basis elements  
def listDSet():
    dSet = []
    X9 = AffineVector([1,2,3,4,5,6,7,8,9]) 

    for combo in combinations(range(1,10), 5):
        dSet.append(AffineVector(combo))
    for combo in combinations(range(1,10), 7):
        dSet.append(AffineVector(combo))
    dSet.append(X9)
    
    return dSet

'''
looks through our dependent set of vectors for the k-caps(caps with k elements) we are looking at rn and finds all of the possible 
unordered/ordered codes we can generate for them. If we 
'''
def codeFinder(lists):

    # list of affine basis elements 
    patterns = {i: "" for i in range(1, 10)}

    # adds x1 to x9 to patterns 
    for i in range(len(lists)):
        patterns[f"x{i+1}"] = ""

    for current_list in lists:

        ''' 
        for each dependent vector, we check whether or not it contains a number from 1-9 bc our affine basis has 9 elements 
        If it does, then we'll append a 1, and likewise a 0 to signify that the current vector doesn't contain that element. 
        This allows us to keep track of which elements in the affine basis are shared between the dependent vectors
        '''
        for num in range(1, 10):
            if num in current_list:
                patterns[num] += "1"
            else:
                patterns[num] += "0"

        '''
        essentially, we are marking down all of the dependent set's vectors and adding them to patterns. think of 
        them like in our tables where they have a single 1 per column 
        '''
        for i in range(len(lists)):
            if current_list == lists[i]:
                patterns[f"x{i+1}"] += "1"
            else:
                patterns[f"x{i+1}"] += "0"

    ''' 
    counts contains every binary number depending on the amount of elements in our dependent set, so if we have 2, then we'll go from
    00 to 11.
    Then we iterate through each of the binary numbers that we assembled in patterns(think like going down the columns of our table) 
    and mark them as present in counts. 
    '''
    counts = {f"{i:0{len(lists)}b}": 0 for i in range(1 << len(lists))}
    for pattern in patterns.values():
        counts[pattern] += 1

    # checks if  more than 1 element in the affine basis is not used - which means that it must be in a lower dimension 
    if next(iter(counts.values())) != 0:
        return "Lower Dimension"

    out = []
    for pattern in counts:
        out.append(str(counts.get(pattern, 0)))
    # out.sort()    #### Comment this line out when you're trying to get unordered codes instead of ordered codes
    
    #returns the complete code we got 
    return "".join(out)

'''
Names a cap using the sum of every dependent vector, followed by the overlap between each pairing of those vectors. 
For example, say we were working with 11 caps, where we define our dependent set as {x, y}. If x and y both are sums of 7, and overlap 5
times, then we can name this cap 7-7-(5). The number(s) outlined in parentheses represent the overlap between the vectors, and the numbers to
the left of them represent the sums of the dependent vectors. 
'''
def capNamer(inputCap):
    sizes = []
    OLs = []

    #iterates over the number of elements in the cap 
    for chooseK in range(len(inputCap)):
        overlapK = [] # tracks the number of overlapping elements per each set of combinations

        ''' 
          iterates through every possible set of combinations  of chooseK + 1 elements in our cap. if chooseK = 0, then we update sizes
        with the number of elements in the 1st combo.
        Otherwise, we update overlapK by adding the number of overlapping elements in the current set to it
      
        '''
        for subset in combinations(inputCap, chooseK + 1):
            if chooseK == 0:
                sizes.append(len(subset[0]))
            else:
                overlapK.append(len(findOverlap(subset)))

        # assuming that chooseK isn't 0, then we sort the entire list of overlap and put it in decreasing order before adding it to OLs
        if chooseK != 0:
            overlapK.sort(reverse = True) 
            OLs.append(overlapK)

    # puts sizes in numerical order 
    sizes.sort(reverse = True) 
    label = ""

    # adding sums for each vector in the dependent set 
    for ele in sizes:
        label += f"{ele}-"
    label += "("

    # adds all the overlap parts for each pairing 
    for overlapType in range(len(OLs)):
        overlay = OLs[overlapType]
        for idx in range(len(overlay)):
            if idx+1 != len(overlay):
                label+= f"{overlay[idx]}-"
            elif overlapType+1 != len(OLs):
                label += f"{overlay[idx]}, " 
            else:
                label += f"{overlay[idx]})"
    return label

#old vennCode, disregard this
'''
     def vennCoder(inputCap):
         vennCode = []

         for chooseK in range(len(inputCap)):
              for vennBubble in combinations(inputCap, chooseK+1):
                # Choosing our initial combination
                   if len(vennBubble) == 1:
                         bubbleSize = 1 + len(findOverlap(vennBubble))
                   else:
                         bubbleSize = 0 + len(findOverlap(vennBubble))

                 for largerSize in range(chooseK + 2, len(inputCap) + 1):
                     for combo in combinations(inputCap, largerSize):
                          if all(ele in combo for ele in vennBubble):
                                if (len(combo) - len(vennBubble)) % 2 == 1:
                                        bubbleSize -= len(findOverlap(combo))
                          else: 
                              bubbleSize += len(findOverlap(combo))
                     vennCode.append(bubbleSize)
          vennCode.sort(reverse=True)    
          return vennCode '''

def vennCoder(inputCap):
    vennCode = []
    n = len(inputCap)

    # Cache intersections so we don't calculate the same overlap repeatedly
    overlapCache = {}

    def cachedOverlap(indices):
        # Use vector positions as the key
        if indices not in overlapCache:
            vectors = tuple(inputCap[i] for i in indices)
            overlapCache[indices] = findOverlap(vectors)

        return overlapCache[indices]

    for k in range(1, n + 1):
        for bubbleIndices in combinations(range(n), k):

            # Initial intersection
            bubbleSize = len(cachedOverlap(bubbleIndices))

            # Singleton bubbles count themselves
            if k == 1:
                bubbleSize += 1

            # Inclusion-exclusion over larger supersets
            for largerSize in range(k + 1, n + 1):
                for superIndices in combinations(range(n), largerSize):

                    # Check whether this is actually a superset
                    if not all(i in superIndices for i in bubbleIndices):
                        continue

                    overlapSize = len(cachedOverlap(superIndices))

                    # Alternate subtraction/addition
                    if (largerSize - k) % 2 == 1:
                        bubbleSize -= overlapSize
                    else:
                        bubbleSize += overlapSize

            vennCode.append(bubbleSize)

    vennCode.sort(reverse=True)
    return ''.join(map(str, vennCode))

#############################################
########### Testing early cases  ############
#############################################

def cap11Finder():
    combos = []
    caps = []
    codes = []
    for combo in combinations(listDSet(), 2):
        if capCheck(combo):

            xSum = combo[1]
            ySum = combo[0] 
            overlap = findOverlap(combo) 

            if f"{len(xSum)}-{len(ySum)}-({len(overlap)})" not in caps:
                caps.append(f"{len(xSum)}-{len(ySum)}-({len(overlap)})")
                # WLOG we can just append the first combination of each type. This should make it infinitely easier to iterate through higher cap-sizes.
                combos.append([ySum, xSum])
                currentCode = codeFinder([ySum, xSum])

                if currentCode not in codes: 
                    codes.append(currentCode) 

    caps.sort(reverse=True)
    codes.sort()
    return [combos, caps, codes]

def cap12Finder():
    combos = []
    caps = []
    codes = []
    combos11 = cap11Finder()[0] # need this because we can find some 12 caps using our previous findings from 11 caps 
    for x3 in listDSet():
        for cap11 in combos11:
            x1 = cap11[0]
            x2 = cap11[1]
            triple = [x1, x2, x3]
            if capCheck(triple):
                # sizes = [len(x1),len(x2),len(x3)]
                # sizes.sort(reverse=True)

                # OL2 = [len(findOverlap([x1,x2])),len(findOverlap([x1,x3])),len(findOverlap([x2,x3]))] #overlaps of pairs
                # OL2.sort(reverse=True)

                # if f"{sizes[0]}-{sizes[1]}-{sizes[2]}-({OL2[0]}-{OL2[1]}-{OL2[2]}, {len(findOverlap([x1,x2,x3]))})" not in caps:
                #     caps.append(f"{sizes[0]}-{sizes[1]}-{sizes[2]}-({OL2[0]}-{OL2[1]}-{OL2[2]}, {len(findOverlap([x1,x2,x3]))})")
                label = capNamer(triple)
                if label not in caps:
                    caps.append(label)
                    combos.append(triple) 
                    if codeFinder(triple) not in codes: 
                        codes.append(codeFinder(triple))

    caps.sort(reverse=True)
    codes.sort()
    return [combos, caps, codes]

def cap13Finder():
    combos = []
    caps = []
    codes = []
    combos12 = cap12Finder()[0]

    for x4 in listDSet():
        for cap12 in combos12:
            x1 = cap12[0]
            x2 = cap12[1]
            x3 = cap12[2]
            quad = [x1, x2, x3, x4] # no, not the quads from cards
            if capCheck(quad):
                label = capNamer(quad)
                code = codeFinder(quad)
                caps.append(label)
                combos.append(quad)
                if code not in codes:# and code != "Lower Dimension":
                    codes.append(code) 

    # caps.sort(reverse=True)
    # codes.sort()
    return [combos, caps, codes]

def cap14Finder():
    combos = []
    caps = []
    codes = []
    combos13 = cap13Finder()[0]

    for x5 in listDSet():
        for cap13 in combos13:
            x1 = cap13[0]
            x2 = cap13[1]
            x3 = cap13[2]
            x4 = cap13[3]
            quintet = [x1, x2, x3, x4, x5] 
            if capCheck(quintet):
                label = capNamer(quintet) 
                code = codeFinder(quintet) 
                if code not in codes:# and code != "Lower Dimension":
                    caps.append(label)
                    combos.append(quintet) 
                    codes.append(code)

    # caps.sort(reverse=True)
    # codes.sort()
    return [combos, caps, codes]

######################################################
### Generalizing to k-Caps and helpful information ###
######################################################

def kCapFinder(k):
    # Designed for k >= 11
    all = listDSet()
    combos = all
    caps = []
    codewords = []
  # venncodes = []

    for i in range(k-10):
        loopCombos = []
        loopCaps = []
        loopCodes = []
        # loopVenns = []
        for prevCombo in combos:
            for newEle in all:
                if i == 0:
                    currentSet = [prevCombo,newEle]
                else:
                    currentSet = prevCombo.copy()
                    currentSet.append(newEle)
                if capCheck(currentSet):
                    label = capNamer(currentSet)
                    code = codeFinder(currentSet)
                    # venn = vennCoder(currentSet)
                    if label not in loopCaps:
                        loopCaps.append(label)
                        loopCombos.append(currentSet)
                        if code not in loopCodes and code != "Lower Dimension":
                            loopCodes.append(code)
                        # if venn not in loopVenns:
                        #     loopVenns.append(venn)
        combos = loopCombos.copy()
        caps = loopCaps.copy()
        codewords = loopCodes.copy()
        # venncodes = loopVenns.copy()

    caps.sort(reverse=True)
    codewords.sort()
  # venncodes.sort(reverse=True)
    return [combos, caps, codewords]#, venncodes]

#displays the codes 
def showCodes(start,end):
    for i in range(start,end + 1):
        print(f"{i}-Cap Codes: {kCapFinder(i)[2]}\n")

def codesTable(n):
    """
    inputs: n, the size of the cap you're looking at (as in an n-Cap, not a dependent set of size n)
    outputs: a list of the form [a list of every possible cap-orientation, a list of corresponding codewords (unordered)]
    """
    table = []
    callList = kCapFinder(n)
    for idx in range(len(callList[0])):
        temp = callList[0]
        table.append([capNamer(temp[idx]), codeFinder(temp[idx]), temp[idx]])
    print(f"Cap Configurations ({len(callList[1])} Unique):")
    for config in table:
        print(config[0])
    print(f"\nCorresponding Templates ({len(temp)} Unique):")
    for config in table:
            print(config[2])
    print(f"\nCorresponding Codewords ({len(callList[2])} Unique):")
    for config in table:
        print(config[1])
    # classes = []
    # for i in range(len(table)):
    #     if [table[i][1],table[i][2]] not in classes:
    #         classes.append([table[i][1],table[i][2]])
    # print(f"\nUnique Classes ({len(classes)}):")
    # for ele in classes:
    #     print(f'{ele}')

codesTable(15)
# showCodes(11,14)
