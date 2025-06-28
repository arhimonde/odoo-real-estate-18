from odoo import fields, models, api

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "sequence, name"

    property_ids = fields.One2many(
        'estate.property',
        'property_type_id',
        string="Properties"
    )

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order property types")
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Property type name must be unique'),
    ]

    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_type_id',
        string="Offers"
    )

    offer_count = fields.Integer(
        string="Offers Count",
        compute='_compute_offer_count',
        store=True
    )

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)