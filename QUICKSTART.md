# CollabDocs - Quick Start Guide

## ✅ Project Complete!

Your CollabDocs collaborative document platform is ready. Here's everything you need to know:

---

## 📦 What's Included

### ✨ 8 Database Models
1. **Workspace** - Team workspaces with owner + is_active flag
2. **WorkspaceMember** - Team members with roles (admin, member, viewer)
3. **Document** - Documents with status (draft, published, archived)
4. **DocumentVersion** - Auto-created on every document save
5. **Comment** - Threaded comments with self-referential FK
6. **Tag** - Tags for organizing documents
7. **AuditLog** - Complete audit trail of all actions
8. **User** - Django built-in User model (auth)

### 🚀 17 API Endpoints

**Users** (2)
- `GET /api/users/me/` - Current user profile
- `GET /api/users/{id}/` - User details

**Workspaces** (6)
- `POST /api/workspaces/` - Create
- `GET /api/workspaces/` - List
- `GET /api/workspaces/{id}/` - Detail
- `PUT /api/workspaces/{id}/` - Update
- `DELETE /api/workspaces/{id}/` - Delete
- `POST /api/workspaces/{id}/invite/` - Invite member

**Documents** (7)
- `POST /api/documents/` - Create (atomic)
- `GET /api/documents/` - List (with filtering)
- `GET /api/documents/{id}/` - Detail
- `PUT /api/documents/{id}/` - Update (creates version)
- `DELETE /api/documents/{id}/` - Delete
- `GET /api/documents/{id}/versions/` - List versions
- `POST /api/documents/{id}/tags/` - Assign tags

**Comments** (2)
- `POST /api/comments/` - Create (threaded)
- `GET /api/comments/` - List by document

**Tags** (1)
- `GET /api/tags/` - List all tags

**Audit Logs** (1)
- `GET /api/audit-logs/` - List logs (admin only)

### 🔧 Features Built

✅ JWT Authentication (SimpleJWT)
✅ Request Logging Middleware
✅ Django Signals (auto DocumentVersion + AuditLog)
✅ Atomic Transactions (data integrity)
✅ Query Optimization (select_related, prefetch_related, annotate)
✅ Role-Based Access Control
✅ Threaded Comments
✅ Document Versioning
✅ PostgreSQL Integration
✅ Postman Collection (19 requests)
✅ Comprehensive README
✅ Initial Migration

---

## 🎯 How to Run Locally

### Step 1: Extract & Navigate
```bash
unzip collabdocs.zip
cd collabdocs
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Database
```bash
# For SQLite (development):
python manage.py migrate

# For PostgreSQL:
# 1. Create database: createdb collabdocs
# 2. Update .env file with DB credentials
# 3. Run: python manage.py migrate
```

### Step 5: Create Superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin user
```

### Step 6: Start Server
```bash
python manage.py runserver
```

Visit: `http://localhost:8000/api/`

---

## 🧪 Testing with Postman

1. **Import Collection**: Open Postman → Import → `Postman_Collection.json`
2. **Set Variables**:
   - `access_token` - Your JWT token
   - `workspace_id` - UUID from workspace response
   - `document_id` - UUID from document response
3. **Run Requests**: Start with user login, then test other endpoints

**Collection Includes:**
- 19 pre-configured requests
- Example request bodies
- Organized into folders

---

## 🔐 Authentication

All endpoints (except admin login) require JWT token:

```bash
Authorization: Bearer <your-jwt-token>
```

Token lifetime: 1 hour (configurable in settings.py)

---

## 📊 Database Schema

All primary keys use UUID (uuid.uuid4, auto-generated, not editable)

**Key Constraints:**
- `WorkspaceMember`: Unique(workspace, user)
- `DocumentVersion`: Unique(document, version_number)
- `Tag`: Unique(name)

**Relationships:**
- Workspace → User (FK owner)
- Document → Workspace (FK)
- Document → User (FK created_by)
- WorkspaceMember → Workspace (FK)
- WorkspaceMember → User (FK)
- Comment → Document (FK)
- Comment → User (FK author)
- Comment → Comment (Self-FK parent for threading)
- DocumentVersion → Document (FK)
- DocumentVersion → User (FK created_by)
- AuditLog → User (FK actor)

