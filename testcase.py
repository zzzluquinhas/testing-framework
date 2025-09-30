class TestCase:
	def __init__(self, test_method_name):
		self.test_method_name = test_method_name

	def run(self):
		self.set_up()    # chama método de setup
		test_method = getattr(self, self.test_method_name)
		test_method()    # chama método de teste 
		self.tear_down() # chama método de teardown 

	def set_up(self):
		pass

	def tear_down(self):
		pass