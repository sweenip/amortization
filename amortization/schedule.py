from typing import Iterator, Tuple

from amortization.amount import calculate_amortization_amount
from amortization.enums import PaymentFrequency


def amortization_schedule(principal: float, interest_rate: float, period: int, 
                          payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY, 
                          actual_payment: float=None, interest_calculation : int=0) -> Iterator[Tuple[int, float, float, float, float]]:
    """
    Generates amortization schedule

    :param principal: Principal amount
    :param interest_rate: Interest rate per year
    :param period: Total number of periods
    :param payment_frequency: Payment frequency per year
    :param actual_payment : actual payment in each period (e.g. if including extra payment towards principal)
    :param interest_calculation : 0 => Microsoft Excel ipmt formula, 1 : Simple Interest formula
    :return: Rows containing period, amount, interest, principal, balance, etc

    Option #0 : msft
    https://answers.microsoft.com/en-us/msoffice/forum/all/what-is-the-equation-that-excel-uses-for-the-ipmt/2b2a7c0d-f39b-4fdc-a713-ba2810b3d166
    Microsoft Excel ipmt formula for monthly payment on a simple loan (fv=0, type =0)

    T : is the length of the loan
    n : is the period in question.
    p : present value
    r : Interest Rate = APR/12 for monthky payment
    a : adjusted intsrest = 1+r 

    ipmt = p*r*(a^(T + 1) - a^n) / (a*(a^T - 1))
    
    Option #1 : simp
    Simple interest formula
    = current balance * r 

    """
    amortization_amount = calculate_amortization_amount(principal, interest_rate, period, payment_frequency)
    if (actual_payment is None):
        payment = amortization_amount
    elif (actual_payment >= amortization_amount):
        payment = actual_payment
    else:
        raise NotImplementedError(f"actual_payment must be None or >= amortization amount, which is currently computed as {amortization_amount:,.0f}")
    
    adjusted_interest = interest_rate / payment_frequency.value

    # p*r*(a^(T + 1) - a^n) / (a*(a^T - 1))  =>  c1*(c2 - a^n)/c3
    a = (1+adjusted_interest)
    c1 = principal * adjusted_interest
    c2 = a**(period+1)
    c3 = a*(a**period - 1)

    balance = principal
    for number in range(1, period + 1):
        if (interest_calculation==0):
            interest = c1*(c2 - a**number)/c3
        elif (interest_calculation==1):
            interest = round(balance * adjusted_interest, 2)
        else:
            raise NotImplementedError(f"Invalid value for interest_calculation")

        if number < period:
            principal = payment - interest
            balance -= principal
        else:
            principal, payment, balance = balance, balance + interest, 0
        yield number, payment, interest, principal, balance
