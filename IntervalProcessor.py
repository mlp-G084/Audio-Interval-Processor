#coding=utf-8

# Public Constant --------------------------------------------------------------------------------------------------------------------------

instrument_dic = {'Guqin':0,'Zhongruan':1,'Guzheng': 2,'Xiao':3,'Zhudi':4,'Pipa':5,'Erhu':6}

# Dataframe Preprocessing ------------------------------------------------------------------------------------------------------------------
# return the sorted instruments for a dataframe
def allInstrumentsInDigit(dataframe):
    l = list(set(dataframe["tier"]))
    l.sort()
    return l

def allInstrumentsInName(dataframe):
    l = list(set(dataframe["name"]))
    l.sort()
    l = [instrument.strip() for instrument in l]
    return l

def findInstrumentDigit(instrument_string):
    return instrument_dic.get(instrument_string)

def findInstrumentName(instrument_digit):
    for name, digit in instrument_dic.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if digit == instrument_digit:
            return name

# find the integer intervals for the intended instrument when doing intersection
# intervals were shortened at sides to round to integers
def intervalsListByNameInter(dataframe, instrument):
    tier = instrument_dic.get(instrument)
    return [[int(start+1),int(stop)] for start, stop in zip(dataframe[dataframe.tier==tier]["start"],dataframe[dataframe.tier==tier]["stop"])]

def intervalsListByDigitInter(dataframe,digit):
    return intervalsListByNameInter(dataframe,findInstrumentName(digit))

# find the integer intervals for the intended instrument when doing difference
# intervals were elongated at sides to round to integers
def intervalsListByNameOuter(dataframe,instrument):
    tier = instrument_dic.get(instrument)
    return [[int(start),int(stop+1)] for start, stop in zip(dataframe[dataframe.tier==tier]["start"],dataframe[dataframe.tier==tier]["stop"])]

def intervalsListByDigitOuter(dataframe,digit):
    return intervalsListByNameOuter(dataframe,findInstrumentName(digit))

# Intersection --------------------------------------------------------------------------------------------------------------------------

# Find intervals that both instruments appear, might include other instruments
# input: 2 ordered interval lists, and the threshold for the interval to be included
# output: list of common intervals
def findCommonIntervals(ins1, ins2, threshold):
    commons = []
    for i in ins1:
        j = 0
        while (j < len(ins2)): # if ins2 hasn't reached the end
            intersect = set(range(i[0],i[1]+1)).intersection(set(range(ins2[j][0],ins2[j][1]+1)))
            if (intersect) and (max(intersect)-min(intersect) >= threshold): # if two intervals do overlap
                commons.append([min(intersect),max(intersect)])
                j = j + 1
            else: # if two intervals don't overlap
                if (ins2[j][1]< i[0]): # if ins1 is after ins2, continue within the while loop
                    j = j + 1
                else:  # if ins1 is before ins2, then break to the outer ins1's loop
                    break
    return commons



# Find common intervals of several instruments, result intervals might include other instruments
# input: dataframe + a list of instrument digits + threshold
# output: a list of common intervals for the given instruments
def findCommonIntervalsForMulti(dataframe, instrument_list, threshold):
    if (len(instrument_list) > 1):
        interval_list = [intervalsListByDigitInter(dataframe, ins_digit) for ins_digit in instrument_list]
        result = findCommonIntervals(interval_list[0],interval_list[1], threshold)
        i = 2
        while (i < len(instrument_list)):
            result = findCommonIntervals(result,interval_list[i], threshold)
            i = i + 1
        return result
    elif (len(instrument_list) == 1):
        return intervalsListByDigitInter(dataframe, instrument_list[0])
    else:
        # print("Invalid: no instrument given in the instrument list. No inclusion is carried out.")
        return []

# Exclusion --------------------------------------------------------------------------------------------------------------------------

# Exclude ins2 from in1
# input: 2 ordered interval lists for 2 instruments, and the threshold for the interval to be included
# output: the interval list that exclude ins2 from ins1 (i.e. anything in ins2 excludesa from ins1)
# notie: can be optimized because the ins1 intervals at the back don't really need to check the ins2 at the very front
def excludeCommonIntervals(ins1,ins2, threshold):
    results = []
    for i in ins1:
        j = 0
        i_copy = i.copy()
        while (j < len(ins2)): # if ins2 hasn't reached the end
            intersect = set(range(i_copy[0],i_copy[1]+1)).intersection(set(range(ins2[j][0],ins2[j][1]+1)))
            if (intersect): # if two intervals do overlap, then exclude the overlapping ranges
                s1, e1, s2, e2 = i_copy[0], i_copy[1], ins2[j][0], ins2[j][1]
                if (s1 > s2) and (e1 > e2): # exclude the start of s1 till e2 if s1 isn't completely included in ins2
                    i_copy[0] = e2
                if (s1 > s2) and (e1 <= e2):# ins1 completely within ins2, break
                    break
                if (s1 < s2) and (e1 <= e2):# add the start of s1 and jump to next ins1 when ins1 tail covered by ins2
                    results.append([s1,s2])
                    break
                if (s1 < s2) and (e1 > e2): # ins2 in between ins1, take the former and update i_copy
                    results.append([s1,s2])
                    i_copy[0] = e2
                j = j + 1
            else: # if two intervals don't overlap, then ins1 either before ins2 or after ins2
                if (ins2[j][1]< i_copy[0]): # if ins1 is after ins2, continue within the while loop
                    j = j + 1
                else:  # if ins1 is before an immdiate ins2, then append and break to the outer ins1's loop
                    results.append(i_copy)
                    break
    return results

