#!/usr/bin/python
from ace.suites import *
from ace.levels import *

import os, re, types, inspect

class_name_regex = re.compile('^Test[A-Z0-9][a-zA-Z0-9]+$')
function_name_regex = re.compile('^test_[a-z0-9_]+$')
file_name_regex = re.compile('^test_[a-z0-9_]+\.py$')
dir_name_regex = re.compile('^[a-z0-9_]+$')
adaptive_directories = []

def process_free_function(file, function):
    function_name = function.__name__
    if getattr(function, '__test__', True)==False or not 'test' in function_name.lower() or \
            function_name=='nottest' or function_name=='istest':
        return []
    return ['The %s test function in %s is not in a class, all methods must be contained in python classes \
(utility methods should be placed in the "ace" directory)' % (function_name, file)]

def process_class_function(file, function, parent_suite=None, parent_level=None, parent_owner=None, parent_jira=None):
    '''Processes a function by validating properties if it is a test function'''

    function_name = function.__name__
    if getattr(function, '__test__', True)==False or not 'test' in function_name.lower() or \
            function_name=='nottest' or function_name=='istest':
        return []
    errors = []

    # Verify naming of the test function
    if not function_name_regex.match(function_name):
        errors.append('Function %s in %s must start with test_ and contain only lower case letters, numbers, and underscores' % (function_name, file))

    # Verify level is set correctly
    if str(getattr(function, 'level', parent_level)) not in levels_available:
        errors.append('Function %s in %s does not have a valid level attribute, valid options are %s' % (function_name, file, ', '.join(levels_available)))

    # Verify suite is set correctly
    suite_attr = getattr(function, 'suite', parent_suite)
    suites = []
    if isinstance(suite_attr, list):
        suites.extend(suite_attr)
    else:
        suites.append(suite_attr)
    error_found = False
    for suite in suites:
        if not error_found and suite not in suites_available:
            error_found = True
            errors.append('Function %s in %s does not have a valid suite attribute, valid options are %s' % (function_name, file, ', '.join(suites_available)))

    # Verify owner is set correctly
    owner = getattr(function, 'owner', parent_owner)
    if owner==None or owner=='':
        errors.append('Function %s in %s does not have a valid owner attribute, must be a non-empty string' % (function_name, file))

    # Verify jira is set correctly
    jira = getattr(function, 'jira', parent_jira)
    if jira==None or jira=='':
        errors.append('Function %s in %s does not have a valid jira attribute, must be a non-empty string' % (function_name, file))

    return errors

def process_class(file, clazz):
    '''Processes a class by validating properties and then processing all contains functions'''

    clazz_name = clazz.__name__
    clazz_module = getattr(clazz, '__module__', True)
    # Make use of directory list obtained in the main method
    adaptive_module = False
    for module in adaptive_directories:
        if module in clazz_module:
            adaptive_module = True

    if clazz_module.startswith('ace.'):
      adaptive_module = False

    if not adaptive_module:
        return []

    errors = []

    # Verify naming of the test class
    if not class_name_regex.match(clazz_name):
        errors.append('Class %s in %s must start with Test and contain only camel case letters and numbers' % (clazz_name, file))

    for function in inspect.getmembers(clazz, predicate=inspect.ismethod):
        if function[0].lower()=='setup' or function[0].lower()=='teardown':
          continue
        errors.extend(process_class_function(file, function[1],
              parent_suite=getattr(clazz, 'suite', None), 
              parent_level=getattr(clazz, 'level', None),
              parent_owner=getattr(clazz, 'owner', None),
              parent_jira=getattr(clazz, 'jira', None)))

    return errors

def process_test_file(file):
    '''Processes a test file to find and process contained functions and classes'''

    module_name = file[2:-3].replace('/', '.')
    try:
        __import__(module_name)
    except ImportError as e:
        print 'Warning: Could not load module %s from %s: %s' % (module_name, file, e)
        return []
    errors = []

    # Verify naming of the test function
    if not file_name_regex.match(os.path.basename(file)):
        errors.append('The file %s must start with test_ and contain only lower case letters, numbers, and underscores' % file)

    module = sys.modules[module_name]
    for function in inspect.getmembers(sys.modules[module_name], predicate=inspect.isfunction):
        errors.extend(process_free_function(file, function[1]))
    for clazz in inspect.getmembers(sys.modules[module_name], predicate=inspect.isclass):
        errors.extend(process_class(file, clazz[1]))

    return errors

def main():
    global adaptive_directories

    print 'Checking all tests for valid attributes...'
    if os.getcwd()!=os.path.abspath('.') or not os.path.exists('.git'):
        print 'This script must be run from the root directory of the repository'
        sys.exit(1)

    # Walk directory structure and get all python files in each sub-dir
    errors = []
    for dirname, dirnames, filenames in os.walk('.'):
        if dirname is '.':
            dirnames.remove('.git')
            dirnames.remove('ace')
            if os.path.exists('.idea'):
                dirnames.remove('.idea')
            # set the adaptive directories for modules check later on
            adaptive_directories = dirnames
            continue

        # Verify naming of directories
        for dir in dirnames:
            if not dir_name_regex.match(dir):
                errors.append('The directory %s must contain only lower case letters, numbers, and underscores' % os.path.join(dirname, dir))

        # Verify presence of __init__.py file
        if not os.path.exists(os.path.join(dirname, '__init__.py')):
            errors.append('The directory %s must have an __init__.py file in order to be included in testing' % dirname)

        for filename in filenames:
            if filename.endswith('.py') and filename!='__init__.py':
                errors.extend(process_test_file(os.path.join(dirname, filename)))

    if errors:
        print '\nValidation errors occurred:'
        print '\n'.join(errors)
        return 1

    print 'All tests were successfully validated'
    return 0

if __name__ == '__main__':
    sys.exit(main())
