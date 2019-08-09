# def func(x):
#     return x+1

# def test_answer():
#     assert func(3) ==4

import pytest

# def f():
#     raise SystemExit(1)
    
# def test_mytest():
#     with pytest.raises(SyntaxError):
#         f()

# def test_kek():
#     assert 'foo neggs bar' == 'foo nspam bar'

class Person():
    def greet():
        return 
    
@pytest.fixture
def person():
    return Person()

def test_greet(person):
    greeting = Person.greet()
    assert greeting == 'Hi there'