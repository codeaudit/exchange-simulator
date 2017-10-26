#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import json

import exchange_api_interface
import exchange

app = Flask(__name__)
api = Api(app)


exchange_parser = exchange_api_interface.LiquiApiInterface()
exchange_caller = exchange.get_liqui_exchange()


class LiquiTrade(Resource):

    def post(self, method):
        """A 'requests' dictionary is made that has the Post Request received
        in the web service and the appropriate parse """

        post_reqs = {
            "Trade": {
                "params_method": exchange_api_interface.TradeParams,
                "exchange_method": exchange_caller.execute_trade_api},
            "WithdrawCoin": {
                "params_method": exchange_api_interface.WithdrawParams,
                "exchange_method": exchange_caller.withdraw_api},
            "getInfo": {
                "params_method": exchange_api_interface.GetBalanceParams,
                "exchange_method": exchange_caller.get_balances_api}
            # "CancelOrder": {
            #    "params_method": exchange_api_interface.CancelTradeParams}
            #    "exchange_method":exchange_caller.==MISSING_METHOD==},
            # "ActiveOrders": ,
            # "OrderHistory":,
            # "OrderInfo":,
            # "TradeHistory":,

        }

        if "Key" not in request.headers:
            return jsonify({
                "success": 0,
                "error": "Missing 'Key' Header"
            })

        try:
            request_all = json.loads(request.data)
        except json.JSONDecodeError:
            return jsonify({
                "success": 0,
                "error": "Invalid data format in your request"
            })

        request_all["api_key"] = request.headers["key"].lower()
        to_exchange_results = exchange_parser.parse_to_exchange(
            method, request_all)
        if "error" in to_exchange_results:
            return jsonify(to_exchange_results)
        else:
            exchange_params = post_reqs[method]["params_method"](
                **to_exchange_results)
            exchange_caller.before_api(
                request.headers["key"].lower())
            exchange_reply = post_reqs[method]["exchange_method"](
                exchange_params)
            exchange_caller.after_api(
                request.headers["key"].lower())
            exchange_parsed_reply = (exchange_parser.parse_from_exchange(
                method, exchange_reply))
            return jsonify(exchange_parsed_reply)


api.add_resource(LiquiTrade, "/liqui/<method>")


if __name__ == "__main__":
    app.run(port="5002")
