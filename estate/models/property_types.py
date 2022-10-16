from odoo import fields, models, api

class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Contains property types"
    _order = "name"
    
    name = fields.Char('Type', required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute='_compute_offers_count')
    sequence = fields.Integer()
    
    _sql_constraints = [
        ('unique_name_validation', 'UNIQUE (name)', 'A property type name must be unique.'),
    ]
    
    @api.depends('offer_ids')
    def _compute_offers_count(self):
        for type in self:
            type.offer_count = len(type.offer_ids)
            
