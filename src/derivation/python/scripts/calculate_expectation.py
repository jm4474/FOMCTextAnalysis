import pandas as pd
from pandas.tseries.offsets import MonthEnd
def main():
    monthly_data = pd.read_csv("../../../collection/python/output/string_theory_indicators_monthly.csv")
    daily_data = pd.read_csv("../output/daily_policy_data.csv")
    daily_data['FF2_COMDTY'].fillna(method='ffill',inplace=True)
    daily_data['FF1_COMDTY'].fillna(method="ffill",inplace=True)

    monthly_data['month'] = pd.to_datetime(monthly_data['DATE'])
    daily_data['date'] = pd.to_datetime(daily_data['DATE'])
    daily_data['eom'] = daily_data['date']+MonthEnd(0) == daily_data['date']

    end_df = daily_data[(daily_data['eom']==True)].copy()

    end_df['month'] = end_df['date'].dt.month
    end_df['year'] = end_df['date'].dt.year
    end_df['merge_date'] = pd.to_datetime(dict(day=1,month=end_df.month,year=end_df.year))
    end_df['no_meeting_exp'] = 100-end_df['FF2_COMDTY']-daily_data["DFEDTAR"]
    end_df['no_meeting_exp'] = end_df['no_meeting_exp'].shift(1)

    daily_data['target_t-1'] = daily_data['DFEDTAR'].shift(1)
    daily_data['ff1_t-1'] = daily_data['FF1_COMDTY'].shift(1)

    daily_data['year'] = daily_data['date'].dt.year
    daily_data['month'] = daily_data['date'].dt.month
    daily_data['day'] = daily_data['date'].dt.day

    monthly_data['year_val'] = monthly_data['month'].dt.year
    monthly_data['month_val'] = monthly_data['month'].dt.month
    monthly_data['exp'] = None

    daily_data['k_x'] = daily_data['day']
    daily_data['kappa'] = (daily_data['date']+MonthEnd(0)).dt.day
    daily_data['mu'] = (daily_data['k_x'])/daily_data['kappa']
    daily_data['r_diff'] = daily_data['DFF']-daily_data['DFEDTAR']
    daily_data.loc[daily_data['year'] < 1994, 'event_type'] = \
        daily_data[daily_data['year'] < 1994]['event_type'].shift(
            periods=1)

    for year in range(1988,2008):
        for month in range(1,13):

            cur_month = daily_data.loc[(daily_data.year == year)
                                   &(daily_data.month==month)]
            meeting_day = cur_month.loc[cur_month.event_type == "Meeting"]['day']

            print(month,year)
            if not meeting_day.empty:
                meeting_day = meeting_day.iloc[0]
                if meeting_day==1:
                    continue
                u_t_k = cur_month.loc[cur_month['day']<meeting_day,'r_diff'].sum()
                monthly_data.loc[(monthly_data.year_val==year)&
                                 (monthly_data.month_val==month),'u_t_k'] = u_t_k
                print(meeting_day)
                meet_vals = daily_data.loc[(daily_data['day']==(meeting_day-1))
                                               &(daily_data['month']==month)
                                               &(daily_data['year']==year)]

                k_x = meet_vals['k_x']
                kappa = meet_vals['kappa']
                mu = meet_vals['mu']
                #if year < 1994:
                #    k_x+=1
                 #   mu = (k_x-1)/kappa
                sigma=0.3
                u_k_x = meet_vals['r_diff']
                r_o_m_exp = u_k_x*((sigma*(1-(sigma**(kappa-k_x))))/(1-sigma))
                monthly_data.loc[(monthly_data.year_val == year) &
                                 (monthly_data.month_val == month), 'r_o_m_exp'] = r_o_m_exp.values


                v_t_k = (1/kappa)*((u_t_k) + r_o_m_exp)
                monthly_data.loc[(monthly_data.year_val == year) &
                                 (monthly_data.month_val == month), 'v_t_k'] = v_t_k.values
                scaling_factor = 1/(1-mu)
                print('scaling factor:',scaling_factor)
                print('target:',100-meet_vals['FF1_COMDTY']-meet_vals['DFEDTAR'])
                print('mu:',mu)
                s_t = ((scaling_factor*(100-meet_vals['FF1_COMDTY']-meet_vals['DFEDTAR'])) -
                       (scaling_factor*v_t_k)).values
                monthly_data.loc[((monthly_data.year_val == year)
                                 &(monthly_data.month_val == month)),'exp'] = s_t
                #print(monthly_data.loc[((monthly_data.year_val == year)
                                       #& (monthly_data.month_val == month))])
            else:
                value = end_df[(end_df['merge_date']==cur_month.iloc[0].date)]['no_meeting_exp']
                monthly_data.loc[(monthly_data.year_val == year)
                                 & (monthly_data.month_val == month),'exp']\
                = value.values
    #print(monthly_data[(monthly_data['year_val']<=2008)&(monthly_data['year_val']>=1988)])
    monthly_data.to_csv("expectation_monthly.csv")
    daily_data.to_csv("expectation_daily.csv")
                #monthly_data.loc[(monthly_data['month_val']==month)
                #                 &(monthly_data['year_val']==year),'exp'] \
                #    = end_df.loc[(end_df['month']==month)&(end_df['year']==year)]
if __name__ == "__main__":
    main()