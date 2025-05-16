# Community Mycelium

A Django-based community platform that facilitates user management, meetings, and access control. The project uses modern web technologies including Django REST Framework, PostgreSQL, and Tailwind CSS.

## Features

- **User Management**: Complete user authentication and authorization system
- **Meetings**: Schedule and manage community meetings
- **Access Control (ACL)**: Granular permission management for different user roles
- **Modern UI**: Styled with Tailwind CSS for a responsive and beautiful interface

## Prerequisites

- Podman (for containerization)
- Python 3.x
- Node.js and npm (for frontend assets)

## Local Development Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd CommunityMycelium
   ```

2. **Set up environment variables**

   ```bash
   cp mycelium/.env-example mycelium/.env
   ```

   Edit the `.env` file with your desired configuration.

3. **Create a superuser**

   ```bash
   make createsuperuser
   ```

4. **Create, initialize and start the development environment**

   ```bash
   make scratch
   ```

   This will create the necessary Podman pod and database containers, setup groups, seed the database and build/start the application. For more fine-grain control, check the Makefile.

The application should now be running at `http://localhost:8000`

## Available Make Commands

- `make init` - Initialize the development environment
- `make up` - Start the application
- `make stop` - Stop all containers
- `make clean` - Remove all containers and volumes
- `make migrate` - Run database migrations
- `make createsuperuser` - Create a new superuser
- `make shell` - Open a Django shell
- `make collectstatic` - Collect static files
- `make seed-all` - Seed the database with sample data
- `make scratch` - Build the project from scratch (removes all data)

## Project Structure

```
mycelium/
├── apps/
│   ├── acl/         # Access Control Layer
│   ├── meetings/    # Meeting management
│   ├── users/       # User management
│   └── core/        # Dashboard/Home
├── config/          # Django settings
├── static/          # Static files (CSS, JS)
├── templates/       # HTML templates
└── manage.py        # Django management script
```

## Development

- The project uses Podman for containerization
- PostgreSQL is used as the database
- Django REST Framework for API endpoints
- Tailwind CSS for styling
- JWT authentication for API security

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests
4. Submit a pull request

## License

[TBD]
