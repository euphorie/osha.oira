# coding=utf-8
from euphorie.client import model
from five import grok
from osha.oira.client import model as oiramodel
from sqlalchemy import sql
from z3c.saconfig import Session
from zope.i18nmessageid import MessageFactory
import htmllib

pl_message = MessageFactory('plonelocales')
grok.templatedir('templates')


NAME_TO_PHASE = {
    'start': 'preparation',
    'profile': 'preparation',
    'identification': 'identification',
    'customization': 'identification',
    'actionplan': 'actionplan',
    'report': 'report',
    'status': 'status',
    'help': 'help',
    'new-email': 'useraction',
    'account-settings': 'useraction',
    'account-delete': 'useraction',
    'update': 'preparation',
    'disclaimer': 'help',
    'terms-and-conditions': 'help',
}


def html_unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()


def remove_empty_modules(nodes):
    """ Takes a list of modules and risks.

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
            for k in tree.keys():
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
        for k in tree.keys():
            if tree[k]:
                prune(tree[k])

            if not tree[k] and k[1] == 'module':
                del tree[k]

    def flatten(tree):
        for k in tree.keys():
            ids.append(k[2])
            flatten(tree[k])

    grow(tree, nodes)
    prune(tree)
    flatten(tree)
    return [n for n in nodes if n.id in ids]


def get_unactioned_nodes(ls, filter_for_measures=False):
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
                if filter_for_measures:
                    if getattr(n, "existing_measures", None):
                        unactioned.append(n)
                else:
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


def get_unanswered_nodes(session):
    query = Session().query(model.SurveyTreeItem)\
        .filter(
            sql.and_(
                model.SurveyTreeItem.session == session,
                sql.or_(
                    oiramodel.MODULE_WITH_UNANSWERED_RISKS_FILTER,
                    oiramodel.UNANSWERED_RISKS_FILTER),
                sql.not_(model.SKIPPED_PARENTS)))\
        .order_by(model.SurveyTreeItem.path)
    return query.all()


def get_risk_not_present_nodes(session):
    query = Session().query(model.SurveyTreeItem)\
        .filter(
            sql.and_(
                model.SurveyTreeItem.session == session,
                sql.or_(
                    model.SKIPPED_PARENTS,
                    oiramodel.MODULE_WITH_RISKS_NOT_PRESENT_FILTER,
                    oiramodel.RISK_NOT_PRESENT_FILTER,
                    oiramodel.SKIPPED_MODULE,
                )))\
        .order_by(model.SurveyTreeItem.path)
    return query.all()


def get_italian_risk_not_present_nodes(session):
    query = Session().query(model.SurveyTreeItem)\
        .filter(
            sql.and_(
                model.SurveyTreeItem.session == session,
                sql.or_(
                    model.SKIPPED_PARENTS,
                    oiramodel.MODULE_WITH_RISKS_NOT_PRESENT_FILTER,
                    oiramodel.SKIPPED_MODULE,
                    oiramodel.UNANSWERED_RISKS_FILTER,
                )))\
        .order_by(model.SurveyTreeItem.path)
    return query.all()
