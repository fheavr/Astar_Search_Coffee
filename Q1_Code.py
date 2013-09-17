## CS 502: AI
## Assignment 1: Q1
## Russell Gillette
## A* search algorithm implementation

import string

class A_star:
    def __init__(self, world):
        self.s_world = world

        # state of the search
        self.s_closed = set() # The set of nodes already evaluated.
        self.s_open   = set() # The set of tentative nodes to be evaluated, initially containing the start node
        self.s_origin = {}    # The set of parent nodes

        self.s_cost   = {}
        self.s_f      = {}    # f(n) = cost + h(n)
        self.s_complete = 0   # boolean indicator for termination
        self.s_goal   = None  # the goal node that was reached by the search

        # initialize start state
        for node in self.s_world.w_start:
            self.s_open.add(node)
            self.s_cost[node.hash] = 0
            self.s_f[node.hash] = self.heuristic(node)

        # add blocks we are not allowed to traverse into the list of elements already traversed
        for node in self.s_world.w_blocked:
            self.s_closed.add(node)
            print "Inaccessible Tile: ( ", node.x, ", ", node.y, ", ", node.coffee, " )"
            

    # heuristic, currently defined to be the manhatan distance to goal
##    def heuristic(self, node):
##        estimate = "inf"
##        for g in self.s_world.w_goal:
##            tmp = self.s_world.x_weight(node.x, g.x) * abs(node.x - g.x) + \
##                  self.s_world.y_weight(node.y, g.y) * abs(node.y - g.y)
##            estimate = tmp if tmp < estimate else estimate
##        return estimate

    # heuristic, defined to be mahattan distance to closest coffee shop +
    # manhatan distance to goal (or just to goal if already having coffee)
    def heuristic(self, node):
        estimate = "inf"
        for g in self.s_world.w_goal:
            if g.coffee == 1 and node.coffee != g.coffee:
                for c in self.s_world.w_coffee:
                   tmp = self.s_world.x_weight(c.y, g.y) * abs(c.x - g.x) + \
                         self.s_world.y_weight(c.y, g.y) * abs(c.y - g.y) + \
                         self.s_world.x_weight(node.x, c.x) * abs(node.x - c.x) + \
                         self.s_world.y_weight(node.y, c.y) * abs(node.y - c.y)
                   estimate = tmp if tmp < estimate else estimate
            else:
                tmp = self.s_world.x_weight(node.x, g.x) * abs(node.x - g.x) + \
                      self.s_world.y_weight(node.y, g.y) * abs(node.y - g.y)
                estimate = tmp if tmp < estimate else estimate
        return estimate

    def expand(self, node):
        self.s_open.remove(node)
        self.s_closed.add(node)

        lnode = node.left(self.s_world)
        if not lnode in self.s_closed:
            eh_left = lnode.hash
            self.s_cost[eh_left] = self.s_cost[node.hash] + self.s_world.w_left
            self.s_f[eh_left] = self.s_cost[eh_left] + self.heuristic(lnode)
            self.s_origin[eh_left] = node
            self.s_open.add(lnode)

        rnode = node.right(self.s_world)
        if not rnode in self.s_closed:
            eh_right = rnode.hash
            self.s_cost[eh_right] = self.s_cost[node.hash] + self.s_world.w_right
            self.s_f[eh_right] = self.s_cost[eh_right] + self.heuristic(rnode)
            self.s_origin[eh_right] = node
            self.s_open.add(rnode)

        unode = node.up(self.s_world)
        if not unode in self.s_closed:
            eh_up = unode.hash
            self.s_cost[eh_up] = self.s_cost[node.hash] + self.s_world.w_up
            self.s_f[eh_up] = self.s_cost[eh_up] + self.heuristic(unode)
            self.s_origin[eh_up] = node
            self.s_open.add(unode)

        dnode = node.down(self.s_world)
        if not dnode in self.s_closed:
            eh_down = dnode.hash
            self.s_cost[eh_down] = self.s_cost[node.hash] + self.s_world.w_down
            self.s_f[eh_down] = self.s_cost[eh_down] + self.heuristic(dnode)
            self.s_origin[eh_down] = node
            self.s_open.add(dnode)

    def select(self):
        cost = "inf"
        chosen = None
        for node in self.s_open:
            if cost > self.s_f[node.hash]:
                cost = self.s_f[node.hash]
                chosen = node

        if chosen == None:
            print "Open set empty, no solution found"
        else:
            print "Node: (", chosen.x, ",", chosen.y, ",", chosen.coffee, ") has been selected from the frontier"

        # check for solution found (assumes only looking for one solution)
        if chosen in self.s_world.w_goal:
            print "Goal found! ", chosen
            self.s_complete = 1
            self.s_goal = chosen
            
        return chosen

    def isComplete(self):
        return self.s_complete

    def print_path(self):
        if self.s_goal == None:
            return
        path = [self.s_goal]
        node = self.s_goal

        print "Total number of nodes expanded = ", (len(self.s_closed) - len(self.s_world.w_blocked))
        print "Final Path: "

        while node not in self.s_world.w_start:
            node = self.s_origin[node.hash]
            path.append(node)
        while len(path) > 0:
            step = path.pop()
            print "( ", step.x, ", ", step.y, " )"

