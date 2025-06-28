from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import timedelta, date

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: date.today() + timedelta(days=90))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Float("Garden Area (sqm)")
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string='Garden Orientation')
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Cancelled')
        ],
        required=True,
        copy=False,
        default='new'
    )
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    salesperson_id = fields.Many2one(
        'res.users', 
        string='Salesperson', 
        default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")
    property_type_id = fields.Many2one(
        'estate.property.type',
        string="Property Type"
    )
    
    # Add the computed field
    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")
    best_offer = fields.Float(
        "Best Offer",
        compute="_compute_best_offer",
        store=True
    )
    
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)
    
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped('price')) if record.offer_ids else 0.0

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for prop in self:
            prop.best_offer = max(prop.offer_ids.mapped('price')) if prop.offer_ids else 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for record in self:
            record.state = 'sold'
        return True

    def action_cancel(self):
        for record in self:
            record.state = 'canceled'
        return True

    def unlink(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError("You can only delete properties that are New or Cancelled.")
        return super().unlink()

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'Expected price must be strictly positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'Selling price must be positive'),
    ]