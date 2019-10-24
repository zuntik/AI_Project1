
# Following 2 lines necessary if aima code not in same dir
import sys
sys.path.append('./aima-python/')

from search import *

from copy import deepcopy,copy

class ASARProblem(Problem):

    """ The problem of search the best scheduling options to increase company
    profit """

    class State:
        def __init__(self,legs,planes):
            self.legs = legs
            self.planes = planes

        def __hash__(self):
            string = ''.join( str(leg['hash']) for leg in self.legs )
            string = string.join( str(leg['hash']) \
                    for plane in self.planes.values() \
                    for leg in plane['legs'] )
            return hash(string)

        def __str__(self):
            return "State:\n" + str(self.legs) + '\n' + str(self.planes)

        def __lt__(self,a):
            return True

    
    def __init__(self, filename=None):
        """The constructor calls the load method for the specific filename"""
        while filename is None or filename=='':
            filename = input('filename: ')
        self.load(open(filename,'r'))


    # TODO change this to implement actions as generator
    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        
        """ an action is a (plane,leg) touple"""
    
        actions = list()

        for pname,p in state.planes.items():
            # pname is the name of the current name

            if p['current'] is None:
                actions = actions + [{'name':pname,'leg':leg} for leg in state.legs if self.airports[leg['from']]['open'] + leg['duration'] < self.airports[leg['to']]['close']]
            else:
                for leg in state.legs:
                    if leg['from'] == p['current'] and p['ready'] + leg['duration'] < self.airports[leg['to']]['close']:
                        actions.append({'name':pname,'leg':leg})
        
        return actions


    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        # the values are stored in the correct order
        #state = deepcopy(state)
        state = ASARProblem.State(deepcopy(state.legs),deepcopy(state.planes))
        planes = state.planes
        legs = state.legs
        
        # the action changes one of the planes
        plane = planes[action['name']]
    
        if plane['current'] is None:
            plane['initial'] = action['leg']['from']
            plane['ready'] = self.airports[action['leg']['from']]['open']

        plane['legs'].append(action['leg'])
        plane['current'] = action['leg']['to']
        plane['ready'] = plane['ready'] + action['leg']['duration'] + plane['rolltime']

        # TODO: make sure this is deep  equals!!!!!!
        legs.remove(action['leg'])

        return state

    def goal_test(self, state):
        """Return True if the state is a goal. """
        # if there are no more legs to atribute and all of the aples
        return (not state.legs) and all( p['initial']==p['current'] for p in state.planes.values())

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""

        """path will be the negative of the profit"""

        return c - action['leg'][state1.planes[action['name']]['class']]

    def heurisitc(self, n):
        """Return the heuristic of node n"""
        return - min( [min( l[k] for k in self.classes ) for l in n.state.legs] if [min( l[k] for k in self.classes ) for l in n.state.legs]!=[] else [0] ) * len(n.state.legs)

    h = heurisitc
#    def h(self,n):
#        return 0

    def load(self, f):
        """Loads a problem from a (opened) file object f"""

        ### Load the data

        lines = f.read().splitlines()
        A = [ l for l in lines if  l.find("A")==0 ]
        P = [ l for l in lines if  l.find("P")==0 ]
        L = [ l for l in lines if  l.find("L")==0 ]
        C = [ l for l in lines if  l.find("C")==0 ]

        # rolltimes is a dictionary which contains the classes for each class
        classes = {s.split()[1]: int(s.split()[2]) for s in C }

        # legs is a dictionary which conatins 
        def Leg(s):
            hashh=s.__hash__()
            s = s.split()
            l = {
                'from': s[1],
                'to': s[2],
                'duration': int(s[3]),
                'hash': hashh
            }
            for i in range( 4, len(s), 2 ):
                l[s[i]] = int(s[i+1])
            return l
        legs = [ Leg(s) for s in L ]

        def Plane(s, c):
            return {
                'class': s[2],
                'rolltime':c,
                'initial': None,
                'current': None,
                'ready': 0,
                'legs': list()
            }

        to_minutes = lambda x: (x//100)*60 + x%100
        self.airports = { s.split()[1]: \
            {'open':to_minutes(int(s.split()[2])),'close':to_minutes(int(s.split()[3]))} for s in A}

        initial_state = ASARProblem.State(\
            legs,\
            {p.split()[1]: Plane(p.split(),classes[p.split()[2]]) for p in P})


        ### Now that the data is loaded we must define the initial states

        self.initial =  initial_state

        # defining a goal state will not be necessary because there is more than
        # one goal state

        self.classes = classes


    def save(self, f , s):
        """saves a solution state s to a (opened) file object f"""
        
        if s is None:
            f.write('Infeasible\n')
            return

        to_time = lambda t: ('0' if (len(str(t//60)) == 1) else '' )\
                + str(t//60) + str(t%60) + ('0' if (len(str(t%60)) == 1) else '' )
        
        profit = 0
        for pn,p in s.state.planes.items():
            line = 'S ' + pn 
            dep = self.airports[p['initial']]['open']
            for l in p['legs']:
                line += ' ' + to_time(dep)  +  ' ' + l['from'] + ' ' + l['to']
                dep += l['duration'] + p['rolltime']
                profit+=l[p['class']]
            f.write(line + '\n')
        
        f.write('P ' + str(float(profit))+'\n')


if __name__ == "__main__":
    problem = ASARProblem('./examples/simple1.txt')

    new_state = problem.result(problem.initial,problem.actions(problem.initial)[3])
    problem.save(open('examples/simple1_solved.txt','w'),astar_search(problem,None))
