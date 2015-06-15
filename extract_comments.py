from __future__ import division
import csv, re, os, json
import MySQLdb
from numpy import median, percentile

# initialize the MySQL service
def initDatabase():
    database = MySQLdb.connect(host = 'localhost', user = 'root', passwd = 'poly', db = 'Mozilla_Bugzilla', port = 3306)
    cursor = database.cursor()
    return cursor

# build bug list
def buildBugList():
    inputDict = dict()
    for row in csvfile:
        inputDict[row[0]] = (float(row[1]), int(row[2]), float(row[4]))
    return inputDict


def isClosed(bugID):
    cursor.execute('SELECT bug_status FROM bugs WHERE bug_id = ' + bugID)
    results = cursor.fetchall()
    if(results[0][0] == 'VERIFIED' or results[0][0] == 'RESOLVED'):
        return 1
    else:
        return 0

def extractPath(comments):
    if(re.search(r'([0-9]|[a-z0-9]+\.[a-z]+)\s*\t(\w|:)+\s*\t(\w|:)+', comments)):
        path_list = re.findall(r'\/[^\s]+\.[cpp|c|h]\b', comments)
        path_set = set()
        if len(path_list):
            for path in set(path_list):
                path_set.add(re.sub(r'[^a-zA-Z]+', '', path, 1))
            return ('path', path_set)
        else:
            return 'not matched' 
    return 'not matched'

def extractFile(comments):
    if(re.search(r'([0-9]|[a-z0-9]+\.[a-z]+)\s*\t(\w|:)+\s*\t(\w|:)+', comments)):
        file_list = re.findall(r'\w+\.[cpp|c|h|cc]\b', comments)
        file_set = set()
        if len(file_list):
            for file in set(file_list):
                file_set.add(file)
            return ('file', file_set)
        else:
            return 'not matched'
        '''sections = location_str.split(' ')
        for sec in sections:
            if('.cpp' in sec or '.h' in sec or '.c' in sec):
                filename = re.search(r'\w+\.(cpp|c|h|cc)\b', sec)
                if(filename):
                    return ('file', filename.group(0))'''
    return 'not matched'

def extractMethod(location_str):
    method = re.search(r'(\w+\:{2})+\w+', location_str)
    if(method):
        #return method.group(0) + '  \t' + 'method'
        return ('method', method.group(0))
    else:
        return 'not matched'

def extractOther(location_str):
    if(re.search(r'\.(cpp|c|h|cc)\b', location_str)):
        sections = location_str.split(' ')
        for sec in sections:
            if('.cpp' in sec or '.h' in sec or '.c' in sec):
                other = re.search(r'\w+\.(cpp|c|h|cc)\b', sec)
                if(other):
                    #return other.group(0) + '  \t' + 'other'
                    return ('other', other.group(0))
    else:
        return 'not matched'

def analyseStackTrace(comments):
    #   extract paths of files from stack trace 
    paths = extractPath(comments)
    if(paths != 'not matched'):
        return paths
    files = extractFile(comments)     
    if(files != 'not matched'):
        return files   
    #   extract methods or other informatin from stack trace      
    text_list = comments.split('\n')
    for oneline in text_list:
        method = extractMethod(oneline)
        if(method != 'not matched'):
            return method
    for oneline in text_list:
        other = extractOther(oneline)
        if(other != 'not matched'):
            return other 
    #print comments
    return 'unknown'  

def localiseBug(comments, title):    
    if(re.search(r'([0-9]|[a-z0-9]+\.[a-z]+)\s*\t(\w|:)+\s*\t(\w|:)+', comments)):
        location = analyseStackTrace(comments)
    else:
        location = extractMethod(title)
    return location   

def extractBasicReportFromJson(bugID, bug_dict, metricDict):
    if os.path.isfile('extract_bug_reports/basic_report/' + bugID + '.json'):
        with open('extract_bug_reports/basic_report/' + bugID + '.json', 'rb') as f:
            read_data = f.read()
        report_item = json.loads(read_data)
        metricDict['title'] = report_item['bugs'][0]['summary']
        status = report_item['bugs'][0]['status']
        if(status == 'VERIFIED' or status == 'RESOLVED'):
            metricDict['is_closed'] = 0
        else:
            metricDict['is_closed'] = 1
        bug_dict[bugID] = metricDict
        return metricDict['title']
    return ''

def extracCommentsFromJson(bugID):
    combined_comments = ''
    if os.path.isfile('extract_bug_reports/bug_comments/' + bugID + '.json'):
        with open('extract_bug_reports/bug_comments/' + bugID + '.json', 'rb') as f:
            read_data = f.read()
        comment_item = json.loads(read_data)
        comment_list = comment_item['bugs'][bugID]['comments']
        for comment in comment_list:
            comment_text = comment['text']
            if len(combined_comments):
                combined_comments = combined_comments + '\n\n' + comment_text
            else:
                combined_comments = comment_text
    return combined_comments

# extract metrics from bug database
def extractMetrics(cursor, inputDict):
    print 'Extracting buggy files ...'
    bug_dict = dict()
    bug_location_dict = dict()
    for bugID in inputDict:
        metricDict = dict()
        # creat_time, bug_title, platform, severity, priority, last_modified_time, reporter, assignee 
        cursor.execute('SELECT  short_desc FROM bugs WHERE bug_id = ' + bugID)
        results = cursor.fetchall()
        if(len(results)):
            tpl = results[0]
            title = tpl[0]
            metricDict['title'] = title
            # is closed
            metricDict['is_closed'] = isClosed(bugID)
            # Add bugID/metrics to the bug dict
            bug_dict[bugID] = metricDict
            # comment
            cursor.execute('SELECT comments FROM bugs_fulltext where bug_id = ' + bugID)
            results = cursor.fetchall()
            comments = results[0][0]
        else:
            print bugID
            title = extractBasicReportFromJson(bugID, bug_dict, metricDict)
            comments = extracCommentsFromJson(bugID)
        # bug's location
        location = localiseBug(comments, title)
        if(location != 'unknown' and location != 'not matched'):
            bug_location_dict[bugID] = localiseBug(comments, title)           
    return (bug_dict, bug_location_dict)
    
def outputBugLocation(bug_location_dict):
    print 'Outputing metrics ...'
    csv_writer = csv.writer(open('results/bug_location.csv', 'wb'))
    csv_writer.writerow(['BugID', 'Location'])
    for bugID in bug_location_dict:
        if(bug_location_dict[bugID][0] == 'path' or bug_location_dict[bugID][0] == 'file'):
            csv_writer.writerow([bugID, ' '.join(bug_location_dict[bugID][1])])
    return

if(__name__ == '__main__'):
    component_set = set()
    csvfile = csv.reader(open('raw_data/basic_info.csv', 'rb'))
    next(csvfile, None)
    cursor = initDatabase()
    inputDict = buildBugList()        
    (bug_dict, bug_location_dict) = extractMetrics(cursor, inputDict)
    outputBugLocation(bug_location_dict)
