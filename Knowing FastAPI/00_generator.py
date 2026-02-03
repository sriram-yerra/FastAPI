from fastapi import FastAPI, HTTPExecption

'''
Normal Function
def get_numbers():
    return [1, 2, 3]
'''
def read_file():
    with open("bigfile.txt") as f:
        return f.readlines()

'''
Generator Function
def get_numbers():
    yield 1
    yield 2
    yield 3

➡ Returns one value at a time
➡ Memory efficient
➡ Pauses after each yield

How it Works Internally
gen = get_numbers()

next(gen)  # 1
next(gen)  # 2
next(gen)  # 3

Each next() resumes the function from where it paused.
'''
def read_file():
    with open("bigfile.txt") as f:
        for line in f:
            yield line