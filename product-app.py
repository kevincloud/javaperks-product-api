import requests
import os
import json
import decimal
from flask import Flask
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key, Attr

access_key = os.getenv("AWS_ACCESS_KEY")
secret_key = os.getenv("AWS_SECRET_KEY")
aws_region = os.getenv("AWS_REGION")
aws_token = os.getenv("AWS_SESSION_TOKEN")
tablename = os.getenv("DDB_TABLE_NAME")
connect = os.getenv("LOCALHOST_ONLY")

ipaddr = "0.0.0.0"
if (connect == "true"):
    ipaddr = "127.0.0.1"

app = Flask(__name__)
CORS(app)
ddb = boto3.resource('dynamodb', aws_access_key_id=access_key, aws_secret_access_key=secret_key, aws_session_token=aws_token, region_name=aws_region)

class DecimalEncoder(json.JSONEncoder):
    def default(self, o): # pylint: disable=E0202
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

# @app.route('/checkdb', strict_slashes=False, methods=['GET'])
# def check_db():
#     url = "http://customer-api.service." + aws_region + ".consul:5822/customers/CS100312"
#     response = requests.get(url)

#     return response.content

@app.route('/version', strict_slashes=False, methods=['GET'])
def get_version():
    return "{ \"api\": \"product-api\", \"version\": \"1.1.6\" }"

@app.route('/all', strict_slashes=False, methods=['GET'])
def get_all():
    table = ddb.Table(tablename)

    response = table.scan(
        Select='ALL_ATTRIBUTES',
        Limit=20
    )

    output = []
    for i in response['Items']:
        output.append(i)

    return json.dumps(output, cls=DecimalEncoder)

@app.route('/detail/<product_id>', strict_slashes=False, methods=['GET'])
def product_info(product_id):
    table = ddb.Table(tablename)
    response = table.query(
        KeyConditionExpression=Key('ProductId').eq(product_id)
    )

    output = []
    for i in response['Items']:
        output.append(i)

    return json.dumps(output, cls=DecimalEncoder)

@app.route('/category/<category>', strict_slashes=False, methods=['GET'])
def category_info(category):
    table = ddb.Table(tablename)
    response = table.scan()
    found = False
    ncat = category.replace("-", " ")

    output = []
    items = response['Items']
    while True:
        for i in items:
            cats = json.loads(i['Categories'])
            try:
                x = cats.index(ncat)
                output.append(i)
            except:
                found = False

        if response.get('LastEvaluatedKey'):
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items = response['Items']
        else:
            break

    return json.dumps(output, cls=DecimalEncoder)

@app.route('/category', strict_slashes=False, methods=['GET'])
def all_categories():
    table = ddb.Table(tablename)
    response = table.scan()

    categories = []
    items = response['Items']
    while True:
        for i in items:
            cats = json.loads(i['Categories'])
            for c in cats:
                try:
                    x = categories.index(c)
                except:
                    categories.append(c)

        if response.get('LastEvaluatedKey'):
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items = response['Items']
        else:
            break

    categories.sort()

    return json.dumps(categories, cls=DecimalEncoder)

@app.route('/image/<product_id>', strict_slashes=False, methods=['GET'])
def product_image(product_id):
    table = ddb.Table(tablename)
    response = table.query(
        KeyConditionExpression=Key('ProductId').eq(product_id)
    )
    
    image_name = ""
    for i in response['Items']:
        image_name = i["Image"]
    
    return image_name

if __name__=='__main__':
    app.run(host=ipaddr, debug=True, port=5821)

