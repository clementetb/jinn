import numpy as np
import random

from helpers import cartesian

from genius_template_importer import import_template
from helpers import is_pareto_efficient


class UtilitySpace():

    def __init__(self, template, resolution=0.05):
        self.utility_space = generate_bids_agent(template['objectives'], resolution)
        self.discount = template['discount']

    def get_offers(self, minut=0, maxut=1):
        # Filtro por los valores de min/max y se coge random
        NotImplementedError


    def get_random(self, minut=0, maxut=1):
        print('Limits', minut, maxut)
        lower = np.ma.masked_less_equal(self.utility_space[:,-1], maxut).mask
        upper = np.ma.masked_greater_equal(self.utility_space[:,-1], minut).mask
        #(all_mask = [i for i, x in enumerate(range(len(lower))) if (lower[i] and upper[i])]
        mask = (lower == True) & (upper == True)
        valids = np.where(mask == True)[0]

        print('valids.size', valids.size)
        if valids.size == 0:
            return None

        index = random.choice(np.arange(valids.size))

        return Bid(self.utility_space[valids[index]], self.discount, valids[index])

    def get_by_index(self, index):
        return Bid(self.utility_space[index], self.discount, index)
    
    def get_utility(self):
        return self.utility_space[:-1]


class Bid():
    INSTANCES = 1

    def __init__(self, values, discount=1, us_index=None, domain=None):
        self.domain = domain
        self.values = values
        self.discount = discount
        self.index = us_index
        self.id = Bid.INSTANCES
        Bid.INSTANCES += 1

    def get_value(self, index):
        return self.values[index]


def get_discrete_issue_function(issue):
    names = []
    values = []
    for i, item in enumerate(issue['items']):
        names.append(i)
        values.append(item['evaluation'])

    names = np.array(names)
    values = np.array(values)

    values = values / values.max()

    return names, values


def get_real_issue_function(issue, resolution):
    upperbound = float(issue['upperbound'])
    lowerbound = float(issue['lowerbound'])
    constant = float(issue['constant'])
    slope = float(issue['slope'])

    step = (upperbound - lowerbound)*resolution

    steps = np.arange(lowerbound, upperbound+step, step)
    values = steps * slope + constant

    return steps, values


def get_issue_function(issue, resolution):
    values = None
    steps = None

    weight = issue['weight']

    if issue['type'].lower() == 'discrete':
        steps, values = get_discrete_issue_function(issue)
    elif issue['type'].lower() == 'real':
        steps, values = get_real_issue_function(issue, resolution)
    else:
        raise NotImplemented('Issue function not implemented')

    return steps, values * weight


def get_utility_function(template, resolution):
    asteps = []
    avalues = []

    for objective in template:
        for issue in objective:
            steps, values = get_issue_function(issue, resolution)

            asteps.append(steps)
            avalues.append(values)

    return asteps, avalues


def generate_bids_agent( template, resolution):
    s1, v1 = get_utility_function(template, resolution)

    bids_values = cartesian(s1).transpose()
    bids_values1 = cartesian(v1)

    u1 = np.sum(bids_values1, axis=1)

    return np.vstack([bids_values, u1]).transpose()


def generate_bids(template1, template2, resolution):
    s1, v1 = get_utility_function(template1, resolution)
    s2, v2 = get_utility_function(template2, resolution)

    bids_values = cartesian(s1).transpose()
    bids_values1 = cartesian(v1)
    bids_values2 = cartesian(v2)

    u1 = np.sum(bids_values1, axis=1)
    u2 = np.sum(bids_values2, axis=1)

    return np.vstack([bids_values, u1, u2]).transpose()
