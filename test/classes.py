
def process(inp):
    if inp>10:
        return 20
    else:
        return inp


class test:

    def __init__(self,t):
        self.data = t

    def run(self):
        return self.data*2

class testtwo(test):

    def runtwo(self):
        stuff = self.run()
        return stuff*4

def final(t):
    fin = t.run()
    other = t.runtwo()
    return {fin, other}
