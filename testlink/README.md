# Script to retrieve test cases through TestLink API and dump to CSV that can be imported into Zephyr.
### Environmental Variables need to be set:
set TESTLINK_API_PYTHON_SERVER_URL=http://<host>/testlink/lib/api/xmlrpc/v1/xmlrpc.php

set TESTLINK_API_PYTHON_DEVKEY=<api_token>

### Update the following according to needs:
* Project Name:
    * project = 'My Project'
* Custom Fields to include:
	* customfields = [Auto Backlog', 'Build No', 'Defects', 'Test Grouping', 'UAT TC Priority', 'UAT Test Case']
* Test case fields to be included. Steps, Preconditions, Summary, Version and Test Suite ID required.
	* testcase_fields = ['name', 'summary', 'preconditions', 'testsuite_id', 'importance', 'version', 'execution_type', 'estimated_exec_duration', 'full_tc_external_id', 'steps']

### Notes:
* Use at your discretion. Unit test cases not provided.
* Replaces HTML with Markup where ever applicable to compatability wtih Zephyr
* Keyword export not supported, issue with TestLink-API-Python-client and API version
* Custom Field Failures are logged once to Output, ignored afterwards

### Requires:
* TestLink-API-Python-client (0.6.2)
* html2text (2016.4.2)

Implemented and Tested with Python 3.5.1 and TestLink 1.9.9(Lone Ranger)