# Exclude the instruments in the exclusion_instrument_list from the given intervals
# input: a list of intervals + a list of instruments by digits to exclude
# output: a list of intervals after exclusion
def excludeCommonIntervalsForMulti(dataframe, intervals, ex_ins_list, threshold):
    if (len(intervals) >= 1):
        for ins in ex_ins_list:
            ex_intervals = intervalsListByDigitOuter(dataframe, ins)
            intervals = excludeCommonIntervals(intervals,ex_intervals, threshold)
        return intervals
    else:
        # print("Invalid: the number of intervals provided is 0. No exclusion is carried out.")
        return []

# Polyphony by Instrument ------------------------------------------------------------------------------------------------------

from itertools import combinations

# Give an instrument, return the intervals that are polyphony.
# A certain key only contains the intervals with the specified instruments in the key and exclude other instruments
# input:
#   1.dataframe dataset
#   2.the name of one instrument by Name
#   3.the length threshold for the intended intervals
# return: a dictionary
#   1. key: sorted lists of instruments by digits; value: list of overlapped intervals
#   2. the last key is 'length' with value as the total number of seconds for the instrument
def polyphonyForInstrument(dataframe, instrument, threshold):
    all_instruments = allInstrumentsInDigit(dataframe)
    print(all_instruments)
    if not (findInstrumentDigit(instrument) in all_instruments):
        print("Instrument not exist in this sound track.")

    else:
        # Find all combinations of the instrument with other instruments [(n-1)^2 possibilities]
        combs = []
        for n in range(2, len(all_instruments)+1):
            # caveat here, list of a set doesn't always return to be ordered cuz of some reasons
            c = [tuple(list(set(c))) for c in combinations(all_instruments,n) if findInstrumentDigit(instrument) in c]
            c.sort()
            combs += c
        # find intervals for all possible combinations
        dictionary = {}
        length = 0
        for comb in combs:
            pre_intervals = findCommonIntervalsForMulti(dataframe, comb, threshold)
            ex_instruments = list(set(all_instruments) - set(comb))
            pre_intervals = excludeCommonIntervalsForMulti(dataframe, pre_intervals, ex_instruments, threshold)
            length = length + sum([ end - start for start,end in pre_intervals])
            dictionary[comb] = pre_intervals

        dictionary['length'] = length
        return dictionary

def polyphonyByInstrument(file, instrument, threshold):
    f = pd.read_csv(file)
    f['tier'].replace(instrument_dic, inplace=True)
    dataframe = f
    return polyphonyForInstrument(dataframe,instrument,threshold)

# Test --------------------------------------------------------------------------------------------------------------------------

