from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import timedelta, date

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        copy=False
    )
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    
    # Add new fields
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            date_start = offer.create_date or fields.Datetime.now()
            offer.date_deadline = date_start.date() + timedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            date_start = offer.create_date or fields.Datetime.now()
            offer.validity = (offer.date_deadline - date_start.date()).days

    def action_accept(self):
        # Check if another offer is already accepted
        if self.property_id.offer_ids.filtered(lambda o: o.status == 'accepted' and o.id != self.id):
            raise UserError("Another offer has already been accepted.")
        self.status = 'accepted'
        self.property_id.buyer_id = self.partner_id
        self.property_id.selling_price = self.price
        self.property_id.state = 'offer_accepted'
        return True

    def action_refuse(self):
        self.status = 'refused'
        return True

    property_type_id = fields.Many2one(
        'estate.property.type',
        related='property_id.property_type_id',
        store=True,
        string="Property Type"
    )

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'Offer price must be strictly positive'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Get the property record
            property_id = self.env['estate.property'].browse(vals['property_id'])
            
            # Check if there's an existing offer with higher price
            if property_id.offer_ids:
                max_offer = max(property_id.offer_ids.mapped('price'))
                if vals.get('price', 0) <= max_offer:
                    raise UserError(f"The offer must be higher than {max_offer}")
            
            # Set property state to 'offer_received'
            property_id.state = 'offer_received'
        
        return super().create(vals_list)