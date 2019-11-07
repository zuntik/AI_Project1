if __name__ == "__main__":
    import sys
    sys.path.append('./aima-python/')
    import os

from search import *

from copy import deepcopy

class ASARProblem(Problem):

    """ The problem of search the best scheduling options to increase company
    profit """

    class State:
        def __init__(self,legs,planes):
            self.legs = legs
            self.planes = planes

        def __eq__(self, obj):
            return self.legs == obj.legs and self.planes == obj.planes

        def __hash__(self):
            string = ''.join( str(leg['hash']) for leg in self.legs )
            string = string.join( str(leg['hash']) \
                for plane in self.planes.values() for leg in plane['legs'] )
            return hash(string)

        def __lt__(self,a):
            return True

    
    def __init__(self, filename=None):
        """The constructor calls the load method for the specific filename"""
        if filename is None:
            return
        self.load(open(filename,'r'))


    def actions(self, state):
        """Return the actions that can be executed in the given state."""
        
        # TODO Yielder!
        actions = list()

        for pname,p in state.planes.items():
            # pname is the name of the current name

            if p['current'] is None:
                actions += [{'name':pname,'leg':leg} for leg in state.legs]
            else:
                for leg in state.legs:
                    if leg['from'] == p['current'] and p['ready'] + leg['duration'] <= self.airports[leg['to']]['close'] and p['ready'] < self.airports[leg['from']]['close']:
                        actions.append({'name':pname,'leg':deepcopy(leg)})
        
        return actions


    def result(self, state, action):
        """Return the state that results from executing the given action in the
        given state. The action must be one of self.actions(state)."""

        # the values are stored in the correct order
        state = ASARProblem.State(deepcopy(state.legs),deepcopy(state.planes))
        planes = state.planes
        legs = state.legs

        # leg is the leg to atribute
        leg = deepcopy(action['leg'])
        legs.remove(action['leg'])

        # the action changes one of the planes
        plane = planes[action['name']]
    
        if plane['current'] is None:
            plane['initial'] = leg['from']
            plane['ready'] = self.airports[leg['from']]['open']

        if plane['ready'] + leg['duration'] < self.airports[leg['to']]['open']:
            plane['ready'] = self.airports[leg['to']]['open'] - leg['duration']

        
        leg['dep'] = plane['ready']
        plane['current'] = leg['to']
        plane['legs'].append(leg)
        plane['ready'] = leg['dep'] + leg['duration'] + plane['rolltime']

        return state

    def goal_test(self, state):
        """Return True if the state is a goal. """
        # if there are no more legs to atribute and all of the planes are
        # currently where they started
        return (not state.legs) and all( p['initial']==p['current'] for p in state.planes.values())

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1."""
        # the step cost is the difference between the ideal profit and the actual profit
        return c + max( [ action['leg'][c] for c in self.classes ] ) - action['leg'][state1.planes[action['name']]['class']]

    def heuristic(self, n):
        """Return the heuristic of node n"""
        return 0

    h = heuristic

    def load(self, f):
        """Loads a problem from a (opened) file object f"""

        ### Load the data

        lines = f.read().splitlines()
        A = [ l for l in lines if  l.find("A")==0 ]
        P = [ l for l in lines if  l.find("P")==0 ]
        L = [ l for l in lines if  l.find("L")==0 ]
        C = [ l for l in lines if  l.find("C")==0 ]

        to_minutes = lambda x: (x//100)*60 + x%100

        # rolltimes is a dictionary which contains the classes for each class
        classes = {s.split()[1]: to_minutes(int(s.split()[2])) for s in C }

        # legs is a dictionary which conatins 
        def Leg(s):
            to_minutes = lambda x: (x//100)*60 + x%100
            hashh=s.__hash__()
            s = s.split()
            l = {
                'from': s[1],
                'to': s[2],
                'duration': to_minutes(int(s[3])),
                'dep': None,
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

        to_time = lambda t: ( '0' + str(t//60)  if t//60<10 else str(t//60) )\
                    + ( '0' + str(t%60)  if t%60<10 else str(t%60) )
        
        profit = 0
        for pn,p in s.planes.items():
            line = 'S ' + pn 
            if p['initial'] is None:
                continue
            
            for l in p['legs']:
                line += ' ' + to_time(l['dep'])  +  ' ' + l['from'] + ' ' + l['to']
                profit+=l[p['class']]
            f.write(line + '\n')
        
        f.write('P ' + str(float(profit))+'\n')


if __name__ == "__main__":

    for i in range(1,9):

        try:
            os.remove('examples/simple'+str(i)+'_solved.txt')
        except:
            pass
        fp_in = open('examples/simple'+str(i)+'.txt','r')
        fp_out = open('examples/simple'+str(i)+'_solved.txt','w')

        problem = ASARProblem()
        problem.load(fp_in)
        final_node = astar_search(problem,problem.heuristic)

        if final_node is None:
            problem.save(fp_out, None)
        else:
            problem.save(fp_out, final_node.state)
