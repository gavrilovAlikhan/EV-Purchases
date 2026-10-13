import pandas as pd

class FeatureEngineering:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        
        self.yes_no_columns: list = ["Home_Charging_Possible", "Subsidy_Available"]

    def engineer_features(self) -> pd.DataFrame:
        eng_df = self.df.copy()
        for c in eng_df[self.es_no_columns]:
            eng_df[c] = eng_df[c].str.lower().map({"no": 0, "yes": 1})


        eng_df["Range_Anxiety_Level"] = (
            eng_df["Range_Anxiety_Level"].str.lower().map({"low": 0, "medium": 1, "high": 2})
        )

        eng_df['Total_Charging_Stations'] = eng_df['Charging_Stations_Near_Home'] + eng_df['Charging_Stations_Near_Work'] + eng_df['Home_Charging_Possible']

        # eng_df['Km_Per_Station'] = eng_df['Daily_Commute_km'] / eng_df['Total_Charging_Stations'].replace(0, np.nan)
        # eng_df['No_Charging'] = (eng_df['Total_Charging_Stations'] == 0).astype('int8')

        eng_df['Realistic_Concern'] = eng_df['Environmental_Concern_Level'] - eng_df['Range_Anxiety_Level']
        
        eng_df["Anxiety_Environmental"] = (
        eng_df["Range_Anxiety_Level"].astype(str)
        + "_"
        + eng_df["Environmental_Concern_Level"].astype(str))

        eng_df['Anxiety_Commute_Ratio'] = np.where(
            eng_df['Daily_Commute_km'] == 0,
            0,
            eng_df['Range_Anxiety_Level'] / eng_df['Daily_Commute_km']
        )

        eng_df["High_Income_EV_Potential"] = (eng_df["Annual_Income_USD"] >= 170537.0).astype('int8')
        eng_df['income_per_car'] = eng_df['Annual_Income_USD'] / (eng_df['Number_of_Cars_Owned'] + 1)

        # # The Dead Zone (0% buy rate region)
        # eng_df['is_dead_zone'] = ((eng_df['Annual_Income_USD'] >= 38000.0) & (eng_df['Annual_Income_USD'] <= 42000.0)).astype('int8')

        # Subsidy combinations

        eng_df['subsidy_income'] = eng_df['Annual_Income_USD'] * eng_df['Subsidy_Available']
        eng_df['subsidy_concern'] = eng_df['Environmental_Concern_Level'] * eng_df['Subsidy_Available']
        eng_df['home_charging_subsidy'] = eng_df['Home_Charging_Possible'] * eng_df['Subsidy_Available']

        num_cols = [
            'Age', 'Annual_Income_USD', 'Daily_Commute_km',
            'Number_of_Cars_Owned', 'Charging_Stations_Near_Home',
            'Charging_Stations_Near_Work', 'Environmental_Concern_Level'
        ]

        # Digit Decomposition
        for c in num_cols:
            for k in range(-4, 4):
                eng_df[f'{c}_digit{k}'] = (eng_df[c].fillna(0) // (10.0 ** k) % 10).astype('int8')

        return eng_df