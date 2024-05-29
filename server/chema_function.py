from marshmallow import Schema, fields


# Define the LifeStatusSchema
class LifeStatusSchema(Schema):
    id = fields.Int()
    Ns = fields.Str()
    describe = fields.Str()