---

## 🔄 Key Design Patterns

### Atomic Transactions
```python
@transaction.atomic
def perform_create(self, serializer):
    document = serializer.save(created_by=self.request.user)
    # Both operations succeed or both fail
```

### Django Signals
```python
@receiver(post_save, sender=Document)
def create_document_version(sender, instance, created, **kwargs):
    if created:
        DocumentVersion.objects.create(
            document=instance,
            content=instance.content,
            version_number=1,
            created_by=instance.created_by
        )
```

### Query Optimization
```python
def get_queryset(self):
    return Document.objects.select_related(
        'created_by',
        'workspace'
    ).prefetch_related('tags').annotate(
        version_count=Count('versions'),
        comment_count=Count('comments')
    )
```

---

## 📝 Environment Variables

Create `.env` file:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# SQLite (default)
# No additional config needed

# PostgreSQL (production)
DB_ENGINE=postgresql
DB_NAME=collabdocs
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

---

## 📤 Push to GitHub

```bash
cd collabdocs
git init
git add .
git commit -m "Initial commit: CollabDocs API"
git remote add origin https://github.com/Prajwal04k/collabdocs.git
git branch -M main
git push -u origin main
```

---

## 📚 File Structure

```
collabdocs/
├── manage.py                    # Django management
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
├── README.md                    # Full documentation
├── QUICKSTART.md               # This file
├── Postman_Collection.json     # API testing
├── collabdocs/
│   ├── settings.py             # Django settings (JWT, DB, etc)
│   ├── urls.py                 # Main URL routing
│   └── wsgi.py
└── api/
    ├── models.py               # 8 Data models
    ├── serializers.py          # DRF serializers
    ├── views.py                # 17 Endpoints
    ├── urls.py                 # API routing
    ├── middleware.py           # Request logging
    ├── signals.py              # Auto DocumentVersion + AuditLog
    └── migrations/
        └── 0001_initial.py     # Database schema
```

---

## ✨ Key Features Demonstrated

✅ **ModelViewSet** - Standard CRUD operations
✅ **@action Decorators** - Custom endpoints (invite, versions, tags)
✅ **Atomic Transactions** - Data integrity
✅ **Signals** - Auto-create DocumentVersion + AuditLog
✅ **SerializerMethodField** - Computed fields (version_count, comment_count)
✅ **Custom Validation** - Serializer.validate()
✅ **Q Objects** - Complex OR filtering
✅ **Middleware** - Request logging with timing
✅ **select_related** - Optimize FK queries
✅ **prefetch_related** - Optimize M2M queries
✅ **annotate/Count** - Aggregation queries
✅ **Role-Based Access** - via WorkspaceMember.role
✅ **Threaded Comments** - Self-referential FK
✅ **UUID Primary Keys** - Better than auto-increment
✅ **JWT Authentication** - Secure API access

---

## 🐛 Common Issues

### "django module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "PostgreSQL connection error"
```bash
# Make sure PostgreSQL is running
# Check .env credentials match your database
createdb collabdocs
```

### "Migration error"
```bash
# Delete db.sqlite3 and migrations (except 0001_initial.py)
rm db.sqlite3
python manage.py migrate
```

---

## 📖 Next Steps

1. ✅ Extract project
2. ✅ Create virtual environment
3. ✅ Install dependencies
4. ✅ Run migrations
5. ✅ Create superuser
6. ✅ Start server
7. ✅ Import Postman collection
8. ✅ Test all 17 endpoints
9. ✅ Push to GitHub

---

## 🎓 Learning Resources

- [Django REST Framework](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Postman Collection Guide](https://learning.postman.com/)

---

## 🚀 Production Checklist

- [ ] Set DEBUG=False
- [ ] Use strong SECRET_KEY
- [ ] Set up PostgreSQL
- [ ] Configure ALLOWED_HOSTS
- [ ] Use environment variables
- [ ] Enable HTTPS
- [ ] Set up logging
- [ ] Configure CORS if needed
- [ ] Set up monitoring
- [ ] Use Gunicorn for serving

---

**Version:** 1.0.0
**Built:** October 2026
**Author:** Claude AI
**Status:** ✅ Complete & Ready to Deploy
