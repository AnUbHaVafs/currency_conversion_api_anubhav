# importing all required libraries for handling requests and json data
import requests
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


# currency conversion api function
class CurrencyConverter(Resource):
    def post(self):
        try:
            request_data = request.get_json()

            # validation for all data present is not for the conversion needed
            if not request_data or 'toConvert' not in request_data:
                return {'error': 'Invalid JSON data or missing "toConvert" key'}, 400

            to_convert = request_data['toConvert']

            if not isinstance(to_convert, list) or not to_convert:
                return {'error': 'Invalid "toConvert" data or empty list'}, 400
            
            # to store all the conversions values
            conversions = []
            
            # iterating over all the target currencies and making th apis calls for exchange values return
            for item in to_convert:
                amount = item.get('amount')
                from_currency = item.get('from')
                to_currencies = item.get('to')

                if not amount or not from_currency or not to_currencies or not isinstance(to_currencies, list):
                    return {'error': 'Invalid conversion request data'}, 400

                exchange_values = []

                for to_currency_item in to_currencies:
                    # Fetch exchange rates for the source and target currencies
                    response = requests.get(
                        f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{from_currency.lower()}/{to_currency_item.lower()}.json")

                    if response.status_code != 200:
                        return {'error': f'Failed to fetch exchange rates for {from_currency} to {to_currency_item}'}, 400

                    exchange_rates = response.json()

                    if 'rate' in exchange_rates:
                        exchange_rate = exchange_rates['rate']
                        converted_amount = round(amount * exchange_rate, 2)
                        exchange_values.append({'to': to_currency_item, 'value': converted_amount})

                conversions.append({'amount': amount, 'from': from_currency, 'exchangeValues': exchange_values})

            response_data = {'conversions': conversions}
            return jsonify(response_data), 200
        except Exception as e:
            return {'error': str(e)}, 400

api.add_resource(CurrencyConverter, '/convert')

if __name__ == '__main__':
    app.run(port=7850, debug=True)