class World:
    def __init__(self, start, coffee, bounds, blocked, goal):
        # the cost of movement in given direction
        self.w_right = 1
        self.w_left  = 1
        self.w_up    = 1
        self.w_down  = 1
        # the locations of coffee
        self.w_coffee = set()
        # define the traversable area
        self.w_bounds = bounds[:]
        # the untraversable nodes
        self.w_blocked = set()
        # the states at which the search may start
        #currently fixed at one
        self.w_start = start[:]
        # the states at which a path has been found
        self.w_goal = goal

        # ensure that coffee states and blocked states
        # account for coffee
        for x in coffee:
            self.w_coffee.add(x)
            self.w_coffee.add(invertCoffee(x))

        for x in blocked:
            self.w_blocked.add(x)
            self.w_blocked.add(invertCoffee(x))

    # moving from a.x -> b.x what is the cost?
    def x_weight(self, a, b):
        if a < b:
            return self.w_right
        else:
            return self.w_left

    # moving from a.y -> b.y what is the cost?
    def y_weight(self, a, b):
        if a < b:
            return self.w_up
        else:
            return self.w_down

class Node:
    def __init__(self, x, y, coffee=0):
        self.x = x
        self.y = y
        self.coffee = coffee
        self.hash = (x << 16) ^ (y << 1) ^ coffee

    def __repr__(self):
        return "( {0}, {1}, {2} )".format(self.x, self.y, self.coffee)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        if self.hash == other.__hash__():
            return True
        else:
            return False

    def left(self, world):
        bounds = world.w_bounds
        dx = self.x - 1 if self.x != bounds[0] else self.x
        new_node = Node(dx, self.y, self.coffee)
        if new_node in world.w_coffee:
            new_node = invertCoffee(new_node)
        return new_node

    def right(self, world):
        bounds = world.w_bounds
        dx = self.x + 1 if self.x != bounds[1] else self.x
        new_node = Node(dx, self.y, self.coffee)
        if new_node in world.w_coffee:
            new_node = invertCoffee(new_node)
        return new_node

    def up(self, world):
        bounds = world.w_bounds
        dy = self.y + 1 if self.y != bounds[3] else self.y
        new_node = Node(self.x, dy, self.coffee)
        if new_node in world.w_coffee:
            new_node = invertCoffee(new_node)
        return new_node

    def down(self, world):
        bounds = world.w_bounds
        dy = self.y - 1 if self.y != bounds[2] else self.y
        new_node = Node(self.x, dy, self.coffee)
        if new_node in world.w_coffee:
            new_node = invertCoffee(new_node)
        return new_node

def invertCoffee(node):
    return Node(node.x, node.y, node.coffee ^ 1)

def Search():

    # define our problem
    start = [Node(3, 2)]
    # the coffee flag is handled, only locations are needed
    coffee = [Node(0, 0), Node(4, 0), Node(8, 4)]
    # the coffee flag is handled, only locations are needed
    blocked = [Node(1, 1), Node(1, 2), \
               Node(1, 3), Node(2, 3), \
               Node(3, 3), Node(4, 3), \
               Node(5, 3), Node(5, 4)]
    bounds = (0, 8, 0, 5) # size of the board (x_min, x_max, y_min, y_max)
    goal = [Node(3, 4, 1)]
    world = World(start, coffee, bounds, blocked, goal)
    a_star = A_star(world)

    while not a_star.isComplete():
        node = a_star.select()
        a_star.expand(node)

    a_star.print_path()

Search()
