# from sqlalchemy import Integer
# from sqlalchemy import String
# from sqlalchemy.sql.expression import cast

    # query_by_path = session.query(SurveyTreeItem).filter(and_(SurveyTreeItem.session_id == context.session_id, SurveyTreeItem.path.like(context.path + "%"))).order_by(SurveyTreeItem.path.desc())
    # query_id = session.query(model.SurveyTreeItem).filter(and_(model.SurveyTreeItem.session_id == self.context.session_id,model.SurveyTreeItem.path.like(self.context.path + "%"))).order_by(int(model.SurveyTreeItem.id).desc())
    query_by_zodb_path = session.query(SurveyTreeItem).filter(and_(SurveyTreeItem.session_id == context.session_id, SurveyTreeItem.path.like(context.path + "%"), SurveyTreeItem.type=="risk"))
    # .order_by(cast(func.split_part(model.SurveyTreeItem.zodb_path, '/', 2), Integer))

    #query_by_zodb_path2 = session.query(model.SurveyTreeItem, cast(func.split_part(model.SurveyTreeItem.zodb_path, '/', 2), Integer)).filter(and_(model.SurveyTreeItem.session_id == self.context.session_id, model.SurveyTreeItem.path.like(self.context.path + "%"), model.SurveyTreeItem.type=="risk")).order_by(cast(func.split_part(model.SurveyTreeItem.zodb_path, '/', 2), Integer))

    #query_by_zodb_path.update({model.SurveyTreeItem.path: self.context.path + cast(cast(func.split_part(model.SurveyTreeItem.zodb_path, '/', 2), Integer), String)  }, synchronize_session=False)

    query_by_zodb_path.update({SurveyTreeItem.path: context.path + "xxx" + func.lpad(func.split_part(SurveyTreeItem.zodb_path, '/', 2), 3, "0")  }, synchronize_session=False)

    query_by_zodb_path.update({SurveyTreeItem.path: context.path + func.lpad(func.split_part(SurveyTreeItem.zodb_path, '/', 2), 3, "0")  }, synchronize_session=False)

    #query_by_zodb_path.update({model.SurveyTreeItem.path: model.SurveyTreeItem.path + 'abcd' }, synchronize_session=False)





pp(tuple((x.path, x.zodb_path, x.title) for x in ordered_custom_risks))


pp(tuple((x.path, x.zodb_path, x.title) for x in sql_risks))


select * from tree where session_id=511 and type='risk'
and zodb_path like 'custom-risks/%'

order by path

-- path, zodb_path, title