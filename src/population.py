import random
import os
import pseudoknot as pk

# Cheeck if it makes a valid base pair of RNA
def IsPair(c1,c2):
    if((c1=="A" and c2=="U") or (c1=="U" and c2=="A")):
        return 1
    elif ((c1=="G" and c2=="C") or (c1=="C" and  c2=="G")):
        return 1
    elif ((c1=="G" and c2=="U") or (c1=="U" and c2=="G")):
        return 1
    else:
        return 0
# end function

# Make dotplot for RNA sequence
def Checkerboard(sequence):
    board = []
    for i in range(0,len(sequence)-1):
        board.append([])
        for j in range(0,len(sequence)-1):
            if(j<i):
                if(IsPair(sequence[i],sequence[j])):
                    board[i].append(1)
                else:
                    board[i].append(0)
            else:
                board[i].append(0)

    #for i in range(0,len(sequence)-1):
    #    for j in range(0,len(sequence)-1):
    #        print(board[i][j])
    #   print("\n")
    return board
# end function

# Finding consecutive 4 or more diagonal 1's in board
def FindDiagonal(sequence,dotplot):
    info = []
    infoTable = []

    for i in range(len(sequence)-2,0,-1):
        for j in range(0,len(sequence)-2):
            if(dotplot[i][j]==1 and dotplot[i-1][j+1]==1):
                count=0
                k=0
                while True:
                    if (dotplot[i-k][j+k] == 1):
                        count+=1
                        dotplot[i - k][j + k] = 2
                    else:
                        break
                    k = k+1
                if(count>3):
                    info.append((j,i,count))  # start, end, length

    # sort info table in descending order
    infoTable = sorted(info, key=lambda x: x[2],reverse=True)
    return infoTable
    

