'''
Script to retrieve test cases through TestLink API and dump to CSV that can be imported into Zephyr.

Environmental Variables need to be set:
set TESTLINK_API_PYTHON_SERVER_URL=http://<host>/testlink/lib/api/xmlrpc/v1/xmlrpc.php
set TESTLINK_API_PYTHON_DEVKEY=<api_token>

Update the following according to needs:
	Project Name:
		project = 'My Project'
	Custom Fields to include:
		customfields = [Auto Backlog', 'Build No', 'Defects', 'Test Grouping', 'UAT TC Priority', 'UAT Test Case']
	Test case fields to be included. Steps, Preconditions, Summary, Version and Test Suite ID required.
		testcase_fields = ['name', 'summary', 'preconditions', 'testsuite_id', 'importance', 'version', 'execution_type', 'estimated_exec_duration', 'full_tc_external_id', 'steps']

Notes:
	Use at your discretion. Unit test cases not provided.
	Replaces HTML with Markup where ever applicable to compatability wtih Zephyr
	Keyword export not supported, issue with TestLink-API-Python-client and API version
	Custom Field Failures are logged once to Output, ignored afterwards

Requires:
	TestLink-API-Python-client (0.6.2)
	html2text (2016.4.2)

Implemented and Tested with Python 3.5.1 and TestLink 1.9.9(Lone Ranger)
'''
import testlink
import datetime
import csv
import html2text

master_project_name_id = {}	#Created to reduce the calls to API to get suite names
ignorecustomfields = []		#reduces the calls to API if custom field is not used by project

def createAPIHandle():
	'''Returns Test Link API File handle'''
	tls = testlink.TestLinkHelper().connect(testlink.TestlinkAPIClient)
	return tls

def getProjectID(tls, project):
	'''Return project id'''
	return tls.getTestProjectByName(project)['id']
	
def allTestCasesInProject(tls, project_id):
	'''All test cases in a given project'''
	project_TLsuites = tls.getFirstLevelTestSuitesForTestProject(project_id)
	testcaseid_list = []
	for s in project_TLsuites:
		master_project_name_id[s['id']] = s['name'] 
		testcaseid_list.extend(tls.getTestCasesForTestSuite(s['id'], True, 'only_id'))
	return testcaseid_list

def parseHTML(html):
	'''clean up returns and tabs, remove extra space and convert to markup using html2text'''
	
	html = html.replace('\n', '')
	html = html.replace('\t', '')
	

	return html2text.html2text(html)
	
def breakDownTestSteps(steps):
	'''return test steps'''
	newsteps = {}
	
	for i in steps:
		if not((i['expected_results'] == '') and (i['actions'] == '')):
			newsteps[i['step_number']] = {'expected_results':parseHTML(i['expected_results']), 'actions':parseHTML(i['actions'])}
	
	return newsteps

def testSuiteInfoFromID(tls, testsuite_id):
	'''return test suite info'''
	#print('{:%H:%M:%S} '.format(datetime.datetime.now()) + 'Suite being looked up' + str(testsuite_id))
	if testsuite_id not in master_project_name_id:
		suite_info = tls.getTestSuiteByID(testsuite_id)
		if suite_info['parent_id'] in master_project_name_id:
			master_project_name_id[str(testsuite_id)] = master_project_name_id[suite_info['parent_id']] + ' / ' + suite_info['name']
		else:
			while True:
				testSuiteInfoFromID(tls, suite_info['parent_id'])
				if suite_info['parent_id'] in master_project_name_id:
					return
	
	return master_project_name_id[str(testsuite_id)]

def getCustomFieldsByTestCase(tls, testcaseid, field, version, project_id):
	'''return customfields from api'''
	if field in ignorecustomfields:
		return
	try:
		return tls.getTestCaseCustomFieldDesignValue(testcaseid, version, project_id, field, 'value')
	except:
		print('{:%H:%M:%S} '.format(datetime.datetime.now()) + 'ERROR: Ignoring Custom Field going forward: ' + field)
		ignorecustomfields.append(field)
	
def createCSV(testcasecsv, testcase_fieldscsv):
	'''print to csv file'''
	addldicts = []
	
	testcase_fieldscsv.remove('steps')
	testcase_fieldscsv.append('actions')
	testcase_fieldscsv.append('expected_results')
	
	#for i in range(1, (len(testcasecsv['steps']) + 1)):
	counter = 0
	for i in sorted(list(testcasecsv['steps'].keys())):
		if counter == 0:
			counter = counter + 1
			testcasecsv['actions'] = testcasecsv['steps'][str(i)]['actions']
			testcasecsv['expected_results'] = testcasecsv['steps'][str(i)]['expected_results']
		else:
			newdict = {x: None for x in testcasecsv}
			del newdict['steps']
			newdict['actions'] = testcasecsv['steps'][str(i)]['actions']
			newdict['expected_results'] = testcasecsv['steps'][str(i)]['expected_results']
			addldicts.append(newdict)
		
	del testcasecsv['steps']
	
	f = open('results.csv', 'a', newline='')
	headerTrue = open('results.csv', 'r').read(1024)
	try:
		with f as csvfile:		
			writer = csv.DictWriter(csvfile, fieldnames=testcase_fieldscsv)
			if headerTrue == '':
				writer.writeheader()
			
			writer.writerow(testcasecsv)
			
			for i in addldicts:
				writer.writerow(i)
	finally:
		f.close()
	
def testCaseDataByID(tls, testcaseid, project_id, testcase_fields, customfields):
	'''returns test case data from API, to do test steps and custom fields'''
	print('{:%H:%M:%S} '.format(datetime.datetime.now()) + 'Test Case being worked on ' + testcaseid)
	testcaseraw = tls.getTestCase(testcaseid)[0]
	testcase = {}
	for s in testcase_fields:
		testcase[s] = testcaseraw[s]
	testcase['preconditions'] =  parseHTML(testcase['preconditions'])
	testcase['summary'] =  parseHTML(testcase['summary'])
	testcase['steps'] = breakDownTestSteps(testcase['steps'])
	testcase['testsuite_id'] = testSuiteInfoFromID(tls, testcase['testsuite_id'])
	for t in customfields:
		if t not in ignorecustomfields:
			testcase[t] = getCustomFieldsByTestCase(tls, testcase['full_tc_external_id'], t, int(testcase['version']), project_id)
	
	
	createCSV(testcase, (testcase_fields + customfields))
	
	return testcase

if __name__ == "__main__":
	project = 'My Project'
	customfields = ['Auto Backlog', 'Build No', 'Defects', 'Test Grouping', 'UAT TC Priority', 'UAT Test Case']
	testcase_fields = ['name', 'summary', 'preconditions', 'testsuite_id', 'importance', 'version', 'execution_type', 'estimated_exec_duration', 'full_tc_external_id', 'steps']
	
	tls = createAPIHandle()
	project_id = getProjectID(tls, project)
	testcaseid_list = allTestCasesInProject(tls, project_id)

	
	print('Project ', project, '. Total test cases in the project are: ', len(testcaseid_list))
	
	for s in testcaseid_list:
		testCaseDataByID(tls, s, project_id, testcase_fields, customfields)
	
	print('Success! Project ', project, '. Total test cases exported: ', len(testcaseid_list))
