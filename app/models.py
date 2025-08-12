from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Tabla de asociación para User-Role (Many-to-Many)
user_roles = db.Table('UserRole',
    db.Column('idROLE', db.Integer, db.ForeignKey('RoleS.iDRole'), primary_key=True),
    db.Column('iD_Useri', db.Integer, db.ForeignKey('users.iD_User'), primary_key=True)
)

# Tabla de asociación para Product-Category (Many-to-Many)
product_categories = db.Table('PRODUC_Category',
    db.Column('id_Category', db.Integer, db.ForeignKey('category.id_Category'), primary_key=True),
    db.Column('id_Product', db.Integer, db.ForeignKey('product.id_Product'), primary_key=True)
)

class Country(db.Model):
    __tablename__ = 'country'
    
    iD_Country = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CountryName = db.Column(db.String(100), nullable=False)
    
    # Relaciones
    states = db.relationship('States', backref='country', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'iD_Country': self.iD_Country,
            'CountryName': self.CountryName
        }

class States(db.Model):
    __tablename__ = 'states'
    
    iD_States = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StatesName = db.Column(db.String(100), nullable=False)
    iD_Country = db.Column(db.Integer, db.ForeignKey('country.iD_Country'), nullable=False)
    
    # Relaciones
    cities = db.relationship('City', backref='state', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'iD_States': self.iD_States,
            'StatesName': self.StatesName,
            'iD_Country': self.iD_Country,
            'country': self.country.CountryName if self.country else None
        }

class City(db.Model):
    __tablename__ = 'city'
    
    iD_City = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CityName = db.Column(db.String(100), nullable=False)
    iD_States = db.Column(db.Integer, db.ForeignKey('states.iD_States'), nullable=False)
    
    # Relaciones
    users = db.relationship('Users', backref='city', lazy=True)
    
    def to_dict(self):
        return {
            'iD_City': self.iD_City,
            'CityName': self.CityName,
            'iD_States': self.iD_States,
            'state': self.state.StatesName if self.state else None,
            'country': self.state.country.CountryName if self.state and self.state.country else None
        }

class RoleS(db.Model):
    __tablename__ = 'RoleS'
    
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
    iD_City = db.Column(db.Integer, db.ForeignKey('city.iD_City'), nullable=True)
    
    # Relaciones Many-to-Many con Roles
    roles = db.relationship('RoleS', secondary=user_roles, lazy='subquery',
                           backref=db.backref('users', lazy=True))
    
    # Relaciones One-to-Many
    sales = db.relationship('Sales', backref='user', lazy=True)
    temporal_sales = db.relationship('TemporalSales', backref='user', lazy=True)
    
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
            'Email': self.Email,
            'iD_City': self.iD_City,
            'city': self.city.to_dict() if self.city else None
        }
        
        if include_roles:
            data['roles'] = [role.to_dict() for role in self.roles]
            
        return data

class Category(db.Model):
    __tablename__ = 'category'
    
    id_Category = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CategoryName = db.Column(db.String(100), nullable=False)
    
    # Relaciones
    images = db.relationship('PRODUC_Image', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id_Category': self.id_Category,
            'CategoryName': self.CategoryName
        }

class Product(db.Model):
    __tablename__ = 'product'
    
    id_Product = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Price = db.Column(db.Float, nullable=False)
    ProductName = db.Column(db.String(200), nullable=False, index=True)
    Stock = db.Column(db.Integer, nullable=False, default=0)
    
    # Relaciones Many-to-Many con Categories
    categories = db.relationship('Category', secondary=product_categories, lazy='subquery',
                                backref=db.backref('products', lazy=True))
    
    # Relaciones One-to-Many
    images = db.relationship('PRODUC_Image', backref='product', lazy=True, cascade='all, delete-orphan')
    sales_details = db.relationship('SalesDetail', backref='product', lazy=True)
    temporal_sales = db.relationship('TemporalSales', backref='product', lazy=True)
    
    def to_dict(self, include_categories=False, include_images=False):
        data = {
            'id_Product': self.id_Product,
            'ProductName': self.ProductName,
            'Price': self.Price,
            'Stock': self.Stock
        }
        
        if include_categories:
            data['categories'] = [cat.to_dict() for cat in self.categories]
            
        if include_images:
            data['images'] = [img.to_dict() for img in self.images]
            
        return data

class PRODUC_Image(db.Model):
    __tablename__ = 'produc_image'
    
    id_image = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_Category = db.Column(db.Integer, db.ForeignKey('category.id_Category'), nullable=True)
    id_Product = db.Column(db.Integer, db.ForeignKey('product.id_Product'), nullable=False)
    pathimage = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    is_main_image = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id_image': self.id_image,
            'id_Category': self.id_Category,
            'id_Product': self.id_Product,
            'pathimage': self.pathimage,
            'alt_text': self.alt_text,
            'is_main_image': bool(self.is_main_image)
        }

class Sales(db.Model):
    __tablename__ = 'sales'
    
    id_Sale = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DescripcionSale = db.Column(db.Text)
    iD_User = db.Column(db.Integer, db.ForeignKey('users.iD_User'), nullable=False, index=True)
    DateCreated = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    details = db.relationship('SalesDetail', backref='sale', lazy=True, cascade='all, delete-orphan')
    temporal_sales = db.relationship('TemporalSales', backref='sale', lazy=True)
    
    def to_dict(self, include_details=False):
        data = {
            'id_Sale': self.id_Sale,
            'DescripcionSale': self.DescripcionSale,
            'iD_User': self.iD_User,
            'DateCreated': self.DateCreated.isoformat() if self.DateCreated else None,
            'user': self.user.UserName if self.user else None
        }
        
        if include_details:
            data['details'] = [detail.to_dict() for detail in self.details]
            data['total'] = sum(detail.ValueSale for detail in self.details)
            
        return data

class TemporalSales(db.Model):
    __tablename__ = 'temporal_sales'
    
    id_TemporalSales = db.Column(db.Integer, primary_key=True, autoincrement=True)
    iD_User = db.Column(db.Integer, db.ForeignKey('users.iD_User'), nullable=False)
    id_Sale = db.Column(db.Integer, db.ForeignKey('sales.id_Sale'), nullable=True)
    id_Product = db.Column(db.Integer, db.ForeignKey('product.id_Product'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    DateAdded = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id_TemporalSales': self.id_TemporalSales,
            'iD_User': self.iD_User,
            'id_Sale': self.id_Sale,
            'id_Product': self.id_Product,
            'quantity': self.quantity,
            'DateAdded': self.DateAdded.isoformat() if self.DateAdded else None,
            'product': self.product.to_dict() if self.product else None,
            'subtotal': self.product.Price * self.quantity if self.product else 0
        }

class SalesDetail(db.Model):
    __tablename__ = 'sales_detail'
    
    id_SalesDetails = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_Product = db.Column(db.Integer, db.ForeignKey('product.id_Product'), nullable=False, index=True)
    id_Sale = db.Column(db.Integer, db.ForeignKey('sales.id_Sale'), nullable=False, index=True)
    id_TemporalSales = db.Column(db.Integer, db.ForeignKey('temporal_sales.id_TemporalSales'), nullable=True)
    DateSales = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Integer, nullable=False)
    ValueSale = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id_SalesDetails': self.id_SalesDetails,
            'id_Product': self.id_Product,
            'id_Sale': self.id_Sale,
            'id_TemporalSales': self.id_TemporalSales,
            'DateSales': self.DateSales.isoformat() if self.DateSales else None,
            'amount': self.amount,
            'ValueSale': self.ValueSale,
            'product': self.product.to_dict() if self.product else None
        }