import pandas as pd
#
# guojige = pd.read_csv("csv/国际歌.csv")
# instrument_dic = {'Guqin':0,'Zhongruan':1,'Guzheng': 2,'Xiao':3,'Zhudi':4,'Pipa':5,'Erhu':6}
# guojige['tier'].replace(instrument_dic, inplace=True)
#
#
# def test_inclusion():
#     a1 = [[1,3],[5,7],[9,40]]
#     b1 = [[2,6],[9,15],[37,40]]
#
#     assert findCommonIntervals(a1,b1,1) == [[2,3],[5,6],[9,15],[37,40]]
#     assert findCommonIntervals(a1,b1,2) == [[9,15],[37,40]]
#     return True
#
# def test_inclusion_multi():
#
#     assert (findCommonIntervalsForMulti(guojige, [0,2],2)) == [[132,206],[210,310]]
#     assert (findCommonIntervalsForMulti(guojige, [2,0],2)) == [[132,206],[210,310]]
#     assert (findCommonIntervalsForMulti(guojige, [0,2,5],2)) == [[158,206],[260,309]]
#     assert (findCommonIntervalsForMulti(guojige, [0,5,2],2)) == [[158,206],[260,309]]
#     assert (findCommonIntervalsForMulti(guojige, [0,4,5],2)) == [[158,206],[260,309]]
#     assert (findCommonIntervalsForMulti(guojige, [0,4],2)) == [[132,208],[235,310]]
#     assert (findCommonIntervalsForMulti(guojige, [0,5,2,4],2)) == [[158,206],[260,309]]
#
#     return True
#
# def test_exclusion():
#     t = 2
#     a1 = intervalsListByNameInter(guojige, 'Guzheng')
#     b1 = intervalsListByNameOuter(guojige, 'Pipa')
#     r1 = [[107, 157], [210,259]]
#     a2 = intervalsListByNameInter(guojige, 'Pipa')
#     b2 = intervalsListByNameOuter(guojige, 'Guzheng')
#     r2 = []
#     a3 = intervalsListByNameInter(guojige, 'Guqin')
#     b3 = intervalsListByNameOuter(guojige, 'Pipa')
#     r3 = [[132,157],[207,259]]
#     a4 = intervalsListByNameInter(guojige, 'Pipa')
#     b4 = intervalsListByNameOuter(guojige, 'Guqin')
#     r4 = []
#     a5 = intervalsListByNameInter(guojige, 'Guzheng')
#     b5 = intervalsListByNameOuter(guojige, 'Guqin')
#     r5 = [[107,131]]
#     a6 = intervalsListByNameInter(guojige, 'Guqin')
#     b6 = intervalsListByNameOuter(guojige, 'Guzheng')
#     r6 = [[207,209]]
#
#     assert (excludeCommonIntervals(a1,b1,t) == r1)
#     assert (excludeCommonIntervals(a2,b2,t) == r2)
#     assert (excludeCommonIntervals(a3,b3,t) == r3)
#     assert (excludeCommonIntervals(a4,b4,t) == r4)
#     assert (excludeCommonIntervals(a5,b5,t) == r5)
#     assert (excludeCommonIntervals(a6,b6,t) == r6)
#
#     return True
#
# def test_exclusion_multi():
#     t = 2
#     a1 = findCommonIntervalsForMulti(guojige,[2,0],2)
#     b1 = [4]
#     r1 = [[210,234]]
#     a2 = findCommonIntervalsForMulti(guojige,[2,0],2)
#     b2 = [4,5]
#     r2 = [[210,234]]
#     a3 = findCommonIntervalsForMulti(guojige,[2,0],2)
#     b3 = [5]
#     r3 = [[132,157],[210,259]]
#
#     assert excludeCommonIntervalsForMulti(guojige,a1,b1,t) == r1
#     assert excludeCommonIntervalsForMulti(guojige,a2,b2,t) == r2
#     assert excludeCommonIntervalsForMulti(guojige,a3,b3,t) == r3
#
#     return True
#
#
# print(test_inclusion())
# print(test_inclusion_multi())
# print(test_exclusion())
# print(test_exclusion_multi())
#
# print("Guojige: ")
# print('- Guzheng:',polyphonyForInstrument(guojige,"Guzheng",2)['length'])
# print('- Pipa:',polyphonyForInstrument(guojige,"Pipa",2)['length'])
# print('- Zhudi:',polyphonyForInstrument(guojige,"Zhudi",2)['length'])
# print('- Guqin:',polyphonyForInstrument(guojige,"Guqin",2)['length'])

# Stats ----------------------------------------------------------------------------------------------------------------------
import os

instrument_dic = {'Guqin':0,'Zhongruan':1,'Guzheng': 2,'Xiao':3,'Zhudi':4,'Pipa':5,'Erhu':6, 'Xun':-1}

def total_count(threshold):
    # Obtain all the files
    files = os.listdir("csv/")
    files.remove('.DS_Store')
    print("All files:", files)
    csvs = []
    for csv in files:
        f = pd.read_csv("csv/" + csv)
        f['tier'].replace(instrument_dic, inplace=True)
        csvs.append(f)

    # Initialise the dictionary for the length of each instrument in all the polyphony test set soundtracks
    length_dictionary = {}
    for instrument in instrument_dic.keys():
        length_dictionary[instrument] = 0

    # Count the length of each instrument in polyphony setting for each soundtrack
    for csv in csvs:
        print("--File--")
        instruments = allInstrumentsInName(csv)
        print(instruments)
        for instrument in instruments:
            length_dictionary[instrument] += polyphonyForInstrument(csv,instrument,threshold)['length']
            print(polyphonyForInstrument(csv,instrument,threshold))

    return length_dictionary

# print(total_count(1))
print(polyphonyByInstrument('csv/guojige.csv','Guzheng',0))

# Addition notes:
# 0.try to take more tests to ensure the functions work properly
# 1. a caveat in polyphony function regarding whether each combination is in the dictionary is ordered
# 2. the functions can potential be made more efficient by shorten the loop and by using clever data structure e.g. segement tree, sequential series etc.
