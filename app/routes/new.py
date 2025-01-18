# # @accounts.route('/<account_id>/edit', methods=['GET', 'POST'])
# # @login_required
# # def edit(account_id):
# #     """Edit an existing account"""
# #     account = Account.query.filter_by(
# #         id=account_id,
# #         user_id=current_user.id
# #     ).first_or_404()
# #
# #     form = AccountEditForm(obj=account)
# #     form.current_balance.data = account.balance
# #
# #     if form.validate_on_submit():
# #         account.name = form.name.data
# #         account.account_type = form.account_type.data
# #         account.currency = form.currency.data
# #         account.description = form.description.data
# #
# #         try:
# #             account.update()
# #             flash('Account updated successfully!', 'success')
# #             return redirect(url_for('accounts.index'))
# #         except Exception as e:
# #             flash('An error occurred while updating the account.', 'error')
# #             return redirect(url_for('accounts.edit', account_id=account_id))
# #
# #     return render_template('accounts/edit.html', form=form, account=account)
# #
# #
# #
# # @accounts.route('/<account_id>/delete', methods=['GET', 'POST'])
# # @login_required
# # def delete(account_id):
# #     account = Account.query.filter_by(
# #         id=account_id,
# #         user_id=current_user.id
# #     ).first_or_404()
# #
# #     form = AccountDeleteForm()
# #
# #     if form.validate_on_submit():
# #         if account.balance == 0:
# #             try:
# #                 Transaction.query.filter_by(account_id=account.id).delete()
# #                 db.session.delete(account)
# #                 db.session.commit()
# #
# #                 if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
# #                     return jsonify({'success': True})
# #
# #                 flash('Account deleted successfully!', 'success')
# #                 return redirect(url_for('accounts.index'))
# #             except Exception as e:
# #                 db.session.rollback()
# #                 if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
# #                     return jsonify({
# #                         'success': False,
# #                         'message': 'Error deleting account'
# #                     }), 400
# #                 flash('Error deleting account.', 'error')
# #         else:
# #             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
# #                 return jsonify({
# #                     'success': False,
# #                     'message': 'Cannot delete account with non-zero balance'
# #                 }), 400
# #             flash('Cannot delete account with non-zero balance.', 'error')
# #
# #     return render_template('accounts/delete.html', form=form, account=account)
#
# @accounts.route('/<account_id>')
# @login_required
# def view(account_id):
#     """View account details and transaction history"""
#     account = Account.query.filter_by(
#         id=account_id,
#         user_id=current_user.id
#     ).first_or_404()
#
#     # Get date range from query parameters or default to last 30 days
#     end_date = datetime.utcnow()
#     start_date = request.args.get('start_date',
#                                   (end_date - timedelta(days=30)).strftime('%Y-%m-%d'))
#     end_date = request.args.get('end_date', end_date.strftime('%Y-%m-%d'))
#
#     # Convert string dates to datetime
#     start_date = datetime.strptime(start_date, '%Y-%m-%d')
#     end_date = datetime.strptime(end_date, '%Y-%m-%d')
#
#     # Get transactions for the date range
#     transactions = Transaction.query.filter(
#         Transaction.account_id == account_id,
#         Transaction.user_id == current_user.id,
#         Transaction.date >= start_date,
#         Transaction.date <= end_date
#     ).order_by(Transaction.date.desc()).all()
#
#     # Calculate statistics
#     total_income = sum(float(t.amount) for t in transactions if t.transaction_type == 'income')
#     total_expenses = sum(float(t.amount) for t in transactions if t.transaction_type == 'expense')
#
#     return render_template('accounts/view.html',
#                            account=account,
#                            transactions=transactions,
#                            total_income=total_income,
#                            total_expenses=total_expenses,
#                            start_date=start_date,
#                            end_date=end_date)