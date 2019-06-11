import ast
import decimal
import json


class DecimalEncoder(json.JSONEncoder):
    def default(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def decimal_to_dict(raw):
    return ast.literal_eval(DecimalEncoder().encode(raw))
