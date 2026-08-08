import numpy as np 

''' 

use pandas to construct a table maybe for the really hard to visualize stuff for the presentation / later on 
also need to design two functions - one that takes in 2 codes, another that takes 2 codes and a basis and determines whether they 
are equivalent or not(if yes, show it is an isomorphism ) 
test for 15 caps - it's only 0 and 1's, but we need to be able to permute them more efficiently so we can determine 
we don't want to remake the basis - cache the ones that you have already done (use dictionaries)
 add some kind of logic check for the ones you've already done

we have to map from one cap to another 
 '''



#tracks the pairs of binary codes we've alr tested for isomorphisms (make 2 separate keys for each code and provide them with a list of values) 
codePairings = {}  

basesUsed = {}

# this takes a k-cap and attempts to find a possible basis for it 
def findBasis(cap): 
    # need to check if the basis has  already been found so we don't use it again or can just use that one instead for whichever codes we're comparing 
    basis = []

    if basis not in basesUsed:
        basesUsed[basis] = cap 
    return basis 

''' this takes in 2 separate codes for caps and checks if their sorted codes are the same. if not, then the 2 caps are obviously not
isomorphic '''
def compareCodes(code1, code2):
    return sorted(code1) == sorted(code2) 


'''trying to check if these caps are isomorphic or not so we can try to figure out wha ttheir equiv class is''' 
def isIsomorphic(code1, code2): 
    return 

    