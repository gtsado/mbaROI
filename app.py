import numpy as np
import numpy_financial as npf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import streamlit.components.v1 as stc 
import copy
import plotly.express as px

st.set_page_config(
    page_title = 'ROI Calc'
    ,page_icon= '💰'
    ,layout='centered'
    ,initial_sidebar_state='auto'
)

html_temp = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@200&family=IBM+Plex+Sans:wght@100;400&display=swap');
        </style>
		<div style="background-color:#FBFBFB;padding:10px;border-radius:10px">
		<p style="color:black;text-align:justify;font-family: 'IBM Plex Mono', monospace;">
        This app was inspired by an <a href="https://www.dollarsandsensela.com/blog/mbacalculator?rq=roi">article</a> I read regarding the actual return on investment of a MBA Degree. There are two functionalities that I wanted to allow users to customize.
        </p>
		</div>
		"""

#@st.cache(suppress_st_warning=True)
def load_data():
    raw = pd.read_excel('Top 15 Business School Data.xlsx', sheet_name='By Industry - Median')
    return raw

#@st.cache(suppress_st_warning = True)
def take_home_pay(salary):
    fica_tax = 0
    fed_tax = 0 

    if salary <= 137700:
        fica_tax += salary * .0765
    else:
        fica_tax += salary * .0145 + .062*(137700)

    tax_bracket = [0,9875, 40125, 85525, 163300, 207350,518400, 100000000]
    tax_rates = [.10, .12,.22,.24, .32, .35, .37]
    tax_owed = [0, 987.50, 4617.50, 14605.50, 32271.50, 47367.50, 156235]
    standard_deduction = 12400
    retirement_percentage = .08
    
    taxable_salary = salary - standard_deduction - salary*(retirement_percentage)
    
    for i, (rate, bottom, top) in enumerate(zip(tax_rates, tax_bracket, tax_bracket[1:])):
        if taxable_salary < bottom : continue
        #print(rate, bottom, top, i)
        fed_tax = tax_owed[i] + rate*(taxable_salary - tax_bracket[i])
    salary = salary - fed_tax - fica_tax
    return salary

#@st.cache(suppress_st_warning = True)
def forecast(pre_mba_salary,post_mba_salary ,start_year):
    pre_tax_salaries_pre_mba = [pre_mba_salary]
    iter_pre_tax_salary_pre_mba = pre_mba_salary
    
    post_tax_salaries_pre_mba = [take_home_pay(pre_mba_salary)]
    iter_post_tax_salary_pre_mba = take_home_pay(pre_mba_salary)
    
    pre_tax_salaries_post_mba = [post_mba_salary]
    iter_pre_tax_salary_post_mba = post_mba_salary
    
    post_tax_salaries_post_mba = [take_home_pay(post_mba_salary)]
    iter_post_tax_salary_post_mba = take_home_pay(post_mba_salary)
    
    index = list(range(start_year, start_year+41))
    
    for i in range(1,len(index)):
        iter_pre_tax_salary_pre_mba *= (1+.03)
        pre_tax_salaries_pre_mba.append(iter_pre_tax_salary_pre_mba)
        
        iter_post_tax_salary_pre_mba *= (1+.03)
        post_tax_salaries_pre_mba.append(iter_post_tax_salary_pre_mba)
        
        iter_pre_tax_salary_post_mba *= (1+.03)
        pre_tax_salaries_post_mba.append(iter_pre_tax_salary_post_mba)
        
        iter_post_tax_salary_post_mba *= (1+.03)
        post_tax_salaries_post_mba.append(iter_post_tax_salary_post_mba)
        
    
    df = pd.DataFrame({'Pre MBA Pre-Tax Income': pre_tax_salaries_pre_mba
                      ,'Pre MBA Post-Tax Income': post_tax_salaries_pre_mba
                      ,'Post MBA Pre-Tax Income': pre_tax_salaries_post_mba
                      ,'Post MBA Post-Tax Income': post_tax_salaries_post_mba}, index = index)
        
    return df

#@st.cache(suppress_st_warning = True)
def amoritization(loan_amount, term, rate = .05):
    balance = [loan_amount]
    monthly_payment = [0]
    interest = [0]
    principal = [0]
    index = list(range(term+1))
    for i in range(len(index)-1):
        monthly_payment.append(-npf.pmt(rate/ 12, term,  loan_amount))
        #print(rate/12)
        interest.append((rate/12)*(balance[i]))
        principal.append(monthly_payment[i+1] - interest[i+1])
        balance.append(balance[i]- principal[i+1])
            
    df = pd.DataFrame({'Payment Amount':monthly_payment
                      ,'Interest': interest
                      ,'Principal': principal
                      ,'Balance': balance}, index=index)
    return df


def main():
    menu = ['Main']
    
    choice = st.sidebar.selectbox('Menu', menu)
    st.title('MBA ROI Calculator 💰')
    if choice == 'Main':
        st.write('*Are you considering an MBA to further your career? Use this app to help gauge your return on investment.*')
        #stc.html(html_temp)
        with st.beta_expander('Background/ Methodology'):
            st.write("""
                #### Motivation
            This app was inspired by an [article](https://www.dollarsandsensela.com/blog/mbacalculator?rq=roi) I read regarding the actual return on investment of a MBA Degree. 
                In the article, the author describes a method of calculating the break even point of a MBA degree using the following inputs:

                - Take home pay of current job
                - MBA summer internship salary
                - Post MBA salary and signing bonus
                - Student loan interest & repayment rate
            #### My Addtions
            I thought that this was a really sound way to look at the ROI of a MBA but that there were opportunities to make the calculator more flexible.
            
                1. Many people enter go to business school considering multiple industries. Industries do not pay the same so it would be important
                2. The cost of attending each school is different and the average/median salaries of each school is different as well
            
            To get started, enter values for the below!
            """)
        
        st.text('\n')
        mba = copy.deepcopy(load_data())

        #mba.columns = map(str.lower, mba.columns)
        #mba.columns = mba.columns.str.replace(' ', '_')

        col1, col2 = st.beta_columns(2)

        with col1:
            start_year = st.number_input('Intended MBA Start Year', min_value= pd.datetime.now().year)
            #school_years = st.number_input('Intended Number of Years in School', min_value= 1, value = 2)
            pre_mba_salary = st.number_input('Pre MBA Salary', value = 85000, step = 1000)
            scholarship_amount = st.number_input('Two Year Scholarship Amount', value = 74000, step = 1000)
            savings_amount = st.number_input('Amount You Can Pay w/ Savings', value = 30000, step = 1000)
            # Bonuses are not guaranteed so we don't include them
        with col2:
            b_school = st.selectbox(
                'Select Business School(s)',
                list(mba['School'].unique()))
            industry = st.selectbox('Select an Industry', ['Consulting', 'Consumer Products', 'Energy', 'Finance', 'Government'
                                                        	,'Manufacturing', 'NonProfit', 'Healthcare', 'Real Estate', 'Technology'
                                                            , 'Media/Entertainment', 'FinTech'])
            loan_interest = st.number_input('Loan Interest Rate', min_value = 1.0, value = 5.0, step = .1)
            loan_interest_rate = loan_interest/100
            payoff_time_years = st.select_slider('Intended Payoff Time (Years)', options = range(21), value = 10)
            payoff_time = payoff_time_years*12
            #loan_interest_rate = st.select_slider('Loan Interest Rate', options = list(np.arange(0.0, 20.99999999999, .1)))
        if st.button('Submit'):
            if not b_school:
                st.warning('Please enter at least one business school to continue.')
            else:
                with st.beta_expander('Analysis'):
                    for column in mba.columns[1:-1]:
                        mba[column] = mba[column].fillna(mba[column].mean())
                    school = mba.loc[mba['School'] == b_school]
                    school['Loan Amount'] = school['Estimated 2Y Cost'] - scholarship_amount - savings_amount

                    school = school.squeeze()

                    #st.write(school)

                    dataframe = forecast(pre_mba_salary, school[industry], start_year)
                    dataframe.index.name = 'Year'

                    loans = amoritization(school['Loan Amount'], payoff_time, loan_interest_rate )

                    dataframe['Out of Pocket Cost'] = 0
                    dataframe.iloc[2, -1] = -school['Loan Amount']
                    dataframe['Loan Interest'] = 0
                    dataframe.iloc[2, -1] = -sum(loans['Interest'])

                    dataframe.iloc[0, 2] = (pre_mba_salary/ 12)*8
                    dataframe.iloc[0, 3] = take_home_pay((pre_mba_salary/ 12)*8)

                    dataframe.iloc[1, 2] = school['Internship Median Monthly Salary']*3
                    dataframe.iloc[1, 3] = take_home_pay(school['Internship Median Monthly Salary']*3)

                    dataframe.iloc[2, 2] = (school[industry]/ 12)*6 + school['School Median Signing Bonus']
                    dataframe.iloc[2, 3] = take_home_pay((school[industry]/ 12)*6 + school['School Median Signing Bonus'])

                    dataframe['Post MBA Pre-Tax Income'] = dataframe['Post MBA Pre-Tax Income'] + dataframe['Out of Pocket Cost'] + dataframe['Loan Interest']
                    dataframe['Post MBA Post-Tax Income']= dataframe['Post MBA Post-Tax Income'] + dataframe['Out of Pocket Cost'] + dataframe['Loan Interest']

                    dataframe['Pre MBA Lifetime Earnings'] = dataframe['Pre MBA Post-Tax Income'].cumsum()
                    dataframe['Post MBA Lifetime Earnings'] = dataframe['Post MBA Post-Tax Income'].cumsum()

                    dataframe['Break-Even Point'] = dataframe['Post MBA Lifetime Earnings'] - dataframe['Pre MBA Lifetime Earnings']

                    break_even_point = 0
                    for i,data in dataframe['Break-Even Point'].iteritems():
                        if data >= 0:
                            break_even_point = i
                            break


                    st.write(f""" {b_school} has two year estimated cost of **${school['Estimated 2Y Cost']:,.2f}**. Given a scholarship of ${scholarship_amount:,.2f} and assuming all of your savings
                    of ${savings_amount:,.2f} goes towards this, you will have to take out loans of **${school['Loan Amount']:,.2f}** to cover the remaining cost.
                    """)

                    st.write(f"""Over the course of {payoff_time_years} years, you will end up paying a total interest of ${sum(loans['Interest']):,.2f} on this loan.""")

                    st.write(f""" The median salary for someone who goes into {industry} from {b_school} is ${school[industry]:,.2f}, the median sign-on bonus is ${school['School Median Signing Bonus']:,.2f},
                    and the median three-month internship at {b_school} pays ${school['Internship Median Monthly Salary']*3:,.2f}""")

                    st.write(f'''
                                You can view the full-time employment report for {b_school} by clicking this [link]({school['Link']})
                    ''')

                    dataframe.reset_index(inplace = True)

                    fig = px.line(dataframe, x='Year', y=['Pre MBA Lifetime Earnings', 'Post MBA Lifetime Earnings'])
                    fig.add_vline(x=break_even_point, line_width=3, line_dash="dash", line_color="green", annotation_text=f"Break-Even Year = {break_even_point}", annotation_font_color="green")
                    fig.update_layout(#title='LifeTime Earnings Pre & Post MBA',
                                        xaxis_title='Year',
                                        yaxis_title='Lifetime Earnings ($$$)')
                    
                    st.write(f'''### You can expect to break even in {break_even_point} which is **{break_even_point - start_year - 2} years** after you finish from {b_school} ''')

                    st.plotly_chart(fig)

                    st.write(dataframe)

                    loans.index.name = 'Month'

                    loans.reset_index(inplace= True)

                    st.write(loans)      


if __name__ == '__main__':
    main()