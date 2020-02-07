from xml.dom import minidom


def parse_item(item):
    dict_item = {
        'index': item.attributes['index'].value,
        'value': item.attributes['value'].value,
        'evaluation': float(item.attributes['evaluation'].value),
        'cost': 0
    }

    if 'cost' in item.attributes:
        dict_item['cost']: float(item.attributes['cost'].value)

    return dict_item


def parse_discrete_issue(issue, weights):
    index = issue.attributes['index'].value
    items = []

    for item in [i for i in issue.getElementsByTagName('item') if i in issue.childNodes]:
        items.append(parse_item(item))

    dict_issue = {
        'index': index,
        'name': issue.attributes['name'].value,
        'weight': float(weights[index]),
        'items': items,
        'type': 'discrete'
    }

    return dict_issue


def parse_real_issue(issue, weights):
    index = issue.attributes['index'].value
    my_range = issue.getElementsByTagName('range')[0]
    evaluator = issue.getElementsByTagName('evaluator')[0]

    dict_issue = {
        'index': index,
        'name': issue.attributes['name'].value,
        'weight': float(weights[index]),
        'upperbound': float(my_range.attributes['upperbound'].value),
        'lowerbound': float(my_range.attributes['lowerbound'].value),
        'constant': float(evaluator.attributes['parameter0'].value),
        'slope': float(evaluator.attributes['parameter1'].value),
        'type': 'real'
    }

    return dict_issue


def parse_integer_issue(issue, weights):
    index = issue.attributes['index'].value
    dict_issue = {
        'index': index,
        'name': issue.attributes['name'].value,
        'weight': float(weights[index]),
        'type': 'integer'
    }

    return dict_issue


def parse_issue(issue, weights):
    issue_type = None

    if 'type' in issue.attributes:
        issue_type = issue.attributes['type'].value

    if 'etype' in issue.attributes:
        issue_type = issue.attributes['etype'].value

    if issue_type == "discrete":
        return parse_discrete_issue(issue, weights)
    elif issue_type == "real":
        return parse_real_issue(issue, weights)
    elif issue_type == "integer":
        return parse_integer_issue(issue, weights)
    else:
        raise NotImplementedError

    return dict_issue


def parse_objective(objective):
    weights = {}
    for weight in objective.getElementsByTagName('weight'):
        index = weight.attributes['index'].value
        value = weight.attributes['value'].value

        weights[index] = value

    issues = []
    for issue in objective.getElementsByTagName('issue'):
        issues.append(parse_issue(issue, weights))

    return issues


def import_template(filename):
    doc = minidom.parse(filename)

    utility_space = doc.getElementsByTagName('utility_space')[0]

    objectives = []
    for objective in utility_space.getElementsByTagName('objective'):
        objectives.append(parse_objective(objective))

    return objectives
