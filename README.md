# Implementando um Framework de Teste

Iremos desenvolver e testar um framework de teste no estilo [xUnit](https://en.wikipedia.org/wiki/XUnit).
Criar um framework de teste é interessante por algumas razões:

- Aprender detalhes sobre o seu design e funcionamento, por exemplo, como testes e fixtures são executados.
- Conhecer na prática (e implementar) conceitos chave, tais como *test case*, *test suite* e *test runner*.
- Exercitar de forma aplicada boas práticas de desenvolvimento e teste de software.

Note que um framework de teste é um software como outro qualquer, portanto, também deve ser testado.
Porém, existe um desafio: devemos testar o código desenvolvido com o próprio framework.

Este framework de teste é adaptado do livro *Test Driven Development: By Example* de Kent Beck.
O framework de teste será desenvolvido na linguagem Python e pode ser visto como uma prova de conceito ([MVP](https://en.wikipedia.org/wiki/Minimum_viable_product)) do framework padrão de Python [unittest](https://docs.python.org/3/library/unittest.html).

## 1. Introdução

Frameworks de teste facilitam a escrita, a execução e a geração de relatórios de teste:

- **Escrita:** Um conjunto de classes e métodos (APIs) são fornecidos pelos frameworks de teste para facilitar a escrita de testes, tais como `assert_equals`, `set_up`, `tear_down`, etc.
  
- **Execução:** No mundo real, sistemas de software podem conter milhares de testes. Portanto, frameworks de teste devem permitir a execução dos testes de forma simples e rápida.

- **Relatórios:** Quando os testes são executados, queremos facilmente identificar os testes que falharam ou verificar que todos passaram. Portanto, frameworks de teste devem também gerar tais resultados para os desenvolvedores.

O pseudocódigo abaixo ilustra de forma simplificada *como* os métodos de teste são executados em um framework de teste:

```
test_case_classes = conjunto de classes de teste

for test_case_class in test_case_classes {
    for test_method in test_case_class {
        tc = new test_case_class()  // instancia classe de teste
        tc.set_up()                 // chama método de setup 
        tc.run(test_method)         // chama método de teste 
        tc.tear_down()              // chama método de teardown 
    }
}
```

Dado um conjunto de classes de teste `test_case_classes`, iteramos em cada classe de teste `test_case_class` e em cada método de teste `test_method`.
Para cada método de teste `test_method` instanciamos a sua respectiva classe de teste.
Em seguida, realizamos três passos: chamar o método `set_up`, chamar o método de teste `test_method` e chamar o método `tear_down`.

Observe que a classe de teste `test_case_class` é instanciada uma vez para *cada* método de teste.
Além disso, as fixtures (`set_up` e `tear_down`) são chamadas em cada instância.
Por exemplo, suponha uma classe de teste `MyTest` com 10 métodos de teste; `MyTest` será instanciada 10 vezes pelo framework de teste, isto é, uma vez para cada método de teste.
Cada fixture também será executada 10 vezes, ou seja, uma vez para cada método de teste.
Isso ocorre pois cada método de teste deve ser executado de forma completamente independente dos demais.

Outro ponto importante (não mostrado no pseudocódigo) é que resultados podem ser coletados durante a execução dos testes.
Por exemplo, podemos coletar quantos testes foram executados, os testes que falharam, o tempo de execução, dentre outras informações.

Para implementar os conceitos acima, utilizamos orientação a objetos.
As principais classes em um framework de teste no estilo xUnit são:

- `TestCase`: Classe base utilizada para criar novos casos de teste.
- `TestSuite`: Representa uma conjunto de casos de testes.
- `TestResult`: Sumariza os resultados da execução dos testes.
- `TestLoader`: Utilizada para criar suítes de teste a partir de casos de casos de teste.
- `TestRunner`: Orquestra a execução dos testes e fornece relatórios.

## 2. Classe TestCase

Para criar casos de teste no xUnit, definimos uma classe de teste que estende da classe `TestCase` fornecida pelo framework:

```
class MyTest extends TestCase {
    set_up() { ... }
    tear_down() { ... }
    test_a() { ... }
    test_b() { ... }
    test_c() { ... }
}
```

Mas como esses testes são executados pelo framework de teste?

Normalmente, não paramos para pensar sobre isso pois os frameworks de teste nos fornecem ferramentas para simplificar o processo de execução dos testes, por exemplo, via linha de comando, IDE de programação, etc.
No entanto, frameworks de teste também devem permitir a execução dos testes diretamente via código.
Por exemplo, idealmente, devemos poder rodar os testes da seguinte forma:

```
test = new MyTest('test_a')
test.run()

test = new MyTest('test_b')
test.run()

test = new MyTest('test_c')
test.run()
```

No código acima, o método `run` da classe `TestCase` é responsável por chamar as fixtures do teste assim como executar o método de teste em si.
Note que cada método de teste é executado em uma instância de `MyTest`, uma vez que os métodos de teste são *independentes*.

Uma alternativa é utilizar uma suíte de testes para evitar duplicação de código e simplificar a execução:

```
test_suite = new TestSuite()

test_suite.add(MyTest('test_a'))
test_suite.add(MyTest('test_b'))
test_suite.add(MyTest('test_c'))

test_suite.run()
```

Portanto, a classe `TestCase` (e `TestSuite`) do nosso framework deve possuir um método `run` responsável por executar os métodos de teste e as fixtures.
Além disso, a classe `TestCase` deve possuir um construtor que recebe uma string com o nome do método a ser testado.

Em Python, temos a seguinte versão inicial da classe `TestCase`:

```python
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
```

- O contrutor (`__init__`) recebe uma string com o nome do método de teste que deve ser executado. Mas como executar esse método de teste com base apenas no seu nome? Felizmente, podemos utilizar a função nativa de Python [getattr](https://docs.python.org/3/library/functions.html#getattr). Dado uma string com o nome de um método, `getattr` nos permite executar esse método, por exemplo, `getattr(x, 'test_foo')` é equivalente a `x.test_foo`.

- O método `run` implementa o padrão de projeto [template method](https://refactoring.guru/design-patterns/template-method). O *template method* é um método em uma superclasse que define o "esqueleto" de um algoritmo com um conjunto de passos que devem ser redefinidos nas subclasses. Para utilizar esse algoritmo, o cliente deve criar a sua própria subclasse.

- No nosso contexto de testes, o *template method* `run` define o esqueleto com os seguintes passos: chamar o método `set_up`, chamar o método de teste que possui nome `test_method_name` e chamar o método `tear_down`. Note que esses passos são similares ao [pseudocódigo](https://github.com/andrehora/teste-de-software/blob/main/implementando-framework-de-teste.md#1-introdu%C3%A7%C3%A3o) apresentado no início.

Para entender melhor o funcionamento de `TestCase`, vamos fazer um pequeno teste.
Considere a classe `MyTest` a seguir que estende de `TestCase`:

```python
class MyTest(TestCase):

    def set_up(self):
        print('set_up')

    def tear_down(self):
        print('tear_down')

    def test_a(self):
        print('test_a')

    def test_b(self):
        print('test_b')

    def test_c(self):
        print('test_c')
```

Podemos então executar os testes `test_a`, `test_b` e `test_c` da seguinte forma:

```python
test = MyTest('test_a')
test.run()

test = MyTest('test_b')
test.run()

test = MyTest('test_c')
test.run()
```

A seguinte saída é gerada, indicando que o *template method* `run` funciona corretamente.
Isto é, `set_up` e `tear_down` são chamados sempre antes e depois, respectivamente, de cada método de teste.

```
set_up
test_a
tear_down
set_up
test_b
tear_down
set_up
test_c
tear_down
```

## 3. Classe TestResult

A classe `TestCase` nos permite executar os testes de forma simples, mas não temos nenhuma informação sobre a execução dos testes.
`TestResult` permite coletar os resultados da execução dos testes.
Inicialmente, geramos apenas a seguinte saída, indicando o número de testes executados, falhas e erros:

```
1 run, 0 failed, 0 error
```

A classe `TestResult` é responsável por sumarizar os resultados da execução:

```python
class TestResult:

    RUN_MSG = 'run'
    FAILURE_MSG = 'failed'
    ERROR_MSG = 'error'

    def __init__(self, suite_name=None):
        self.run_count = 0
        self.failures = []
        self.errors = []

    def test_started(self):
        self.run_count += 1

    def add_failure(self, test):
        self.failures.append(test)

    def add_error(self, test):
        self.errors.append(test)

    def summary(self):
        return f'{self.run_count} {self.RUN_MSG}, ' \
               f'{str(len(self.failures))} {self.FAILURE_MSG}, ' \
               f'{str(len(self.errors))} {self.ERROR_MSG}'
```

Essa classe contém três atributos (`run_count`, `failures` e `errors`) para armazenar as informações da execução dos testes.
O método `test_started` representa um contador de testes.
Os métodos `add_failure` e `add_error` salvam os métodos de testes com falhas e erros.
O método `summary` sumariza os dados armazenados nos atributos, gerando o resultado do tipo: `1 run, 0 failed, 0 error`.

O próximo passo é integrar `TestResult` à classe `TestCase`.
Para isso, alteramos a assinatura do método `run` para receber um resultado (parâmetro `result`) e coletamos os dados necessários:

```python
class TestCase:

    def run(self, result):
        result.test_started()
        ...
```

Agora os testes devem ser executados da seguinte forma:

```python

result = TestResult()

test = MyTest('test_a')
test.run(result)

test = MyTest('test_b')
test.run(result)

test = MyTest('test_c')
test.run(result)

print(result.summary())
```

O código acima produz o seguinte resultado:

```
3 run, 0 failed, 0 error
```

O leitor mais atento vai perceber que devemos modificar um pouco o método `run` de `TestCase` para coletar dados de falhas e erros,
conforme apresentado a seguir:

```python
class TestCase:

    def run(self, result):
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
```

Especificamente, o código anterior executa o teste dentro de um bloco `try`.
Caso ocorra alguma exceção, então coletamos as falhas e os erros:

- Caso ocorra um  [AssertionError](https://docs.python.org/3/library/exceptions.html#AssertionError), isso indica que o comando `assert` falhou. Portanto, salvamos o nome do método de teste através de `add_failure`.
- Caso ocorra uma outra `Exception`, isso indica um erro no teste (por exemplo, uma divisão por zero, um erro ao abrir um arquivo, uma falha de conexão com BD, entre outros). Essa informação é salva através de `add_error`.

Com isso, concluímos o básico do nosso framework de teste, com as versões iniciais da classe `TestCase` e `TestResult`.
A seguir, iremos começar a testar o código desenvolvido até o momento.

## 4. Testando TestCase

Como testar o framework de teste?

Primeiramente, iremos criar uma classe auxiliar `TestStub` que vai estender de `TestCase`.
Essa classe não é o teste em si, mas uma classe de suporte ao teste que simula uma classe de teste.
`TestStub` contém três testes: um teste que passa com sucesso (`test_success`), um teste que falha (`test_failure`) e um teste que lança uma exceção (`test_error`).

```python
class TestStub(TestCase):

    def test_success(self):
        assert True

    def test_failure(self):
        assert False

    def test_error(self):
        raise Exception
```

A classe `TestCaseTest` apresenta o primeiro teste para `TestCase`.
`TestCaseTest` possui uma fixture que inicializa `TestResult` e quatro métodos de teste:

```python
class TestCaseTest(TestCase):

    def set_up(self):
        self.result = TestResult()

    def test_result_success_run(self):
        stub = TestStub('test_success')
        stub.run(self.result)
        assert self.result.summary() == '1 run, 0 failed, 0 error'

    def test_result_failure_run(self):
        stub = TestStub('test_failure')
        stub.run(self.result)
        assert self.result.summary() == '1 run, 1 failed, 0 error'

    def test_result_error_run(self):
        stub = TestStub('test_error')
        stub.run(self.result)
        assert self.result.summary() == '1 run, 0 failed, 1 error'

    def test_result_multiple_run(self):
        stub = TestStub('test_success')
        stub.run(self.result)
        stub = TestStub('test_failure')
        stub.run(self.result)
        stub = TestStub('test_error')
        stub.run(self.result)
        assert self.result.summary() == '3 run, 1 failed, 1 error'
```

Cada teste de `TestCaseTest` executa os testes de `TestStub` e verifica o resultado gerado:

- O teste `test_result_success_run` verifica se `test_success` foi executado com sucesso, gerando o resultado `1 run, 0 failed, 0 error`.
- O teste `test_result_failure_run` verifica se `test_failure` gera uma falha, enquanto o teste `test_result_error_run` verifica se `test_error` lança uma exceção.
- Por fim, o teste `test_result_multiple_run` executa os três testes de `TestStub` e verifica se o resultado gerado é `3 run, 1 failed, 1 error`.

> [!NOTE] 
> Observe que todos os testes utilizam o comando [assert](https://stackoverflow.com/questions/5142418/what-is-the-use-of-assert-in-python) nativo de Python para verificar uma condição. Caso essa condição não seja verdade, a exceção `AssertionError` é lançada. Mais adiante, iremos desenvolver nossos próprios comandos asserts, tais como `assert_equal`, `assert_true` e `assert_false`.
Por enquanto, o `assert` nativo de Python é suficiente!

Para saber se o teste `TestCaseTest` está de fato correto, devemos, claro, executar esse teste.
Podemos rodar `TestCaseTest` através do seguinte código já conhecido:

```python
result = TestResult()

test = TestCaseTest('test_result_success_run')
test.run(result)

test = TestCaseTest('test_result_failure_run')
test.run(result)

test = TestCaseTest('test_result_error_run')
test.run(result)

test = TestCaseTest('test_result_multiple_run')
test.run(result)

print(result.summary())
```

Ao executar o teste `TestCaseTest` através do código acima, teremos o seguinte relatório de teste, indicando que os quatro métodos de teste e `TestCaseTest` passaram com sucesso!

```
4 run, 0 failed, 0 error
```

### Mais Testes para TestCase

Em seguida, criamos outra classe auxiliar `TestSpy` para testar `TestCase`.
`TestSpy` nos ajuda a verificar o comportamento do *template method*, isto é, se as fixtures estão sendo chamadas antes/depois do método de teste:

```python
class TestSpy(TestCase):

    def __init__(self, name):
        TestCase.__init__(self, name)
        self.was_run = False
        self.was_set_up = False
        self.was_tear_down = False
        self.log = ""

    def set_up(self):
        self.was_set_up = True
        self.log += "set_up "

    def test_method(self):
        self.was_run = True
        self.log += "test_method "

    def tear_down(self):
        self.was_tear_down = True
        self.log += "tear_down"
```

`TestSpy` é similar a `TestStub` no sentido de que simula uma classe de teste.
No entanto, `TestSpy` captura ("espiona") detalhes da execução:

- Os atributos `was_run`, `was_set_up` e `was_tear_down` verificam se o método de teste e as fixtures foram executadas.
- O atributo `log` salva o nome dos métodos executados mantendo a ordem de execução.

Com base em `TestSpy`, podemos criar novos testes para `TestCase`:

```python
class TestCaseTest(TestCase):

    def set_up(self):
        self.result = TestResult()

    ...

    def test_was_set_up(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        assert spy.was_set_up

    def test_was_run(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        assert spy.was_run

    def test_was_tear_down(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        assert spy.was_tear_down

    def test_template_method(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        assert spy.log == "set_up test_method tear_down"
```

Note que:

- Os três primeiros testes verificam se os métodos de `TestSpy` foram chamados a partir do *template method*.
- O teste `test_template_method` verifica a ordem de execução dos métodos de `TestSpy`, isto é, `set_up test_method tear_down`.

Ao rodar todos os testes de `TestCaseTest`, teremos agora 8 testes passando com sucesso:

```python
...

test = TestCaseTest('test_was_set_up')
test.run(result)

test = TestCaseTest('test_was_run')
test.run(result)

test = TestCaseTest('test_was_tear_down')
test.run(result)

test = TestCaseTest('test_template_method')
test.run(result)

print(result.summary())
```

```
8 run, 0 failed, 0 error
```

Observe que o código para executar os testes vai crescer à medida que novos testes forem adicionados.
Nas próximas seções, iremos criar as classes `TestSuite`, `TestLoader` e `TestRunner` para simplificar a execução dos testes.


## 5. Classe TestSuite

`TestSuite` representa uma coleção de casos de testes.
Por exemplo, com uma suíte de testes, podemos rodar o teste anterior (`TestCaseTest`) da seguinte forma:

```python
result = TestResult()
suite = TestSuite()

suite.add_test(TestCaseTest('test_result_success_run'))
suite.add_test(TestCaseTest('test_result_failure_run'))
...

suite.run(result)
print(result.summary())
```

Note que a classe `TestSuite` e `TestCase` possuem a mesma interface para executar os testes, isto é, `run(result)`.
A diferença entre ambas é que `TestSuite` representa uma coleção de testes, ou seja, ao executar os testes utilizando uma suíte, todos os testes desta coleção de testes são executados.

Para implementar `TestSuite` iremos utilizar o padrão de projeto [composite](https://refactoring.guru/design-patterns/composite), que trata um grupo de objetos (todo, isto é ``TestSuite``) da mesma forma que um único objeto (parte, isto é `TestCase`).

A classe `TestSuite`, portanto, contém uma coleção de testes e implementa o método `run(result)` que apenas itera na coleção e executa cada teste:

```python
class TestSuite:

    def __init__(self):
        self.tests = []

    def add_test(self, test):
        self.tests.append(test)

    def run(self, result):
        for test in self.tests:
            test.run(result)
```

`TestCase` e `TestSuite` possuem agora a mesma interface de execução dos testes, portanto, pode-se rodar um ou dezenas de testes da mesma forma, ou seja, através do método `run`.

### Testando TestSuite

A seguir, criamos a classe de teste `TestSuiteTest` para testar `TestSuite`.
Neste caso, também iremos utilizar a classe `TestStub` para dar suporte a criação dos testes:

```python
class TestSuiteTest(TestCase):

    def test_suite_size(self):
        suite = TestSuite()

        suite.add_test(TestStub('test_success'))
        suite.add_test(TestStub('test_failure'))
        suite.add_test(TestStub('test_error'))

        assert len(suite.tests) == 3

    def test_suite_success_run(self):
        result = TestResult()
        suite = TestSuite()
        suite.add_test(TestStub('test_success'))

        suite.run(result)

        assert result.summary() == '1 run, 0 failed, 0 error'

    def test_suite_multiple_run(self):
        result = TestResult()
        suite = TestSuite()
        suite.add_test(TestStub('test_success'))
        suite.add_test(TestStub('test_failure'))
        suite.add_test(TestStub('test_error'))

        suite.run(result)

        assert result.summary() == '3 run, 1 failed, 1 error'
```

`TestSuiteTest` possui três testes:

- O teste `test_suite_size` verifica a quantidade de testes presente na suíte.
- O teste `test_suite_success_run` executa um teste através da suíte.
- Por fim, o teste `test_suite_multiple_run` executa múltiplos testes através da suíte.

Observe que podemos utilizar nossa própria suíte de testes para executar os 8 testes de `TestCaseTest` e os 3 testes de `TestSuiteTest`:

```python
result = TestResult()
suite = TestSuite()

suite.add_test(TestCaseTest('test_result_success_run'))
suite.add_test(TestCaseTest('test_result_failure_run'))
suite.add_test(TestCaseTest('test_result_error_run'))
suite.add_test(TestCaseTest('test_result_multiple_run'))
suite.add_test(TestCaseTest('test_was_set_up'))
suite.add_test(TestCaseTest('test_was_run'))
suite.add_test(TestCaseTest('test_was_tear_down'))
suite.add_test(TestCaseTest('test_template_method'))

suite.add_test(TestSuiteTest('test_suite_size'))
suite.add_test(TestSuiteTest('test_suite_success_run'))
suite.add_test(TestSuiteTest('test_suite_multiple_run'))

suite.run(result)
print(result.summary())
```

Resultado:

```
11 run, 0 failed, 0 error
```

## 6. Classes TestLoader e TestRunner

Conforme já mencionamos, o código para execução dos testes está se tornando cada vez maior.
As classes `TestLoader` e `TestRunner` surgem para resolver esse problema.

Queremos que os métodos de teste de uma classe de teste sejam descobertos automaticamente, sem a necessidade de escrever o nome de cada método de teste.
Métodos de teste são todos aqueles na classe de teste que possuem o prefixo *test*.
Dado uma classe de teste, `TestLoader` encontra os seus métodos de teste através de `get_test_case_names` e retorna uma suíte pronta para ser executada através de `make_suite`:

```python
class TestLoader:

    TEST_METHOD_PREFIX = 'test'

    def get_test_case_names(self, test_case_class):
        methods = dir(test_case_class)
        test_method_names = list(filter(lambda method: 
            method.startswith(self.TEST_METHOD_PREFIX), methods))
        return test_method_names

    def make_suite(self, test_case_class):
        suite = TestSuite()
        for test_method_name in self.get_test_case_names(test_case_class):
            test_method = test_case_class(test_method_name)
            suite.add_test(test_method)
        return suite
```

### TestLoader

Os testes a seguir verificam alguns comportamentos de `TestLoader` para criar suítes (`test_create_suite` e `test_create_suite_of_suites`) e encontrar métodos de teste (`test_get_multiple_test_case_names` e `test_get_no_test_case_names`):

```python
class TestLoaderTest(TestCase):

    def test_create_suite(self):
        loader = TestLoader()
        suite = loader.make_suite(TestStub)
        assert len(suite.tests) == 3

    def test_create_suite_of_suites(self):
        loader = TestLoader()
        stub_suite = loader.make_suite(TestStub)
        spy_suite = loader.make_suite(TestSpy)

        suite = TestSuite()
        suite.add_test(stub_suite)
        suite.add_test(spy_suite)

        assert len(suite.tests) == 2

    def test_get_multiple_test_case_names(self):
        loader = TestLoader()
        names = loader.get_test_case_names(TestStub)
        assert names == ['test_error', 'test_failure', 'test_success']

    def test_get_no_test_case_names(self):

        class Test(TestCase):
            def foobar(self):
                pass

        loader = TestLoader()
        names = loader.get_test_case_names(Test)
        assert names == []
```

Podemos, portanto, utilizar `TestLoader` para executar os testes da seguinte forma, simplificando bastante a execução dos testes:

```python
result = TestResult()
loader = TestLoader()
suite = loader.make_suite(TestLoaderTest)
suite.run(result)
print(result.summary())
```

Resultado:

```
4 run, 0 failed, 0 error
```

Observe que *não* precisamos mais escrever o nome dos métodos de teste, uma vez que `TestLoader` detecta automaticamente os testes presentes na classe de teste.

Apesar do código acima ser mais simples que os anteriores, ele ainda apresenta alguns detalhes que incomodam.
Por exemplo, devemos instanciar `TestResult` e passar como argumento do método `run`.
Além disso, devemos imprimir o relatório da execução.
Por isso, precisamos de uma outra classe: `TestRunner`.

### TestRunner

A classe `TestRunner` surge para resolver esses problemas: ela orquestra a execução dos testes e fornece relatórios.
`TestRunner` contém uma referência para `TestResult`.
Ela também contém o método `run` que recebe um teste (`TestCase` ou `TestSuite`), executa-os e gera o relatório da execução:

```python
class TestRunner:

    def __init__(self):
        self.result = TestResult()

    def run(self, test):
        test.run(self.result)
        print(self.result.summary())
        return self.result
```

Note que toda a responsabilidade de executar os testes e gerar os relatórios é delegada para `TestRunner`.
Portanto, podemos rodar os testes da seguinte forma:

```python
loader = TestLoader()
suite = loader.make_suite(TestLoaderTest)

runner = TestRunner()
runner.run(suite)
```

Resultado:

```
4 run, 0 failed, 0 error
```

Outro ponto importante é que diferentes *runners* podem ser criados (por exemplo, `WebTestRunner`, `JSONTestRunner`, `UITestRunner`, etc.), sem a necessidade de modificar as classes *core* do framework: `TestCase`, `TestSuite` e `TestLoader`.

## 7. Executando Todos os Testes

Temos a até o momento três classes de teste: `TestCaseTest` (8 testes), `TestSuiteTest` (3 testes) e `TestLoaderTest` (4 testes).

Mas como podemos executar todos os 15 testes?
Para executar todos os testes, devemos utilizar as classes `TestLoader`, `TestSuite` e `TestRunner`:

```python
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
```

Resultado:

```
15 run, 0 failed, 0 error
```

## 8. Comandos Assert

Implementamos até o momento as principais classes do nosso framework de teste: `TestCase`, `TestRunner`, `TestSuite`, `TestLoader` e `TestRunner`.
Podemos facilmente executar os testes de uma classe que estende `TestCase` e gerar um relatório simples de saída no forma to `X run, Y failed, Z error`.
No entanto, para verificar o resultado do teste, estamos utilizando o `assert` nativo de Python.
Para melhor usabilidade e legibilidade dos testes, iremos desenvolver os nossos próprios asserts, tais como `assert_equal`, `assert_true` e `assert_false`.

Atualmente, escrevemos as asserções no seguinte formato:

```python
assert self.result.summary() == '1 run, 0 failed, 0 error'
assert spy.was_set_up
```

Idealmente, queremos escrevê-las como:

```python
assert_equal(self.result.summary(), '1 run, 0 failed, 0 error')
assert_true(spy.was_set_up)
```

> [!NOTE]
> Antes de continuar a leitura, reflita por um momento *onde* devemos implementar os novos asserts.
> Além disso, tente elaborar *como* essas novas funcionalidades devem ser desenvolvidas.

Os novos asserts devem ser implementados na superclasse `TestCase` para podermos utilizá-los via herança nas subclasses de teste.
A seguir, implementamos o `assert_equal`: esse código falha quando dois objetos (`first` e `second`) não são iguais, sendo lançada a exceção `AssertionError`.

```python
def assert_equal(self, first, second):
    if first != second:
        msg = f'{first} != {second}'
        raise AssertionError(msg)
```

Em seguida, definimos `assert_true` e `assert_false`:

```python
def assert_true(self, expr):
    if not expr:
        msg = f'{expr} is not true'
        raise AssertionError(msg)

def assert_false(self, expr):
    if expr:
        msg = f'{expr} is not false'
        raise AssertionError(msg)
```

O código de ambos os métodos são bastantes simples:

- `assert_true` verifica se a condição `expr` é verdade. Caso seja falsa, a exceção `AssertionError` é lançada.
- `assert_false` verifica se `expr` é falsa. Caso seja verdade, a exceção `AssertionError` é lançada.

Por fim, implementamos mais um assert bastante utilizando em Python, `assert_in`, que verifica se `member` está em `container`:

```python
def assert_in(self, member, container):
    if member not in container:
        msg = f'{member} not found in {container}'
        raise AssertionError(msg)
```

***

> [!NOTE]
> **asserts no unittest.**
> Apresentamos a seguir a definição do próprio framework unittest para os métodos `assert_true`, `assert_false` e `assertIn`.
> Observe a similaridade com a nossa implementação.
> De fato, a principal diferença é que (por simplicidade) não implementamos a possibilidade de definir uma mensagem de falha ([link](https://github.com/python/cpython/blob/main/Lib/unittest/case.py)).

```python
# test_case.py - unittest
def assertTrue(self, expr, msg=None):
    """Check that the expression is true."""
    if not expr:
        msg = self._formatMessage(msg, "%s is not true" % safe_repr(expr))
        raise self.failureException(msg)

def assertFalse(self, expr, msg=None):
    """Check that the expression is false."""
    if expr:
        msg = self._formatMessage(msg, "%s is not false" % safe_repr(expr))
        raise self.failureException(msg)
    
def assertIn(self, member, container, msg=None):
    """Just like self.assertTrue(a in b), but with a nicer default message."""
    if member not in container:
        standardMsg = '%s not found in %s' % (safe_repr(member), safe_repr(container))
        self.fail(self._formatMessage(msg, standardMsg))
```

***

### Testando os Asserts

A seguir criamos alguns testes para os asserts na classe `TestCaseTest`.

```python

class TestCaseTest(TestCase):
    
    ...

    def test_assert_true(self):
        self.assert_true(True)

    def test_assert_false(self):
        self.assert_false(False)

    def test_assert_equal(self):
        self.assert_equal("", "")
        self.assert_equal("foo", "foo")
        self.assert_equal([], [])
        self.assert_equal(['foo'], ['foo'])
        self.assert_equal((), ())
        self.assert_equal(('foo',), ('foo',))
        self.assert_equal({}, {})
        self.assert_equal({'foo'}, {'foo'})

    def test_assert_in(self):
        animals = {'monkey': 'banana', 'cow': 'grass', 'seal': 'fish'}

        self.assert_in('a', 'abc')
        self.assert_in('foo', ['foo'])
        self.assert_in(1, [1, 2, 3])
        self.assert_in('monkey', animals)
```

***

> [!NOTE]
> **Testes no unittest.**
> O framework unittest possui centenas de testes ([link](https://github.com/python/cpython/tree/main/Lib/unittest/test)).
> A seguir, listamos alguns desses testes para as classes `TestCase`, `TestSuite` e `TestLoader`.
> Note como os nomes dos métodos teste são, em grande parte, auto-explicativos.
> Consequentemente, apenas lendo os nomes dos testes, podemos perceber que diversos comportamentos distintos e casos limites são testados.

```python
class Test_TestCase
    def test_countTestCases(self)
    def test_run_call_order__failure_in_test(self)
    def test_run__returns_given_result(self)
    def test_setUp(self)
    def testAssertEqual(self)

class Test_TestSuite
    def test_init__empty_tests(self)
    def test_run__empty_suite(self)
    def test_addTest__TestCase(self)
    def test_addTest__TestSuite(self)
    def test_run(self)

class Test_TestLoader
    def test_loadTestsFromTestCase(self)
    def test_loadTestsFromTestCase__no_matches(self)
    def test_getTestCaseNames(self)
    def test_getTestCaseNames__no_tests(self)
    def test_getTestCaseNames__not_a_TestCase(self)
```

***

## Considerações Finais

Kent Beck comenta em seu livro *Test Driven Development: By Example* ([link](https://learning.oreilly.com/library/view/test-driven-development/0321146530/)) que o espírito do xUnit é a simplicidade.
Sobre essa simplicidade, Martin Fowler destacou:

> Never in the annals of software engineering was so much owed by so many to so few lines of code ([link](https://learning.oreilly.com/library/view/test-driven-development/0321146530/)).

## Referências

- Kent Benk. Test Driven Development: By Example. Addison-Wesley Professional, 2002.
- Marco Tulio Valente. Engenharia de Software Moderna: Princípios e Práticas para Desenvolvimento de Software com Produtividade, Editora: Independente, 2020.
- unittest - website: https://docs.python.org/3/library/unittest.html
- unittest - código: https://github.com/python/cpython/tree/main/Lib/unittest
