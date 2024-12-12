# What Is This - Object Identification Platform

A full-stack web application that helps users identify unknown objects by leveraging community knowledge and Wikidata integration.

## Tech Stack

### Backend
- **Django 4.2.17**: Python web framework for building the application
- **PostgreSQL**: Primary database for storing application data
- **Redis**: For caching and session management
- **Gunicorn**: WSGI HTTP Server for running Django in production
- **Celery**: For handling background tasks (future implementation)

### Frontend
- **Bootstrap 5**: For responsive UI components and layout
- **jQuery**: For DOM manipulation and AJAX requests
- **Select2**: For enhanced select boxes
- **jQuery UI**: For additional UI components

### Infrastructure
- **Docker & Docker Compose**: For containerization and orchestration
- **Nginx**: Web server and reverse proxy
- **Certbot**: For SSL/TLS certificate management
- **Let's Encrypt**: SSL certificate provider

## Features

### Authentication & User Management
- User registration with email verification
- Custom login/logout functionality
- Profile management with:
  - Profile picture
  - Occupation
  - About me section

### Post Management
- Create posts with:
  - Object name
  - Description
  - Image upload
  - Material specification
  - Size dimensions (length, width, height)
  - Shape description
  - Text and language details
  - Location information
  - Color selection
  - Wikidata tag integration

### Post Features
- Status tracking (open/solved)
- Advanced filtering and search:
  - By name
  - By material
  - By size ranges
  - By shape
  - By color
  - By location
  - By tags
- Image management
- Tag system with Wikidata integration

### Interaction Features
- Commenting system
- Nested replies to comments
- Upvote/downvote system for:
  - Comments
  - Replies
- User dashboard
- Post detail views

## API Endpoints

### Authentication
- `GET/POST /accounts/login/`: User login
- `GET/POST /accounts/logout/`: User logout
- `GET/POST /accounts/register/`: User registration

### Posts
- `GET /`: Home page with post listing
- `GET/POST /create/`: Create new post
- `GET /post/<int:post_id>/`: Post detail view
- `POST /post/<int:post_id>/comment/`: Add comment to post
- `POST /toggle-status/<int:post_id>/`: Toggle post status
- `GET/POST /edit-post/<int:post_id>/`: Edit existing post

### Comments & Replies
- `POST /comment/<int:comment_id>/upvote/`: Upvote comment
- `POST /comment/<int:comment_id>/downvote/`: Downvote comment
- `POST /comment/<int:comment_id>/reply/`: Add reply to comment
- `POST /reply/<int:reply_id>/reply/`: Add nested reply
- `POST /reply/<int:reply_id>/upvote/`: Upvote reply
- `POST /reply/<int:reply_id>/downvote/`: Downvote reply

### Profile & User Management
- `GET/POST /profile/`: User profile management

### Tags & Search
- `GET /fetch-tags/`: Fetch tags from Wikidata
- `GET /search-tags/`: Search existing tags

## Setup & Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Create necessary directories:
```bash
mkdir -p nginx/conf.d certbot/conf certbot/www
```

3. Set up environment variables in `.env` file:
```env
# Example environment variables
POSTGRES_DB=<your_db_name>
POSTGRES_USER=<your_db_user>
POSTGRES_PASSWORD=<your_db_password>
```

4. Start the services:
```bash
docker compose up -d
```

5. Initialize SSL certificates:
```bash
./init-letsencrypt.sh
```

6. Create superuser:
```bash
docker compose exec web python manage.py createsuperuser
```

## Development

### Running in Development Mode
```bash
docker compose -f docker-compose.dev.yml up -d
```

### Running Tests
```bash
docker compose exec web python manage.py test
```

### Collecting Static Files
```bash
docker compose exec web python manage.py collectstatic
```

## Production Deployment

The application is configured for production deployment with:
- SSL/TLS encryption
- Static file serving through Nginx
- Media file handling
- Database backups
- Logging configuration
- Security headers
- Session management

## Security Features

- HTTPS enforcement
- CSRF protection
- XSS protection
- Secure cookie configuration
- Content security headers
- Rate limiting
- SQL injection protection
- File upload validation

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

   
