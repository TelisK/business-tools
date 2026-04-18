import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from datetime import date

def prediction_model(df, days_prediction=15):

    df = df.dropna()
    df['day'] = pd.to_datetime(df['day'])
    df = df.sort_values('day')
    df = df.reset_index()

    df['income_cash'] = df['income_cash'].astype(float)
    df['income_pos'] = df['income_pos'].astype(float)
    df['income_deposit'] = df['income_deposit'].astype(float)
    df['income_check'] = df['income_check'].astype(float)
    df['income_other'] = df['income_other'].astype(float)
    df = df.drop('index', axis=1)
    df['total'] = df['income_cash'] + df['income_pos'] + df['income_deposit'] + df['income_check'] + df['income_other']

    # Date Features
    df['Year'] = df['day'].dt.year
    df['Month'] = df['day'].dt.month
    df['Day'] = df['day'].dt.day
    df['Day_of_week'] = df['day'].dt.dayofweek
    df['Day_of_year'] = df['day'].dt.dayofyear
    df['Weekend'] = (df['Day_of_week'] >= 5).astype(int)

    X = df[['Year', 'Month', 'Day', 'Day_of_week', 'Day_of_year', 'Weekend']]
    y = df['total']


    model = RandomForestRegressor(n_estimators=100, random_state=42) # Use all the data to train
    model.fit(X, y)

    today = date.today()
    future_dates = pd.date_range(start=today + pd.Timedelta(days=1), periods=days_prediction)

    future_df = pd.DataFrame({
        'day': future_dates,
        'Year': future_dates.year,
        'Month': future_dates.month,
        'Day': future_dates.day,
        'Day_of_week': future_dates.dayofweek,
        'Day_of_year': future_dates.day_of_year,
        'Weekend': (future_dates.dayofweek >= 5).astype(int)
    })

    X_future = future_df[['Year', 'Month', 'Day', 'Day_of_week', 'Day_of_year', 'Weekend']]
    predictions = model.predict(X_future)

    result = pd.DataFrame({
        'day': future_dates.strftime('%d/%m/%Y'),
        'predicted_income': predictions.round(2)
    })

    return result.to_dict('records')  # records returns a list of dictionaries