from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
from odoo.exceptions import UserError


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Contains property offers"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(copy=False,
                              selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True, ondelete='cascade')
    validity = fields.Integer('Validity (days)', default=7)
    date_deadline = fields.Date('Deadline', compute='_compute_date_deadline', readonly=False,
                                inverse='_inverse_date_deadline')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)

    _sql_constraints = [
        ('check_offer_price', 'CHECK (price > 0)', 'An offer price must be strictly positive.'),
    ]

    @api.depends('validity')
    def _compute_date_deadline(self):
        for offer in self:
            if not offer.create_date:
                offer.date_deadline = fields.Datetime.today() + relativedelta(days=+offer.validity)
            else:
                offer.date_deadline = offer.create_date + relativedelta(days=+offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            offer.validity = (offer.date_deadline - offer.create_date.date()).days

    def action_set_offer_accepted(self):
        for offer in self.property_id.offer_ids:
            if offer.status == 'accepted':
                raise UserError('Only one offer can be accepted for a given property.')
        for offer in self:
            offer.status = 'accepted'
            offer.property_id.selling_price = offer.price
            offer.property_id.partner_id = offer.partner_id
            offer.property_id.state = 'offer accepted'
        return True

    def action_set_offer_refused(self):
        for offer in self:
            offer.status = 'refused'
        return True

    @api.model
    def create(self, vals):
        self.env['estate.property'].browse(vals['property_id']).state = 'offer received'
        best_property_offer_price = self.env['estate.property'].browse(vals['property_id']).best_price
        if vals['price'] < best_property_offer_price:
            raise UserError(f'The offer must be higher than {best_property_offer_price}')
        return super().create(vals)
