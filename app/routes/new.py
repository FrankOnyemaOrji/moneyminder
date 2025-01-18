# @accounts.route('/<account_id>/delete', methods=['GET', 'POST'])
# @login_required
# def delete(account_id):
#     """Delete an account"""
#     account = Account.query.filter_by(
#         id=account_id,
#         user_id=current_user.id
#     ).first_or_404()
#
#     form = AccountDeleteForm()
#
#     if form.validate_on_submit():
#         try:
#             account.delete()
#             flash('Account deleted successfully!', 'success')
#             return redirect(url_for('accounts.index'))
#         except Exception as e:
#             flash('An error occurred while deleting the account.', 'error')
#             return redirect(url_for('accounts.delete', account_id=account_id))
#
#     return render_template('accounts/delete.html',
#                            form=form,
#                            account=account)