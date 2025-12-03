from typing import Dict, Any

class BaseModelMixin:
    """
    Mixin class that provides common methods for all database models.
    Handles safe data filtering and creation from dictionaries.
    """
    
    @classmethod
    def get_db_columns(cls):
        """Get all column names that exist in the database table."""
        return {column.name for column in cls.__table__.columns}

    @classmethod
    def filter_db_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter data to only include fields that exist in the database model.
        
        Args:
            data: Dictionary with data (may include extra fields)
            
        Returns:
            Dictionary with only the fields that exist in the database
        """
        db_columns = cls.get_db_columns()
        return {key: value for key, value in data.items() if key in db_columns}

    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]):
        """
        Create a model instance from dictionary data, safely filtering out non-DB fields.
        
        Args:
            data: Dictionary with data (may include fields that don't exist in DB)
            
        Returns:
            Model instance with only valid database fields
        """
        filtered_data = cls.filter_db_data(data)
        return cls(**filtered_data)