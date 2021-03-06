# Quotapi - A Quotation API

![Quotapi Logo](http://quotapi.kleiber.me/assets/quotapi-logo-100.png)

Quotapi is a very simple RESTful (well, almost) quotation API that is based on Flask and SQLite. Quotapi is the result of an educational investigation into Flask and is not really suited for productive use. Quotapi's purpose is to provide (famous) quotations in JSON.										

## Documentation (API v.1.0)
### Searching
/quotapi/api/v1.0/quotes/search/
* Request: POST ['search_term', string]
* Return: JSON "search_results" containing all quotes ("author", "id", "lang", "quote", "timeadded") that include the search term
* Return Failure: 404

### Retrieving a Random Quotation
/quotapi/api/v1.0/quotes/random
* Request: GET
* Return: JSON "quote" containing the "author", "id", "lang", "quote", "timeadded", and "verification_sum"
* Return Failure: 404

### Retrieving a Single Quotation
/quotapi/api/v1.0/quotes/$quote_id
* Request: GET
* Return: JSON "quote" containing the "author", "id", "lang", "quote", "timeadded", and "verification_sum"
* Return Failure: 404

### Validating a Quotation
/quotapi/api/v1.0/quotes/verify/$quote_id
* Request: POST ['verification', int (-1/0/1)]
* Return: 200
* Return Failure: 409, 403, 404

### API Status
/quotapi/api/v1.0/status
* Request: GET
* Return: JSON "status" containing "status: ok" and "number_of_quotes"
* Return Failure: 404

## Quote Verification
The idea behind quote verification is that api users can verify the correctness of a quotation. Each user (= IP) can verifiy each quote in the form of an integer between -1 and 1. Each "1" represents a verification of validity. The total number of verifications is returned together with the quotation in order to evaluate it's quality.