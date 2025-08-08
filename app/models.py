from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Tabla de asociación para User-Role (Many-to-Many)
user_roles = db.Table('UserRole',
    db.Column('idROLE', db.Integer, db.ForeignKey('role_s.iDRole'), primary_key=True),
    db.Column('iD_Useri', db.Integer, db.ForeignKey('users.iD_User'), primary_key=True)
)


class RoleS(db.Model):
    __tablename__ = 'role_s'
    
    iDRole = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TypeRole = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'iDRole': self.iDRole,
            'TypeRole': self.TypeRole
        }

class Users(db.Model):
    __tablename__ = 'users'
    
    iD_User = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserName = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    PasswoRDkey = db.Column(db.String(255), nullable=False)
   
    
    # Relaciones Many-to-Many con Roles
    roles = db.relationship('RoleS', secondary=user_roles, lazy='subquery',
                           backref=db.backref('users', lazy=True))
    
    def set_password(self, password):
        """Hash password"""
        self.PasswoRDkey = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password"""
        return check_password_hash(self.PasswoRDkey, password)
    
    def to_dict(self, include_roles=False):
        data = {
            'iD_User': self.iD_User,
            'UserName': self.UserName,
            'Email': self.Email
        
        }
        
        if include_roles:
            data['roles'] = [role.to_dict() for role in self.roles]
            
        return data