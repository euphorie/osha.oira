import htmllib
from five import grok


def html_unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()


def remove_empty_modules(ls):
    """ Takes a list of modules and risks.

        Removes modules that don't have any risks in them.
        Modules with submodules (with risks) must however be kept.
    """
    while ls and ls[-1].type == 'module':
        ls = ls[:-1]

    for i in range(len(ls) - 1, 0, -1):
        if ls[i] is None:
            if ls[i - 1].type == 'module':
                ls[i - 1] = None

        elif ls[i].type == 'module':
            if ls[i - 1].type == 'module' and \
                    ls[i - 1].depth >= ls[i].depth:
                ls[i - 1] = None

    return [m for m in ls if m is not None]


def get_unactioned_nodes(ls):
    """ Takes a list of modules and risks and removes all risks that have been
        actioned (i.e has at least one valid action plan).
        Also remove all modules that have lost all their risks in the process

        See https://syslab.com/proj/issues/2885
    """
    unactioned = []
    for n in ls:
        if n.type == 'module':
            unactioned.append(n)

        elif n.type == 'risk':
            if not n.action_plans:
                unactioned.append(n)
            else:
                # It's possible that there is an action plan object, but
                # that it's not yet fully populated
                if n.action_plans[0] is None or \
                        n.action_plans[0].action_plan is None:
                    unactioned.append(n)

    return remove_empty_modules(unactioned)


def get_actioned_nodes(ls):
    """ Takes a list of modules and risks and removes all risks that are *not*
        actioned (i.e does not have at least one valid action plan)
        Also remove all modules that have lost all their risks in the process.

        See https://syslab.com/proj/issues/2885
    """
    actioned = []
    for n in ls:
        if n.type == 'module':
            actioned.append(n)

        if n.type == 'risk' and len(n.action_plans):
                # It's possible that there is an action plan object, but
                # it's not yet fully populated
                plans = [p.action_plan for p in n.action_plans]
                if plans[0] is not None:
                    actioned.append(n)

    return remove_empty_modules(actioned)