# Generates given number of molecules
def GenerateMolecule(sequence, sequenceLength,popSize,infoTable):
    molecule = []
    moleculeShort = []
    stemPool = {}
    molecule_energy = []
    moleculeTable = []
    basePairs = {}


    for t in range(popSize):
        flag = []
        flagValid = []
        makePair = []
        infoEnergy = []
        mol = []
        moleculeSequence = []
        molShort = {}
        pool = []
        scElements = []
        pkElements = []

        # Initialization
        for i in range(sequenceLength):
            flag.append(0)
            flagValid.append(0)
            mol.append(".")

        # Adding paranthesis
        pair = 0
        pairIndex=0

        # Randomize the infoTable for each time population generation
        # random.shuffle(infoTable)
        infoTable1 = infoTable[:]
        # Molecule sequence generate for CRO operator 
        # problem; duplicate vales 
        for i in range(0,len(infoTable)-1):
            moleculeSequence.append(i)
            #moleculeSequence.append(random.randint(0, len(infoTable)-1))

        # Stem list after permutation is the population
        random.shuffle(moleculeSequence)
        for i in range(0,len(infoTable)-1):
            infoTable[moleculeSequence[i]] = infoTable1[i]


        # Find for new population
        index = 0
        for base in infoTable:
            start,end,length = base
            # Initial energy 0
            basePairs[base] = 0.0

            # Search inside for making bond
            for j,k in zip(range(start,start+length,1),range(end,0,-1)):
                if(flag[j]==0 and flag[k]==0):
                    flag[j] = 2
                    flag[k] = 2
                    flagValid[j] = 1 # (
                    flagValid[k] = 2 # )
                # endif
            # End for j,k

            # Search for 3 or more bp
            startPair = None
            endPair = None

            for j,k in zip(range(start,start+length,1),range(end,0,-1)):
                # Check if first valid bond is found
                stem = 0
                short = 0

                if(flag[j]==2 and flag[k]==2 and Equal12(flagValid,j,k)):
                    startPair = (j,k)
                    while(flag[j]==2 and flag[k]==2 and Equal12(flagValid,j,k) and j<=k):
                        stem+=1
                        j+=1
                        k-=1
                        # May not needed
                        endPair = (j,k)
                    # endwhile

                    # Revoke if not found enough stems
                    if(stem<3 and stem>0):
                        f,t = startPair
                        for x,y in zip(range(f,f+stem,1),range(t,t-stem,-1)):
                            flag[x] = 0
                            flag[y] = 0
                            flagValid[x] = 0
                            flagValid[y] = 0
                        # endfor

                    # Else add to mol and info
                    else:
                        f,t = startPair
                        scElements.append([f,t,stem]) # start,end,length
                        for x,y in zip(range(f,f+stem,1),range(t,0,-1)):
                            flag[x] = 1
                            flag[y] = 1
                            mol[x] = "("
                            mol[y] = ")"
                            infoEnergy.append((x,y))  # start, end
                            makePair.append((x,y))
                        # endfor
                        # Save this info as added in molecules
                        if(stem):   # Unnecessary if statement
                            molShort[index] =(start, end, stem)
                            index+=1
                            short = 0
                        # endif short
                    # endif stem

                # endif
            # Endfor j,k
        # Endfor basepair = start, end, length

        # print(PrintableMolecule(mol))
        # print(scElements)
        # Finding pseudoknot
        mol2 = mol[:]  # make a duplicate of molecule
        for i,j,len1 in scElements:
            for k,l,len2 in infoTable:
                if(i<k and k<j and j<l):   # condiiton for H-type Pseudoknot
                    # Pseudoknot info
                    # Loop lenght calculation for energy evaluation 
                    l1 = k - (i + len1)
                    l2 = (j - len1 + 1) - (k + len2)
                    l3 = (l - len2) - j
                    if(pk.LoopsFulfill(l1, l2, l3)):
                        # print(j,k,len2,"pk")

                        # Search inside for making pk
                        for u,v in zip(range(k,k+len2,1),range(l,0,-1)):
                            if(flag[u]==0 and flag[v]==0):
                                flag[u] = 2
                                flag[v] = 2
                                flagValid[u] = 3 # [
                                flagValid[v] = 4 # ]
                            # endif
                        # endfor

                        # Search for 2 or more bp for making pk
                        startPk = None
                        endPk = None

                        for u,v in zip(range(k,k+len2,1),range(l,0,-1)):
                            # Checy if first valid bond is found
                            stem = 0
                            if(flag[u]==2 and flag[v]==2 and Equal34(flagValid,u,v)):
                                startPair = (u,v)
                                uu = u
                                vv = v
                                while(flag[u]==2 and flag[v]==2 and Equal34(flagValid,u,v) and u<=v):
                                    
                                    # Check if it is still valid counting the future stem
                                    l1 = uu - (i + len1)
                                    l2 = (j - len1 + 1) - (uu + stem+1)
                                    l3 = (vv - stem-1) - j
                                    stillValid = pk.LoopsFulfill(l1, l2, l3)
                                    if(stillValid):
                                        stem+=1
                                        u+=1
                                        v-=1
                                        # May not needed
                                        endPair = (u,v)
                                    else:
                                        break
                                # endwhile

                                
                                # Revoke if not found enough stems (at least 2)
                                if(stem<2 and stem>0): # or (not stillValid)
                                    f,t = startPair
                                    for x,y in zip(range(f,f+stem,1),range(t,t-stem,-1)):
                                        flag[x] = 0
                                        flag[y] = 0
                                        flagValid[x] = 0
                                        flagValid[y] = 0
                                    # endfor

                                # add to mol and info
                                elif(stillValid):
                                    f,t = startPair
                                    # print(i,j,f,t,len1,stem,l1,l2,l3)
                                    pkElements.append([i,j,f,t,len1,stem,l1,l2,l3])
                                    for x,y in zip(range(f,f+stem,1),range(t,0,-1)):
                                        flag[x] = 1
                                        flag[y] = 1
                                        mol2[x] = "["
                                        mol2[y] = "]"

                                        # Must be removed later
                                        infoEnergy.append((x,y))
                                        makePair.append((x,y))
                                    # endfor
                                # endif stem

                            # endif
                        # Endfor x,y
                    else:
                        marker =0 #, l1, l2, l3,len1,len2= pk.Overlap(l1, l2, l3, len1, len2)
                        if(marker):
                        # Resolvable overlap
                            # print(l1,l2,l3,"pk-OL",len1,len2)
                            pass
                    
                # end pseudo condition
            # end for k,l, l2
        # end for i,j,l1

        # print(PrintableMolecule(mol2))

        
        # Energy calculation
        flag1 = 0   # Found au/gu penalty
        flag2 = 0   # Check if it is the first input
        flag3 = 0
        flag4 = 0
        total_energy = 0
        energy = 0
        infoEnergy.sort()
        for i in range(len(infoEnergy)-1):
            
            if(infoEnergy[i][0]+1==infoEnergy[i+1][0]):
                flag3 = 1
                flag4 = 1
                if (flag2 == 0 and ((sequence[infoEnergy[i][0]] == 'A') or (sequence[infoEnergy[i][0]] == 'U') or (sequence[infoEnergy[i][0]] == 'G' and sequence[infoEnergy[i][1]] == 'U') or (sequence[infoEnergy[i][0]]== 'U' and sequence[infoEnergy[i][1]] == 'G'))):
                    flag1 = 1
                    flag2 = 1
                    energy += .45
                    energy += CalculateEnergy(sequence[infoEnergy[i][0]], sequence[infoEnergy[i][1]], sequence[infoEnergy[i+1][0]], sequence[infoEnergy[i+1][1]])
                else:
                    energy += CalculateEnergy(sequence[infoEnergy[i][0]], sequence[infoEnergy[i][1]], sequence[infoEnergy[i+1][0]], sequence[infoEnergy[i+1][1]])
            else:
                flag4 = 2
                if(flag3==1):
                    if (((sequence[infoEnergy[i][0]] == 'A') or (sequence[infoEnergy[i][0]] == 'U') or (sequence[infoEnergy[i][0]] == 'G' and sequence[infoEnergy[i][1]] == 'U') or (sequence[infoEnergy[i][0]] == 'U' and sequence[infoEnergy[i][1]] == 'G'))):
                        energy += .45
                        energy += .43
                        energy += 4.09
                        total_energy += energy
                        flag2 = 0
                        flag1 = 0
                    else:
                        if(flag1==1):
                            energy += .43
                            energy += 4.09
                            total_energy += energy
                            flag2 = 0
                            flag1 = 0
                        elif(flag1 != 1):
                            energy += 4.09
                            total_energy += energy
                            flag2 = 0
                            flag1 = 0
                        # Endifelse
                    flag3 = 0
                #Endif
            #Endelse
        #Endfor
        if (flag4 != 2):            
            if (flag3 == 1):
                if (((sequence[infoEnergy[len(infoEnergy)-1][0]] == 'A') or (sequence[infoEnergy[len(infoEnergy) - 1][0]] == 'U') or (sequence[infoEnergy[len(infoEnergy) - 1][0]] == 'G' and sequence[infoEnergy[len(infoEnergy) - 1][1]] == 'U') or (sequence[infoEnergy[len(infoEnergy) - 1][0]] == 'U' and sequence[infoEnergy[len(infoEnergy) - 1][1]] == 'G'))):
                    energy += .45
                    energy += .43
                    energy += 4.09
                    total_energy += energy
                    flag2 = 0
                    flag1 = 0
                else:
                    if (flag1 == 1):
                        energy += .43
                        energy += 4.09
                        total_energy += energy
                        flag2 = 0
                        flag1 = 0
                    elif (flag1 != 1):
                        energy += 4.09
                        total_energy += energy
                        flag2 = 0
                        flag1 = 0
                flag3 = 0
                #Endif
            #Endif
        # Endif
        molecule_energy.append(total_energy)

        # Compute stemPool
        temp = []
        pool = moleculeSequence
        for i in pool:
            fl=0
            for j in molShort:
                if(infoTable[i]==j):
                    fl = 1
                    break
                # endif
            if(fl==0):
                temp.append(pool[i])

            # Endfor
        # Endfor
        stemPool[t] = temp

        # Add molecules to the mole
        if(mol==mol2):
            # print("No Pseudoknot detected!")
            pass
        else:
            molecule.append(mol2)

        moleculeShort.append(molShort)
        moleculeTable.append(moleculeSequence)
        
        # Clear all    
        flagValid.clear()
        flag.clear()

    return molecule,stemPool,infoEnergy, molecule_energy,moleculeTable,basePairs,infoTable,moleculeShort
