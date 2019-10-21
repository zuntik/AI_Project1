
# Following 2 lines necessary if aima code not in same dir
import sys
sys.path.insert(1, 'aima-python')


from search import *

class ASARProblem(Problem):

    """ The problem of search the best scheduling options to increase company
    profit """
    
    def __init__(self, filename=None):
        """The constructor calls the load method for the specific filename"""
        while filename is None or filename=='':
            filename = input('filename: ')
        self.load(open(filename,'r'))


    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""

        """ path will be the negative of the profit """

        return c + 1

    def heurisitc(self, n):
        """Return the heuristic of node n"""
        raise NotImplementedError

    def load(self, f):
        """Loads a problem from a (opened) file object f"""

        ### Load the data


        lines = f.read().splitlines()
        A = [ l for l in lines if  l.find("A")==0 ]
        P = [ l for l in lines if  l.find("P")==0 ]
        L = [ l for l in lines if  l.find("L")==0 ]
        C = [ l for l in lines if  l.find("C")==0 ]

        # rolltimes is a dictionary which contains the rolltimes for each class
        self.rolltimes = {s.split()[1]: int(s.split()[2]) for s in C }

        # legs is a dictionary which conatins 
        def Leg(s):
            d = {
                'from': s[1],
                'to': s[2],
                'duration': int(s[3]),
            }
            for i in range( 4, len(s), 2 ):
                d[s[i]] = int(s[i+1])
            return d
        self.legs = [ Leg(s.split()) for s in L ]

        print(self.rolltimes)
        print(self.legs)

        ### Now that the data is loaded we must define the initial states

        #self.initial = 

        # defining a goal state will not be necessary because there is more than
        # one goal state


    def save(self, f , s):
        """saves a solution state s to a (opened) file object f"""
        raise NotImplementedError

if __name__ == "__main__":
    ASARProblem('./examples/simple1.txt')
