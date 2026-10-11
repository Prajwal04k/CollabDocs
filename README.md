# CollabDocs - Collaborative Document Platform API

A Django REST Framework backend for a collaborative document editing platform, similar to Notion or Google Docs. Teams can create workspaces, manage documents with versioning, leave threaded comments, and track all changes via audit logs.

## 🎯 Features

✅ **User Management** - User profiles and authentication with JWT
✅ **Workspaces** - Create and manage team workspaces with role-based access  
✅ **Documents** - Full CRUD with automatic version history tracking
✅ **Threaded Comments** - Reply to comments for document discussions
✅ **Document Versioning** - Automatic version creation on every edit
✅ **Tags** - Organize documents with tags
✅ **Audit Logs** - Complete audit trail of all actions
✅ **Atomic Transactions** - Data integrity with atomic operations
✅ **Request Logging** - Custom middleware for request tracking
✅ **JWT Authentication** - Secure API access with bearer tokens
✅ **PostgreSQL Ready** - Production-ready database integration

## Project Structure

```
collabdocs/
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── README.md
├── collabdocs/          # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── api/                 # Main API app
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── middleware.py
    ├── models.py
    ├── serializers.py
    ├── signals.py
    ├── urls.py
    ├── views.py
    └── tests.py
```

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip

### Setup Instructions

1. Clone the repository
```bash
git clone <repository-url>
cd collabdocs
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your database credentials and settings
```

5. Create database (ensure PostgreSQL is running)
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser
```bash
python manage.py createsuperuser
```

7. Run the development server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Users (2 endpoints)
- `GET /api/users/me/` - Get current user profile
- `GET /api/users/{id}/` - Get user details

### Workspaces (6 endpoints)
- `POST /api/workspaces/` - Create workspace
- `GET /api/workspaces/` - List user's workspaces
- `GET /api/workspaces/{id}/` - Get workspace details
- `PUT /api/workspaces/{id}/` - Update workspace
- `DELETE /api/workspaces/{id}/` - Delete workspace
- `POST /api/workspaces/{id}/invite/` - Add member to workspace

### Documents (7 endpoints)
- `POST /api/documents/` - Create document
- `GET /api/documents/` - List documents (with filtering)
- `GET /api/documents/{id}/` - Get document details
- `PUT /api/documents/{id}/` - Update document
- `DELETE /api/documents/{id}/` - Delete document
- `GET /api/documents/{id}/versions/` - Get document versions
- `POST /api/documents/{id}/tags/` - Assign tags to document

### Comments (2 endpoints)
- `POST /api/comments/` - Create comment
- `GET /api/comments/?document_id=<id>` - Get document comments

### Tags (1 endpoint)
- `GET /api/tags/` - List all tags

### Audit Logs (1 endpoint)
- `GET /api/audit-logs/` - Get audit logs (admin only)

## Models

### Workspace
- `id` (UUID, primary key)
- `name` (CharField)
- `owner` (ForeignKey to User)
- `is_active` (BooleanField, default=True)
- `created_at` (DateTimeField)

### WorkspaceMember
- `id` (UUID, primary key)
- `workspace` (ForeignKey)
- `user` (ForeignKey)
- `role` (TextChoices: admin, member, viewer)
- `created_at` (DateTimeField)
- Unique constraint on (workspace, user)

### Document
- `id` (UUID, primary key)
- `title` (CharField)
- `content` (TextField)
- `status` (TextChoices: draft, published, archived)
- `workspace` (ForeignKey)
- `created_by` (ForeignKey to User)
- `tags` (ManyToManyField to Tag)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### DocumentVersion
- `id` (UUID, primary key)
- `document` (ForeignKey)
- `content` (TextField)
- `version_number` (IntegerField)
- `created_by` (ForeignKey to User)
- `created_at` (DateTimeField)
- Auto-created via signal on Document save

### Comment
- `id` (UUID, primary key)
- `document` (ForeignKey)
- `author` (ForeignKey to User)
- `text` (TextField)
- `parent` (ForeignKey to self, for threaded replies)
- `created_at` (DateTimeField)

### Tag
- `id` (UUID, primary key)
- `name` (CharField, unique)
- `created_at` (DateTimeField)

### AuditLog
- `id` (UUID, primary key)
- `actor` (ForeignKey to User)
- `action` (CharField)
- `model_name` (CharField)
- `object_id` (CharField)
- `timestamp` (DateTimeField)

## Usage Examples

### 1. Get JWT Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Create a Workspace
```bash
curl -X POST http://localhost:8000/api/workspaces/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Workspace"}'
```

### 3. Create a Document
```bash
curl -X POST http://localhost:8000/api/documents/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Document Title",
    "content": "Document content",
    "status": "draft",
    "workspace": "workspace-uuid"
  }'
```

### 4. List Documents with Filtering
```bash
# Filter by title
curl "http://localhost:8000/api/documents/?title=report" \
  -H "Authorization: Bearer <access_token>"

# Filter by status
curl "http://localhost:8000/api/documents/?status=published" \
  -H "Authorization: Bearer <access_token>"

# Filter by workspace
curl "http://localhost:8000/api/documents/?workspace=workspace-uuid" \
  -H "Authorization: Bearer <access_token>"
```

### 5. Add Comment to Document
```bash
curl -X POST http://localhost:8000/api/comments/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "document-uuid",
    "text": "This is a comment"
  }'
```

### 6. Get Document Versions
```bash
curl "http://localhost:8000/api/documents/document-uuid/versions/" \
  -H "Authorization: Bearer <access_token>"
```

## Key Features Implementation

### Atomic Operations
Document create/update operations use database transactions to ensure consistency:
- Document save
- DocumentVersion auto-creation via signal
- AuditLog entry creation

### Query Optimization
- `select_related` for foreign key fields
- `prefetch_related` for reverse relations
- `annotate(Count)` for aggregations
- Filtering with Q objects for complex queries

### Security
- JWT authentication on all endpoints
- Role-based access control
- User-workspace membership validation
- Unique constraints on workspace membership

### Automatic Audit Trail
- Post-save signals automatically create AuditLog entries
- DocumentVersion created on every document change
- Tracks actor, action, model, and timestamp

## Configuration

### Django Settings
- Debug mode: Controlled via DEBUG environment variable
- Database: PostgreSQL with credentials from .env
- Timezone: UTC
- Static files: Collected in `staticfiles/`

### JWT Settings
- Access token lifetime: 1 hour
- Refresh token lifetime: 1 day
- Algorithm: HS256

### Middleware
- Request logging middleware tracks all HTTP requests with response status and duration

## Admin Interface

Access Django admin at `http://localhost:8000/admin/`

Manage:
- Users
- Workspaces
- Documents
- Comments
- Tags
- Audit logs

## Development

### Running Tests
```bash
python manage.py test
```

### Making Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

## Production Deployment

1. Set `DEBUG=False` in .env
2. Update `SECRET_KEY` with a secure value
3. Update `ALLOWED_HOSTS` with your domain
4. Use environment-specific database settings
5. Set up proper logging
6. Use a production WSGI server (gunicorn, uWSGI)
7. Set up static file serving with a reverse proxy (nginx)

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please open an issue in the repository.
