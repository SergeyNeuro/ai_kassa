# Import telium package
from telium import *

# Open device
my_device = Telium('/dev/ttyACM0', debugging=True, timeout=10, baudrate=115200)

# Construct our payment infos
my_payment = TeliumAsk.new_payment(
    12.5,
    payment_mode='debit',  # other mode: credit or refund.
    target_currency='RUB',
    # wait_for_transaction_to_end=True,  # If you need valid transaction status
    # collect_payment_source_info=True,  # If you need to identify payment source
    # force_bank_verification=False
)

# Send payment infos to device
try:
    if not my_device.ask(my_payment):
        print('Your device just refused your transaction. Try again.')
        exit(1)
except TerminalInitializationFailedException as e:
    print(format(e))
    exit(2)

# Wait for terminal to answer
my_answer = my_device.verify(my_payment)

if my_answer is not None:
    # Convert answered data to dict.
    print(my_answer.dict)

    # > {
    # '_pos_number': '01',
    # '_payment_mode': '1',
    # '_currency_numeric': '978',
    # '_amount': 12.5,
    # '_private': '0000000000',
    # 'has_succeeded': True,
    # 'transaction_id': '0000000000',
    # '_transaction_result': 0,
    # '_repport': '4711690463168807000000000000000000000000000000000000000',
    # '_card_type':
    #  {
    #      '_name': 'VISA',
    #      '_regex': '^4[0-9]{12}(?:[0-9]{3})?$',
    #      '_numbers': '4711690463168807',
    #      '_masked_numbers': 'XXXXXXXXXXXX8807'
    #  }
    # }

if my_answer.has_succeeded:
    print("Your payment has been processed using a {0} card. Id: {1}".format(my_answer.card_type.name,
                                                                             my_answer.card_type.numbers))
else:
    print("Your payment was rejected. Try again if you wish to.")