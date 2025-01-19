from app import db
from app.models import BaseModel
from datetime import datetime


class ReportTemplate(db.Model, BaseModel):
    """
    Model for saved report templates
    """
    __tablename__ = 'report_templates'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    filters = db.Column(db.JSON, nullable=False)  # Stores report filter settings
    is_default = db.Column(db.Boolean, default=False)
    last_used = db.Column(db.DateTime)

    # Foreign Keys
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('report_templates', lazy='dynamic'))

    def __init__(self, name, filters, user_id, description=None, is_default=False):
        self.name = name
        self.filters = filters
        self.user_id = user_id
        self.description = description
        self.is_default = is_default

    def __repr__(self):
        return f'<ReportTemplate {self.name}>'

    def to_dict(self):
        """Convert template to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'filters': self.filters,
            'is_default': self.is_default,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used = datetime.utcnow()
        self.save()

    @classmethod
    def get_user_templates(cls, user_id):
        """Get all templates for a user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.name).all()

    @classmethod
    def get_default_template(cls, user_id):
        """Get user's default template if exists"""
        return cls.query.filter_by(user_id=user_id, is_default=True).first()

    def set_as_default(self):
        """Set this template as default for the user"""
        # First, remove default status from any other template
        ReportTemplate.query.filter_by(
            user_id=self.user_id,
            is_default=True
        ).update({'is_default': False})

        # Set this template as default
        self.is_default = True
        self.save()

    def validate_filters(self):
        """Validate filter settings"""
        required_fields = ['start_date', 'end_date', 'accounts', 'categories']
        return all(field in self.filters for field in required_fields)
