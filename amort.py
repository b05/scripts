import pandas as pd
from datetime import date
import numpy as np
from collections import OrderedDict
from dateutil.relativedelta import *
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from IPython.core.pylabtools import figsize
plt.style.use('ggplot')
pd.set_option('display.max_columns', None)
pd.set_option("display.max_rows",999)
pd.set_option('expand_frame_repr', False)

def amortize(principal, interest_rate, years, pmt, addl_principal, start_date, annual_payments):

    p = 1
    beg_balance = principal
    end_balance = principal

    while end_balance > 0:

        interest = round(((interest_rate/annual_payments) * beg_balance), 2)

        pmt = min(pmt, beg_balance + interest)
        principal = pmt - interest

        addl_principal = min(addl_principal, beg_balance - principal)
        end_balance = beg_balance - (principal + addl_principal)

        yield OrderedDict([('Month',start_date),
                           ('Period', p),
                           ('Begin Balance', beg_balance),
                           ('Payment', pmt),
                           ('Principal', principal),
                           ('Interest', interest),
                           ('Additional_Payment', addl_principal),
                           ('End Balance', end_balance)])

        p += 1
        start_date += relativedelta(months=1)
        beg_balance = end_balance

def amortization_table(principal, interest_rate, years, addl_principal=0, annual_payments=12, start_date=date.today()):

    payment = -round(np.pmt(interest_rate/annual_payments, years*annual_payments, principal), 2)

    schedule = pd.DataFrame(amortize(principal, interest_rate, years, payment,
                                     addl_principal, start_date, annual_payments))
    schedule = schedule[["Period", "Month", "Begin Balance", "Payment", "Interest",
                         "Principal", "Additional_Payment", "End Balance"]]

    schedule["Month"] = pd.to_datetime(schedule["Month"])

    payoff_date = schedule["Month"].iloc[-1]
    stats = pd.Series([payoff_date, schedule["Period"].count(), interest_rate,
                       years, principal, payment, addl_principal,
                       schedule["Interest"].sum()],
                       index=["Payoff Date", "Num Payments", "Interest Rate", "Years", "Principal",
                             "Payment", "Additional Payment", "Total Interest"])

    return schedule, stats

def make_plot_data(schedule, stats):
    """Create a dataframe with annual interest totals, and a descriptive label"""
    y = schedule.set_index('Month')['Interest'].resample("A").sum().reset_index()
    y["Year"] = y["Month"].dt.year
    y.set_index('Year', inplace=True)
    y.drop('Month', 1, inplace=True)
    label="{} years at {}% with additional payment of ${}".format(stats['Years'], stats['Interest Rate']*100, stats['Additional Payment'])
    return y, label

df, stats = amortization_table(350000, .04, 30, addl_principal=200, start_date=date(2017, 1,1))

#print(stats)
#print(df.head())

schedule1, stats1 = amortization_table(350000, .04, 30, addl_principal=0, start_date=date(2017,1,1))
schedule2, stats2 = amortization_table(350000, .04, 30, addl_principal=250, start_date=date(2017,1,1))
schedule3, stats3 = amortization_table(350000, .04, 30, addl_principal=500, start_date=date(2017,1,1))

#print(pd.DataFrame([stats1, stats2, stats3]))

'''
fig, ax = plt.subplots(1, 1)
schedule1.plot(x='Month', y='End Balance', label="Scenario 1", ax=ax)
schedule2.plot(x='Month', y='End Balance', label="Scenario 2", ax=ax)
schedule3.plot(x='Month', y='End Balance', label="Scenario 3", ax=ax)
fmt = '${x:,.0f}'
tick = mtick.StrMethodFormatter(fmt)
ax.yaxis.set_major_formatter(tick)
plt.title("Pay Off Timelines");
'''

y1, label1 = make_plot_data(schedule1, stats1)
y2, label2 = make_plot_data(schedule2, stats2)
y3, label3 = make_plot_data(schedule3, stats3)

y = pd.concat([y1, y2, y3], axis=1)

figsize(7,5)
fig, ax = plt.subplots(1, 1)
y.plot(kind="bar", ax=ax)
fmt = '${x:,.0f}'
tick = mtick.StrMethodFormatter(fmt)
ax.yaxis.set_major_formatter(tick)
plt.legend([label1, label2, label3], loc=1, prop={'size':10})
plt.title("Interest Payments");

#additional payment plot example
additional_payments = [0, 50, 200, 500]
fig, ax = plt.subplots(1, 1)

for pmt in additional_payments:
    result, _ = amortization_table(350000, .04, 30, addl_principal=pmt, start_date=date(2017,1,1))
    ax.plot(result['Month'], result['End Balance'], label='Addl Payment = ${}'.format(str(pmt)))

fmt = '${x:,.0f}'
tick = mtick.StrMethodFormatter(fmt)
ax.yaxis.set_major_formatter(tick)
plt.title("Pay Off Timelines")
plt.ylabel("Balance")
ax.legend();

#%matplotlib inline
plt.show()
