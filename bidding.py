import numpy as np

from helpers import cartesian


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


def generate_bids(template1, template2, resolution):
    s1, v1 = get_utility_function(template1, resolution)
    s2, v2 = get_utility_function(template2, resolution)

    bids_values = cartesian(s1).transpose()
    bids_values1 = cartesian(v1)
    bids_values2 = cartesian(v2)

    u1 = np.sum(bids_values1, axis=1)
    u2 = np.sum(bids_values2, axis=1)

    return np.vstack([bids_values, u1, u2]).transpose()