# end function

def RemoveParanthesis(u,v,mol2,makePair):
    for j,k in makePair:
        if(u==j):
            mol2[k] = "."
        elif(u==k):
            mol2[j] = "."
        if(v==j):
            mol2[k] = "."
        elif(v==k):
            mol2[j] = "."
    return mol2
# end function

def Equal12(flagValid,j,k):
    one=0
    two=0
    if(j>k):   
        #swap(j,k)
        t = j
        j = k
        k = t

    for i in range(j,k+1):
        if(flagValid[i]==1):
            one+=1
        elif (flagValid[i]==2):
            two+=1
    
    if(one==two):
        return True
    else:
        return False
# end function

def Equal34(flagValid,j,k):
    three=0
    four=0
    if(j>k):   
        #swap(j,k)
        t = j
        j = k
        k = t

    for i in range(j,k+1):
        if(flagValid[i]==3):
            three+=1
        elif (flagValid[i]==4):
            four+=1
    
    if(three==four):
        return True
    else:
        return False
# end function
# Calclates the Gibbs free energy of a molecule on INN-HB model
def CalculateEnergy(p1, p2, p3, p4):
        
    ene = 0
    if ((p1 == 'A' and p2 == 'U' and p3 == 'A' and p4 == 'U') or (p1 == 'U' and p2 == 'A' and p3 == 'U' and p4 == 'A')):
    
        ene = -.93
        return ene
    
    if ((p1 == 'A' and p2 == 'U' and p3 == 'U' and p4 == 'A')):
    
        ene = -1.10
        return ene
    
    if ((p1 == 'A' and p2 == 'U' and p3 == 'G' and p4 == 'U') or (p1 == 'U' and p2 == 'G' and p3 == 'U' and p4 == 'A')):
    
        ene = -.55
        return ene
    
    if ((p1 == 'A' and p2 == 'U' and p3 == 'U' and p4 == 'G') or (p1 == 'G' and p2 == 'U' and p3 == 'U' and p4 == 'A')):
    
        ene = -1.36
        return ene
    
    if ((p1 == 'A' and p2 == 'U' and p3 == 'G' and p4 == 'C') or (p1 == 'C' and p2 == 'G' and p3 == 'U' and p4 == 'A')):
    
        ene = -2.08
        return ene
    
    if ((p1 == 'A' and p2 == 'U' and p3 == 'C' and p4 == 'G') or (p1 == 'G' and p2 == 'C' and p3 == 'U' and p4 == 'A')):
    
        ene = -2.24
        return ene
    
    if ((p1 == 'U' and p2 == 'A' and p3 == 'A' and p4 == 'U')):
    
        ene = -1.33
        return ene
    
    if ((p1 == 'U' and p2 == 'A' and p3 == 'G' and p4 == 'U') or (p1 == 'U' and p2 == 'G' and p3 == 'A' and p4 == 'U')):
    
        ene = -1.0
        return ene
    
    if ((p1 == 'U' and p2 == 'A' and p3 == 'U' and p4 == 'G') or (p1 == 'G' and p2 == 'U' and p3 == 'A' and p4 == 'U')):
    
        ene = -1.27
        return ene
    
    if ((p1 == 'U' and p2 == 'A' and p3 == 'C' and p4 == 'G') or (p1 == 'G' and p2 == 'C' and p3 == 'A' and p4 == 'U')):
    
        ene = -2.35
        return ene
    
    if ((p1 == 'A' and p2 == 'U' and p3 == 'A' and p4 == 'U') or (p1 == 'U' and p2 == 's' and p3 == 'U' and p4 == 's')):
    
        ene = -.93
        return ene
    
    if ((p1 == 'U' and p2 == 'A' and p3 == 'G' and p4 == 'C') or (p1 == 'C' and p2 == 'G' and p3 == 'A' and p4 == 'U') or (p1 == 'G' and p2 == 'U' and p3 == 'G' and p4 == 'C') or (p1 == 'C' and p2 == 'G' and p3 == 'U' and p4 == 'G')):
    
        ene = -2.11
        return ene
    
    if ((p1 == 'G' and p2 == 'U' and p3 == 'C' and p4 == 'G') or (p1 == 'G' and p2 == 'C' and p3 == 'U' and p4 == 'G')):
    
        ene = -2.51
        return ene
    
    if ((p1 == 'G' and p2 == 'U' and p3 == 'G' and p4 == 'U') or (p1 == 'U' and p2 == 'G' and p3 == 'U' and p4 == 'G')):
    
        ene = -.5
        return ene
    
    if ((p1 == 'G' and p2 == 'U' and p3 == 'U' and p4 == 'G')):
    
        ene = +1.29
        return ene
    
    if ((p1 == 'U' and p2 == 'G' and p3 == 'G' and p4 == 'C') or (p1 == 'C' and p2 == 'G' and p3 == 'G' and p4 == 'U')):
    
        ene = -1.41
        return ene
    
    if ((p1 == 'U' and p2 == 'G' and p3 == 'C' and p4 == 'G') or (p1 == 'G' and p2 == 'C' and p3 == 'G' and p4 == 'U')):
    
        ene = -1.53
        return ene
    
    if ((p1 == 'U' and p2 == 'G' and p3 == 'G' and p4 == 'U')):
    
        ene = +.3
        return ene
    
    if ((p1 == 'C' and p2 == 'G' and p3 == 'G' and p4 == 'C')):
    
        ene = -2.36
        return ene
    
    if ((p1 == 'G' and p2 == 'C' and p3 == 'C' and p4 == 'G')):
    
        ene = -3.42
        return ene
    
    if ((p1 == 'G' and p2 == 'C' and p3 == 'G' and p4 == 'C') or (p1 == 'C' and p2 == 'G' and p3 == 'C' and p4 == 'G')):
    
        ene = -3.26
        return ene
    
    return ene
    
# end function

# Generates an array of given size and return them with shuffling
def SequenceGenerator(size):

    numbers = []
    for i in range(0,size):
        numbers.append(i)
    random.shuffle(numbers)
    return numbers
# end function
def PrintableMolecule(molecule):
    moleculeStr = ""
    for i in molecule:
        moleculeStr+=i
    # endfor
    return moleculeStr
# end function