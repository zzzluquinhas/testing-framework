from test_result import TestResult

class TestCase:
	def __init__(self, test_method_name):
		self.test_method_name = test_method_name

	def run(self, result: TestResult):
		result.test_started()
		self.set_up()
		try:
			test_method = getattr(self, self.test_method_name)
			test_method()
		except AssertionError as e:
			result.add_failure(self.test_method_name)
		except Exception as e:
			result.add_error(self.test_method_name)
		self.tear_down()

	def set_up(self):
		pass

	def tear_down(self):
		pass