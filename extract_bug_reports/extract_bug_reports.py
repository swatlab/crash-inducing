import urllib2

def downloadReport(bugID, type):
    #   Initialise variables
    if(type == 'basic_report'):
        url = 'https://bugzilla.mozilla.org/rest/bug/' + bugID + '?include_fields=_all'
    elif(type == 'comments'):
        url = 'https://bugzilla.mozilla.org/rest/bug/' + bugID + '/comment'
    urlItem = None
    #   download bug reports as json
    try:
        urlItem = urllib2.urlopen(url)
    except:
        print 'Invalid bug ID or non-authorised access'
    if(urlItem):
        pageBytes = urlItem.read()
        pageTxt = pageBytes.decode('utf-8', 'ignore')
        jsonStr = pageTxt.encode('ascii','ignore')        
        if(type == 'basic_report'):
            with open('basic_report/' + bugID + '.json', 'wb') as f:
                f.write(jsonStr)
        else:
            with open('bug_comments/' + bugID + '.json', 'wb') as f:
                f.write(jsonStr)
    return
    
if(__name__ == '__main__'):
    with open('bug-IDs.txt', 'rb') as f:
        read_data = f.read()
    for bugID in read_data.split('\n'):
        print bugID
        downloadReport(bugID, 'basic_report')
        downloadReport(bugID, 'comments')
    