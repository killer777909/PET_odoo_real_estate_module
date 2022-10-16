from odoo import fields, models

class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Contains property tags"
    _order = "name"
    
    name = fields.Char(string='Tag', required=True)
    color = fields.Integer()
    
    _sql_constraints = [
        ('unique_name_validation', 'UNIQUE (name)', 'A property tag name must be unique.'),
    ]
    