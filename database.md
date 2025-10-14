# Database

## Account

id
account_number
name
type

## Account Payable

id
company_id
amount

## Account Receivable

id
company_id
amount

## Customer

id
name
nit
date_birth
comercial_activity
email
address

## Invoice

id
date
authorization_number
dte_type
serie
dte_number
company_id
customer_id
currency
amount
state
is_cancelled
cancelled_date
iva
petroleo
turismo_hospedaje
turismo_pasajes
timbre_prensa
bomberos
tasa_municipal
bebidas_alcoholicas

## Journal Entry

id
company_id
invoice_id
debit
credit

## Users

auth_id
email
picture
