_applied = False

if not _applied:
    from z3c.form.form import Form

    # Zap the totally useless 'There were some errors' message.
    Form.formErrorsMessage = None
    del Form
    _applied = True
