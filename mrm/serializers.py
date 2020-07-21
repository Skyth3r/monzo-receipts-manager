from marshmallow import Schema, fields


class SubItemSchema(Schema):
    description = fields.String(required=True)
    amount = fields.Integer(required=True)
    currency = fields.String(required=True, default='GBP')
    quantity = fields.Float(default=1)
    unit = fields.String()
    tax = fields.Integer()


class ItemSchema(SubItemSchema):
    sub_items = fields.List(fields.Nested(SubItemSchema))


class TaxSchema(Schema):
    description = fields.String(required=True)
    amount = fields.Integer(required=True)
    currency = fields.String(required=True, default='GBP')
    tax_number = fields.String()


class PaymentSchema(Schema):
    type = fields.String(required=True)
    amount = fields.Integer(required=True)
    currency = fields.String(required=True, default='GBP')
    last_four = fields.String()
    gift_card_type = fields.String()
    bin = fields.String()
    auth_code = fields.String()
    aid = fields.String()
    mid = fields.String()
    tid = fields.String()


class MerchantSchema(Schema):
    name = fields.String()
    online = fields.Boolean()
    phone = fields.String()
    email = fields.String()
    store_name = fields.String()
    store_address = fields.String()
    store_postcode = fields.String()


class ReceiptSchema(Schema):
    external_id = fields.String(required=True)
    transaction_id = fields.String(required=True)
    total = fields.Integer(required=True)
    currency = fields.String(required=True, default='GBP')
    items = fields.List(fields.Nested(ItemSchema), required=True, missing=[])
    taxes = fields.List(fields.Nested(TaxSchema), missing=[])
    payments = fields.List(fields.Nested(PaymentSchema), missing=[])
    merchant = fields.Nested(MerchantSchema)
