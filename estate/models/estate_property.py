from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Contains property data"
    _order = "id desc"

    name = fields.Char('Title', required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date('Available From', copy=False,
                                    default=fields.Datetime.today() + relativedelta(months=+3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer('Garden Area (sqm)')
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    active = fields.Boolean(default=True)
    state = fields.Selection(string='Status', required=True, copy=False, default='new',
                             selection=[('new', 'New'), ('offer received', 'Offer Received'),
                                        ('offer accepted', 'Offer Accepted'), ('sold', 'Sold'),
                                        ('canceled', 'Canceled')])
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    user_id = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    tag_ids = fields.Many2many('estate.property.tag')
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    total_area = fields.Integer('Total Area (sqm)', compute="_compute_total_area")
    best_price = fields.Float('Best Offer', compute='_compute_best_offer')

    _sql_constraints = [
        ('check_expected_price', 'CHECK (expected_price > 0)', 'A property expected price must be strictly positive.'),
        ('check_selling_price', 'CHECK (selling_price > -1)', 'A property selling price must be positive.'),
    ]

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.living_area + property.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for property in self:
            if property.offer_ids:
                property.best_price = max(property.offer_ids.mapped('price'))
            else:
                property.best_price = 0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    def action_set_property_canceled(self):
        for property in self:
            if property.state == 'sold':
                raise UserError('Sold properties cannot be canceled.')
            else:
                property.state = 'canceled'
        return True

    def action_set_property_sold(self):
        for property in self:
            if property.state == 'canceled':
                raise UserError('Canceled properties cannot be sold.')
            else:
                property.state = 'sold'
        return True

    @api.constrains('selling_price')
    def _selling_price_compare(self):
        for property in self:
            if property.selling_price < property.expected_price / 100 * 90:
                raise ValidationError('The selling price must be at least 90% of the expected price! You \
must reduce the expected price if you want to accept this offer.')

    @api.ondelete(at_uninstall=False)
    def delete_record_state_check(self):
        for property in self:
            if property.state not in ['new', 'canceled']:
                raise UserError('Only new and canceled properties can be deleted.')
