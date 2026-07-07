from income_expenses.views import get_totals
'''
Fetches the economic summary. Income, Expenses, FPA Tax, Income analysis with cash, pos, etc.
YTD result and YTD total's analysis.
for a specific store, a specific timeline. 

Args:
    store: The unique ID (integer) of the store.
    date_from: The start date of the timeline in 'DD-MM-YYYY' format.
    date_to: The end date of the timeline in 'DD-MM-YYYY' format.
'''

# Bridge function with get_totals. Gemini don't recognise Dataframes, and I don't need them.
def ai_assist_totals(store: int, date_from: str, date_to: str):
    sum_income_result, sum_expenses_result, expenses_fpa, income_totals, YTD_result, \
    YTD_totals, income_df, expenses_df, income_result, expenses_result = get_totals(
        store=store,
        date_from=date_from,
        date_to=date_to
)

    return {
            'sum_income': float(sum_income_result),
            'sum_expenses': float(sum_expenses_result),
            'expenses_fpa': float(expenses_fpa),
            'income_totals': {
                'cash': float(income_totals.get('total_cash')),  # maybe needs a ',0' in case it's None?
                'pos': float(income_totals.get('total_pos')),
                'deposit': float(income_totals.get('total_deposit')),
                'check': float(income_totals.get('total_check')),
                'other': float(income_totals.get('total_other'))
            },
            'YTD_result': float(YTD_result),
            'YTD_totals': {
                'cash': float(YTD_totals.get('total_cash')),
                'pos': float(YTD_totals.get('total_pos')),
                'deposit': float(YTD_totals.get('total_deposit')),
                'check': float(YTD_totals.get('total_check')),
                'other': float(YTD_totals.get('total_other'))
            }
            # 'income_result': float(income_result),  # QUERYSET
            # 'expenses_result': float(expenses_result)
    }
    