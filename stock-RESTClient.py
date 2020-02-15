import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
from lib.Stock import *
from flask import Flask, Response
from flask_restful import Resource, Api ,reqparse
from waitress import serve
import json

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('begin_date', type=str, required=True, help='Begin date')
parser.add_argument('end_date', type=str, required=True, help='End date')


class StockDataEP(Resource):
    def get(self, stock_code, stock_index):
        args = parser.parse_args()
        stockdata = StockData(stock_code, args['begin_date'], args['end_date'])
        d = {stock_index: stockdata.GetData(stock_index)}
        df = pd.DataFrame(d)
        out = df.to_json(orient='columns', date_format='iso')
        resp = Response(response=out,
                        status=200,
                        mimetype="application/json")
        return(resp)

api.add_resource(StockDataEP, '/stockdata/<string:stock_code>/<string:stock_index>')

if __name__ == '__main__':
    #for debug
    #app.run(debug=True, port=5000)
    
    #for production
    serve(app, host='0.0.0.0', port=5000)