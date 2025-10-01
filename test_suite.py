from testcase import TestCase
from test_result import TestResult

class TestSuite:
    def __init__(self):
        self.tests = []

    def add_test(self, test: TestCase):
        self.tests.append(test)

    def run(self, result: TestResult):
        for test in self.tests:
            test.run(result)