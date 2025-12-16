"""Custom exceptions for storage operations"""


class StorageException(Exception):
    """Base exception for storage operations"""
    pass


class DataCleaningException(StorageException):
    """Exception raised during data cleaning"""
    pass


class ValidationException(StorageException):
    """Exception raised during data validation"""
    pass


class ImageDownloadException(StorageException):
    """Exception raised during image download"""
    pass


class DatabaseException(StorageException):
    """Exception raised during database operations"""
    pass
