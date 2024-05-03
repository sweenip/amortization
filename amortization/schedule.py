from typing import Iterator, Tuple

from amortization.amount import calculate_amortization_amount
from amortization.enums import PaymentFrequency


def amortization_schedule(principal: float, interest_rate: float, period: int, 
                          payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY, actual_payment: float=None) -> Iterator[Tuple[int, float, float, float, float]]:
    """
    Generates amortization schedule

    :param principal: Principal amount
    :param interest_rate: Interest rate per year
    :param period: Total number of periods
    :param payment_frequency: Payment frequency per year
    :param actual_payment : actual payment in each period (e.g. if including extra payment towards principal)
    :return: Rows containing period, amount, interest, principal, balance, etc
    """
    amortization_amount = calculate_amortization_amount(principal, interest_rate, period, payment_frequency)
    if (actual_payment is None):
        payment = amortization_amount
    elif (actual_payment >= amortization_amount):
        payment = actual_payment
    else:
        raise NotImplementedError(f"actual_payment must be None or >= amortization amount, which is currently computed as {amortization_amount:,.0f}")
    
    adjusted_interest = interest_rate / payment_frequency.value
    balance = principal
    for number in range(1, period + 1):
        interest = round(balance * adjusted_interest, 2)
        if number < period:
            principal = payment - interest
            balance -= principal
        else:
            principal, payment, balance = balance, balance + interest, 0
        yield number, payment, interest, principal, balance
