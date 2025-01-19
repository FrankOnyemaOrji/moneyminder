# MoneyMinder - Personal Finance Management System

MoneyMinder is a comprehensive web application developed for Code of Africa GmbH that helps users manage their personal finances effectively. It provides a user-friendly interface for tracking multiple accounts, managing transactions, setting budgets, and generating detailed financial reports.

## Live Demo
🌐 [MoneyMinder Live](https://moneyminder-khus.onrender.com)

## Project Overview Video
🎥 [Watch the Project Demo](https://youtu.be/your-video-link)

## Features

### Account Management
- Support for multiple account types (Bank accounts, Mobile Money, Cash)
- Real-time balance tracking and updates
- Account-specific transaction history
- Currency support for USD and local currencies

### Transaction Tracking
- Easy transaction entry and categorization
- Support for both income and expenses
- Bulk transaction import from CSV/Excel
- Detailed transaction history with filtering options

### Budget Management
- Monthly budget setting by category
- Real-time budget tracking
- Visual budget progress indicators
- Budget alerts and notifications

### Financial Reports
- Comprehensive spending reports
- Income vs. Expenses analysis
- Custom date range selection
- Export to PDF and Excel formats
- Category-wise spending breakdown

### User Interface
- Clean, modern dashboard design
- Mobile-responsive layout
- Intuitive navigation
- Real-time data updates

## Tech Stack

### Backend
- Python 3.8+
- Flask Framework
- SQLAlchemy ORM
- JWT Authentication
- RESTful API Design

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Chart.js for visualizations
- Responsive Design

### Database
- PostgreSQL
- SQLAlchemy (Development)

### Testing & Quality
- pytest for unit testing
- GitHub Actions for CI/CD
- Code coverage reports
- ESLint & Prettier

## Prerequisites

1. Python 3.8+
2. PostgreSQL
3. Git
4. pip (Python package manager)
5. Virtual environment tool (venv)

## Local Development Setup

1. Clone the repository:
   ```bash
   git https://github.com/FrankOnyemaOrji/moneyminder.git
   cd moneyminder
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   flask db upgrade
   ```

6. Run the development server:
   ```bash
   flask run --debug
   ```

The application will be available at `http://localhost:5000`

## Testing

To run the test suite:
```bash
pytest
```

For test coverage report:
```bash
pytest --cov=app tests/
```

## Deployment

The application is deployed on AWS using:
- Render for hosting
- RDS for PostgreSQL database

Detailed deployment instructions are available in the deployment guide.

## Security Features

- Password hashing with bcrypt
- CSRF protection
- XSS prevention
- SQL injection protection
- Rate limiting
- Session management
- Input validation

## Roadmap

- [ ] Mobile app development
- [ ] Multi-currency support
- [ ] Investment tracking
- [ ] Bill reminders
- [ ] Financial goals setting
- [ ] API integration with banks
- [ ] Advanced analytics
- [ ] Expense predictions

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your PR adheres to:
- Code style guidelines
- Test coverage requirements
- Documentation standards

## Support

For support, contact:
- Email: f.orji@alustudent.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Code of Africa GmbH team
- Open source contributors
- Beta testers and early adopters
