import requests
import os
from datetime import datetime

JENKINS_URL='http://localhost:8080/'

ALLOWED_PROJECT_LIST = ['kshanuanand']
ALLOWED_REPO_LIST = ['repo1']
HTML_FILE_PATH = '.'
HTML_FILE_NAME = 'mail.html'
HTML_HEAD ='''
<html>
<head>
</head>
<body>
<table border=2>
<tr>
<th>PROJECT</th>
<th>Repository</th>
<th>Branch</th>
<th>Age last Built (in days)</th>
</tr>
'''
HTML_BODY = '''
'''
HTML_TAIL = '''
</table>
</body>
</html>
'''
for project in ALLOWED_PROJECT_LIST:
    print("Get List of repositories present in project {}".format(project))
    PROJECT_API = JENKINS_URL+'job/'+project+'/api/json'
    resp = requests.get(PROJECT_API)
    if resp.status_code != 200:
        raise ApiError('GET {} : {}'.format(PROJECT_API,resp.status_code))
    for repos in resp.json()['jobs']:
        repository = repos['name']
        if repository in ALLOWED_REPO_LIST:
            print("\tProcessing repository {} with URL: {}".format(repository,repos['url']))
            REPOSITORY_API = repos['url'] + 'api/json'
            respRepository = requests.get(REPOSITORY_API)
            if respRepository.status_code != 200:
                raise ApiError('GET {} : {}'.format(REPOSITORY_API,respRepository.status_code))
            for branches in respRepository.json()['jobs']:
                branch = branches['name']
                branch_url = branches['url']
                branch_url_lastBuild = branches['url'] + 'lastBuild/api/json'
                respBuild = requests.get(branch_url_lastBuild)
                if respBuild.status_code != 200:
                    raise ApiError('GET {} : {}'.format(branch_url_lastBuild,respBuild.status_code))
                ct = datetime.now()
                timestamp_epoch = float(respBuild.json()['timestamp'])/1000.
                timestamp = datetime.fromtimestamp(timestamp_epoch)
                diff_in_days = 31 #(ct - timestamp).days
                print("\t\tProcessing Branch: {} with URL: {}, timestamp: {}, ct: {}, diff in days: {}".format(branch,branch_url, timestamp, ct, diff_in_days))
                if diff_in_days > 30:
                    print('\t\t\tReport to Respective DL')
                    HTML_BODY = HTML_BODY + '''
                    <tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    </tr>
                    '''.format(project,repository,branch,diff_in_days)
HTML = HTML_HEAD + HTML_BODY + HTML_TAIL
print(HTML)
FILE = ''
if os.name == 'nt':
    FILE = HTML_FILE_PATH + '\\' + HTML_FILE_NAME
else:
    FILE = HTML_FILE_PATH + '/' + HTML_FILE_NAME
print(FILE)
f = open(FILE,"w")
f.write(HTML)