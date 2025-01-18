class Category:
    """
    Category class for managing preset categories and their tags
    Note: This is now a regular class, not a database model
    """

    # Define preset categories with their colors and icons
    PRESET_CATEGORIES = {
        'Shopping': {'color': '#4299E1', 'icon': 'shopping-cart'},
        'Home': {'color': '#48BB78', 'icon': 'home'},
        'Transport': {'color': '#ED8936', 'icon': 'car'},
        'Food': {'color': '#F56565', 'icon': 'utensils'},
        'Healthcare': {'color': '#9F7AEA', 'icon': 'hospital'},
        'Education': {'color': '#667EEA', 'icon': 'graduation-cap'},
        'Entertainment': {'color': '#F687B3', 'icon': 'film'},
        'Gift': {'color': '#ED64A6', 'icon': 'gift'},
        'Travel': {'color': '#4FD1C5', 'icon': 'plane'},
        'Savings': {'color': '#68D391', 'icon': 'piggy-bank'},
        'Salary': {'color': '#4CAF50', 'icon': 'money-bill-wave'},
        'Investment': {'color': '#FFD700', 'icon': 'chart-line'}
    }

    # Tags/subcategories for each category
    CATEGORY_TAGS = {
        'Shopping': {
            'Subcategories': [
                'Clothing', 'Electronics', 'Groceries', 'Accessories', 'Furniture',
                'Gadgets', 'Books', 'Jewelry', 'Cosmetics', 'Sporting Goods'
            ]
        },
        'Home': {
            'Subcategories': [
                'Rent', 'Utilities', 'Repairs', 'Furniture', 'Interior Decoration',
                'Gardening', 'Cleaning Services', 'Home Insurance', 'Smart Home Devices',
                'Pest Control'
            ]
        },
        'Transport': {
            'Subcategories': [
                'Fuel', 'Car Insurance', 'Public Transport', 'Vehicle Maintenance',
                'Taxis/Ride-sharing', 'Parking Fees', 'Car Rentals', 'Road Taxes',
                'Air Travel', 'Vehicle Purchase'
            ]
        },
        'Food': {
            'Subcategories': [
                'Fruits', 'Vegetables', 'Proteins (Chicken, Fish, Beef)', 'Dairy Products',
                'Snacks', 'Beverages', 'Organic Foods', 'Bakery Items', 'Ready-to-Eat Meals',
                'Dining Out'
            ]
        },
        'Healthcare': {
            'Subcategories': [
                'Hospital Visits', 'Medications', 'Health Insurance', 'Dental Care', 'Eye Care',
                'Surgeries', 'Mental Health Services', 'Physical Therapy', 'Wellness Products',
                'Vaccinations'
            ]
        },
        'Education': {
            'Subcategories': [
                'Tuition Fees', 'Books', 'Stationery', 'Online Courses', 'Uniforms',
                'Extracurricular Activities', 'College Applications', 'Test Preparation',
                'Tutoring Services', 'Educational Subscriptions'
            ]
        },
        'Entertainment': {
            'Subcategories': [
                'Movies', 'Concerts', 'Video Games', 'Streaming Services', 'Amusement Parks',
                'Nightlife (Bars, Clubs)', 'Hobbies (Crafting, Collecting)', 'Sports Events',
                'Subscription Boxes', 'Music Equipment'
            ]
        },
        'Gift': {
            'Subcategories': [
                'Birthdays', 'Anniversaries', 'Weddings', 'Festive Seasons', 'Personalized Gifts',
                'Electronics', 'Jewelry', 'Home Décor', 'Gift Cards', 'Flowers and Chocolates'
            ]
        },
        'Travel': {
            'Subcategories': [
                'Airfare', 'Hotels', 'Transportation (Car Rentals, Public Transport)', 'Meals',
                'Tour Packages', 'Sightseeing', 'Travel Insurance', 'Souvenirs', 'Cruise',
                'Visa Applications'
            ]
        },
        'Savings': {
            'Subcategories': [
                'Emergency Fund', 'Retirement Fund', 'High-Interest Savings', 'Recurring Deposits',
                'Fixed Deposits', 'Education Savings', 'Travel Savings', 'House Savings',
                'Insurance-Linked Savings', 'Technology Upgrades Savings'
            ]
        },
        'Salary': {
            'Subcategories': [
                'Base Pay', 'Bonuses', 'Overtime', 'Allowances (Housing, Travel)', 'Gratuity',
                'Commission', 'Severance', 'Perks (Health Benefits, Gym)', 'Stock Options',
                'Profit Sharing'
            ]
        },
        'Investment': {
            'Subcategories': [
                'Stocks', 'Bonds', 'Real Estate', 'Mutual Funds', 'Cryptocurrency',
                'Commodities (Gold, Silver)', 'Startups', 'ETFs (Exchange-Traded Funds)',
                'Art and Collectibles', 'Fixed Income Plans'
            ]
        }
    }

    @classmethod
    def get_all_categories(cls):
        """Get all preset categories with their details"""
        return {
            name: {
                'color': details['color'],
                'icon': details['icon'],
                'tags': cls.CATEGORY_TAGS[name]['Subcategories']
            }
            for name, details in cls.PRESET_CATEGORIES.items()
        }

    @classmethod
    def get_category_details(cls, category_name):
        """Get details for a specific category"""
        category = cls.PRESET_CATEGORIES.get(category_name, {})
        tags = cls.CATEGORY_TAGS.get(category_name, {}).get('Subcategories', [])

        return {
            'name': category_name,
            'color': category.get('color'),
            'icon': category.get('icon'),
            'tags': tags
        }

    @classmethod
    def get_tags_for_category(cls, category_name):
        """Get tags/subcategories for a given category"""
        return cls.CATEGORY_TAGS.get(category_name, {}).get('Subcategories', [])

    @classmethod
    def validate_category(cls, category_name):
        """Validate if a category exists"""
        return category_name in cls.PRESET_CATEGORIES

    @classmethod
    def validate_tag(cls, category_name, tag_name):
        """Validate if a tag exists for a category"""
        tags = cls.get_tags_for_category(category_name)
        return tag_name in tags

    @staticmethod
    def get_default_icon():
        """Get default icon for unknown categories"""
        return 'tag'

    @staticmethod
    def get_default_color():
        """Get default color for unknown categories"""
        return '#718096'
