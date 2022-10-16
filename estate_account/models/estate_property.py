from odoo import models, Command

class InheritedEstateProperty(models.Model):
    _inherit = "estate.property"

    def action_set_property_sold(self):
        
        invoice_values = {
            'partner_id': self.partner_id,
            'move_type': 'out_invoice',
            'journal_id': self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal().id,
            'invoice_line_ids': [
                Command.create({
                    'name': '6% of the selling price',
                    'quantity': 1,
                    'price_unit': self.selling_price/100*6,
                }),
                Command.create({
                    'name': 'an additional 100.00 from administrative fees',
                    'quantity': 1,
                    'price_unit': 100.00,
                }),
            ],
        }
        self.env['account.move'].create(invoice_values)
        return super().action_set_property_sold()