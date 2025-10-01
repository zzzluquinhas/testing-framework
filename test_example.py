from test_loader_test import TestLoaderTest
from test_loader import TestLoader
from test_runner import TestRunner
from test_suite_test import TestSuiteTest
from testcase_test import TestCaseTest
from test_suite import TestSuite

loader = TestLoader()
test_case_suite = loader.make_suite(TestCaseTest)
test_suite_suite = loader.make_suite(TestSuiteTest)
test_load_suite = loader.make_suite(TestLoaderTest)

suite = TestSuite()
suite.add_test(test_case_suite)
suite.add_test(test_suite_suite)
suite.add_test(test_load_suite)

runner = TestRunner()
runner.run(suite)