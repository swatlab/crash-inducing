import os, re, sys
import xmltodict
import pandas as pd
from collections import OrderedDict, Counter

DEBUG = False

def loadFile(filename):
    with open(filename, 'rb') as f:
        return f.read()

def addChangedType(key, father, how, changed_type_list):    #   How means: added/deleted/modified
    if key == '#text':
        changed_type = father[-1]
        if changed_type == 'type':
            print father
    elif key == 'name':
        changed_type = 'refactoring'
        #how = 'n/a'
    elif key == 'block':
        changed_type = father[-1]
        if changed_type == 'type':
            print father
    else:
        changed_type = key
    changed_type_list.append((changed_type, how))
    return

def compareString(s1, s2, depth, father, key):
    if s1 != s2:
        if re.search(r'[a-zA-Z]+', s1) or re.search(r'[a-zA-Z]+', s2):
            if DEBUG:
                print '  '*depth + '+', key.upper(), 'DELETED', father
                print '  '*depth + '+', key.upper(), 'ADDED', father
            addChangedType(key, father, 'deleted', changed_type_list)
            addChangedType(key, father, 'added', changed_type_list)
    return

def compareDifferntTypes(depth, father, key):
    if DEBUG:
        print '  '*depth + '+', key.upper(), 'DELETED - DIFFERENT TYPES', father
        print '  '*depth + '+', key.upper(), 'ADDED - DIFFERENT TYPES', father
    addChangedType(key, father, 'deleted', changed_type_list)
    addChangedType(key, father, 'added', changed_type_list)
    return

def compareDict(d1, d2, depth, father, changed_type_list):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    #   Intersection and union of the keys in the two items
    intersect = d1_keys & d2_keys
    union = d1_keys | d2_keys
    #   Check whether the two items possess the identical keys
    if union == intersect:    
        for key in d1:
            #   If both compared items are ordered-dict
            if type(d1[key]) == type(OrderedDict()) and type(d2[key]) == type(OrderedDict()):
                d1_value = d1[key]
                d2_value = d2[key]
                compareDict(d1_value, d2_value, depth+1, father + [key], changed_type_list)
            else: 
                #   If both compared items are strings
                if type(d1[key]) == type(u'') and type(d2[key]) == type(u''):
                    s1 = d1[key]
                    s2 = d2[key]
                    compareString(s1, s2, depth, father, key)      
                #   If both compared items are list
                elif type(d1[key]) == type(list()) and type(d2[key]) == type(list()):
                    #   The two lists are with the same length
                    if len(d1[key]) == len(d2[key]):
                        for i in range(len(d1[key])):
                            sub_d1_value = d1[key][i]
                            sub_d2_value = d2[key][i]
                            if type(sub_d1_value) == type(OrderedDict()) and type(sub_d2_value) == type(OrderedDict()):
                                compareDict(sub_d1_value, sub_d2_value, depth+1, father + [key], changed_type_list)
                            else:
                                if type(sub_d1_value) == type(u'') and type(sub_d2_value) == type(u''):
                                    compareString(sub_d1_value, sub_d2_value, depth, father, key)
                                else:
                                    compareDifferntTypes(depth, father, key)
                    #   A list is longer than the other one (the nested structure is ignored, the current node is thought to be modified)
                    else:
                        if DEBUG:
                            print '  '*depth + '+', key.upper(), 'MODIFIED', father
                        addChangedType(key, father, 'modified', changed_type_list)
                #   If one of the compared items is string (the other may be ordered-dict, or list)
                else:
                    if type(d1[key]) != type(d2[key]):
                        compareDifferntTypes(depth, father, key)                        
    #   If the two items possess some different keys
    else:
        if DEBUG:
            print '  '*depth + '-', 'UNSYMETRIC KEYS:'
        for aKey in d1_keys-intersect:
            if DEBUG:
                print '  '*depth + '+', aKey.upper(), 'DELETED', father
            addChangedType(aKey, father, 'deleted', changed_type_list)
        for aKey in d2_keys-intersect:
            if DEBUG:
                print '  '*depth + '+', aKey.upper(), 'ADDED', father
            addChangedType(aKey, father, 'added', changed_type_list)
    return
    
def outputChangedTypes(all_changed_results, part_num):
    #   Find all types detected
    types_set = set()
    for f in all_changed_results:
        changed_dict = all_changed_results[f]
        type_set = set([ct[0] for ct in changed_dict.keys()])
        types_set |= type_set
    #   Cross types and modes (modes: added, deleted, modified)
    all_types_modes = list()
    modes = ['_added', '_deleted', '_modified']
    for t in list(types_set):
        all_types_modes += [t+m for m in modes]    
    #   Output results to a dataframe, then a csv
    changed_occur_list = list()
    for f in all_changed_results:
        changed_dict = all_changed_results[f]
        type_occurs = [0] * len(all_types_modes)
        for ct in changed_dict:
            occur_num = changed_dict[ct]
            #print occur_num
            type_and_mode = ct[0] + '_' + ct[1]
            type_idx = all_types_modes.index(type_and_mode)
            type_occurs[type_idx] += occur_num
        changed_occur_list.append([f] + type_occurs)
    #print changed_occur_list 
    df = pd.DataFrame(changed_occur_list, columns=['file'] + all_types_modes)
    df.to_csv('analytic_code/changed_types/part%d.csv' %part_num, header=True, index=False)
    return
    

if(__name__ == '__main__'):
    part_num = int(sys.argv[1])
    print 'Dealing with Part %d' %part_num
    
    before_folder = 'analytic_code/xml_before'
    after_folder = 'analytic_code/xml_after'
    all_changed_results = dict()
    file_list = sorted(os.listdir(before_folder))
    
    for i in range(0, len(file_list)):
        if i%10 == part_num:
            f = file_list[i]
            if f.endswith('.xml'):
                before_path = before_folder + '/' + f
                after_path = after_folder + '/' + f
                if os.path.isfile(after_path): 
                    before_str = loadFile(before_path)
                    after_str = loadFile(after_path)
                    try:
                        #   convert xml to dictionary
                        before_dict = xmltodict.parse(before_str)
                        after_dict = xmltodict.parse(after_str)
                        #   recursively compare the difference between the two versions
                        changed_type_list = list()
                        print '*****', f, '*****'
                        compareDict(before_dict, after_dict, 0, ['rootnode'], changed_type_list)
                        print Counter(changed_type_list)
                        all_changed_results[f] = dict(Counter(changed_type_list))
                        print '-'*150, '\n'
                    except:
                        print '*****', f, '*****'
                        print 'Error occurred'
    outputChangedTypes(all_changed_results, part_num)       
    
