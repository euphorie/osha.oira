from euphorie.client import model
from osha.oira.client import model as oiramodel
from sqlalchemy import sql
from z3c.saconfig import Session


def remove_empty_modules(nodes):
    """Takes a list of modules and risks.

    Removes modules that don't have any risks in them.
    Modules with submodules (with risks) must however be kept.

    How it works:
    -------------
    Use the 'grow' method to create a tree datastructure that
    mirrors the actual layout of modules and risks.

    Then 'prune' it by removing all branches that end in modules.

    Lastly flatten the tree back into a list and use it to filter the
    original list.
    """
    tree = {}
    ids = []

    def grow(tree, nodes):
        for i in range(0, len(nodes)):
            node = nodes[i]
            inserted = False
            keys = list(tree.keys())
            for k in keys:
                if node.path.startswith(k[0]):
                    if tree[k]:
                        grow(tree[k], [node])
                    else:
                        tree[k] = {(node.path, node.type, node.id): {}}
                    inserted = True
                    break
            if not inserted:
                tree[(node.path, node.type, node.id)] = {}

    def prune(tree):
        keys = list(tree.keys())
        for k in keys:
            if tree[k]:
                prune(tree[k])

            if not tree[k] and k[1] == "module":
                del tree[k]

    def flatten(tree):
        keys = list(tree.keys())
        for k in keys:
            ids.append(k[2])
            flatten(tree[k])

    grow(tree, nodes)
    prune(tree)
    flatten(tree)
    return [n for n in nodes if n.id in ids]


def get_actioned_nodes(ls):
    """Takes a list of modules and risks and removes all risks that are *not*
    actioned (i.e does not have at least one valid action plan) Also remove all
    modules that have lost all their risks in the process.

    See https://syslab.com/proj/issues/2885
    """
    actioned = []
    for n in ls:
        if n.type == "module":
            actioned.append(n)

        if n.type == "risk" and len(n.action_plans):
            # It's possible that there is an action plan object, but
            # it's not yet fully populated
            plans = [p.action_plan for p in n.action_plans]
            if plans[0] is not None:
                actioned.append(n)

    return remove_empty_modules(actioned)


def get_unanswered_nodes(session):
    query = (
        Session()
        .query(model.SurveyTreeItem)
        .filter(
            sql.and_(
                model.SurveyTreeItem.session == session,
                sql.or_(
                    oiramodel.MODULE_WITH_UNANSWERED_RISKS_FILTER,
                    oiramodel.UNANSWERED_RISKS_FILTER,
                ),
                sql.not_(model.SKIPPED_PARENTS),
            )
        )
        .order_by(model.SurveyTreeItem.path)
    )
    return query.all()


def get_risk_not_present_nodes(session):
    query = (
        Session()
        .query(model.SurveyTreeItem)
        .filter(
            sql.and_(
                model.SurveyTreeItem.session == session,
                sql.or_(
                    model.SKIPPED_PARENTS,
                    oiramodel.MODULE_WITH_RISKS_NOT_PRESENT_FILTER,
                    oiramodel.RISK_NOT_PRESENT_FILTER,
                    oiramodel.SKIPPED_MODULE,
                ),
            )
        )
        .order_by(model.SurveyTreeItem.path)
    )
    return query.all()
