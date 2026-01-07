from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    easytax_code = Column(String(20), nullable=True)  # Mapping to EasyTax categories
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Self-referential relationship for subcategories
    parent = relationship("Category", remote_side=[id], backref="children")
