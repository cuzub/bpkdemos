import json
import os
import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Demo
from .schemas import DemoCreate, DemoRead, DemoUpdate, LoginPayload, TokenResponse, VisibilityPayload

SEED_DEMOS = [
    {
        "title": "Vision AI Playground",
        "description": "<p>Image recognition, OCR, and automated summaries.</p><ul><li>Image analysis</li><li>REST API</li></ul>",
        "links": [
            {"label": "Frontend", "url": "https://example.com/vision"},
            {"label": "API", "url": "https://example.com/vision-api"}
        ],
        "tags": ["AI", "Vision", "Python"],
        "image_path": None,
        "is_visible": True,
    },
    {
        "title": "Analytics Dashboard",
        "description": "<p>Interactive dashboards with business KPIs, dynamic filters, and exports.</p>",
        "links": [
            {"label": "Dashboard", "url": "https://example.com/analytics"},
            {"label": "Docs", "url": "https://example.com/analytics-docs"}
        ],
        "tags": ["BI", "Dashboard", "Vue"],
        "image_path": None,
        "is_visible": True,
    }
]

DATA_DIR = Path('/data')
UPLOADS_DIR = DATA_DIR / 'uploads'
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
JWT_SECRET = os.getenv('ADMIN_JWT_SECRET', 'change-me-please')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRE_HOURS = int(os.getenv('ADMIN_TOKEN_EXPIRE_HOURS', '12'))
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123!')
security = HTTPBearer(auto_error=False)


def normalize_tags(tags: list[str]) -> list[str]:
    seen = set()
    cleaned = []
    for tag in tags:
        value = (tag or '').strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(value)
    return cleaned[:20]


def migrate_schema() -> None:
    inspector = inspect(engine)
    columns = {column['name'] for column in inspector.get_columns('demos')} if inspector.has_table('demos') else set()
    with engine.begin() as connection:
        if 'tags_json' not in columns:
            connection.execute(text("ALTER TABLE demos ADD COLUMN tags_json TEXT NOT NULL DEFAULT '[]'"))
        if 'image_path' not in columns:
            connection.execute(text("ALTER TABLE demos ADD COLUMN image_path VARCHAR(500) NULL"))
        if 'is_visible' not in columns:
            connection.execute(text("ALTER TABLE demos ADD COLUMN is_visible BOOLEAN NOT NULL DEFAULT 1"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    migrate_schema()
    with SessionLocal() as session:
        if session.query(Demo).count() == 0:
            for item in SEED_DEMOS:
                session.add(
                    Demo(
                        title=item['title'],
                        description=item['description'],
                        links_json=json.dumps(item['links']),
                        tags_json=json.dumps(item['tags']),
                        image_path=item['image_path'],
                        is_visible=item.get('is_visible', True),
                    )
                )
            session.commit()
    yield


app = FastAPI(title='Demo Showcase API', lifespan=lifespan)
app.mount('/uploads', StaticFiles(directory=str(UPLOADS_DIR)), name='uploads')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({'sub': username, 'exp': expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def require_admin(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]):
    if not credentials or credentials.scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required.')
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token.') from exc
    if payload.get('sub') != ADMIN_USERNAME:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token.')
    return payload


@app.post('/api/auth/login', response_model=TokenResponse)
def login(payload: LoginPayload):
    if payload.username != ADMIN_USERNAME or payload.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials.')
    return TokenResponse(access_token=create_token(payload.username))


def serialize_demo(demo: Demo) -> DemoRead:
    return DemoRead(
        id=demo.id,
        title=demo.title,
        description=demo.description,
        links=json.loads(demo.links_json or '[]'),
        tags=json.loads(demo.tags_json or '[]'),
        image_path=demo.image_path,
        is_visible=demo.is_visible,
    )


@app.get('/api/health')
def healthcheck():
    return {'status': 'ok'}


@app.get('/api/tags', response_model=list[str])
def list_tags(db: Session = Depends(get_db)):
    demos = db.query(Demo).filter(Demo.is_visible.is_(True)).all()
    tags: list[str] = []
    for demo in demos:
        tags.extend(json.loads(demo.tags_json or '[]'))
    return sorted(normalize_tags(tags), key=lambda value: value.lower())


@app.get('/api/demos', response_model=list[DemoRead])
def list_demos(tag: str | None = None, db: Session = Depends(get_db)):
    demos = db.query(Demo).filter(Demo.is_visible.is_(True)).order_by(Demo.id.desc()).all()
    serialized = [serialize_demo(demo) for demo in demos]
    if tag:
        lookup = tag.strip().lower()
        serialized = [demo for demo in serialized if any(item.lower() == lookup for item in demo.tags)]
    return serialized


@app.get('/api/admin/demos', response_model=list[DemoRead], dependencies=[Depends(require_admin)])
def list_admin_demos(db: Session = Depends(get_db)):
    demos = db.query(Demo).order_by(Demo.id.desc()).all()
    return [serialize_demo(demo) for demo in demos]


@app.post('/api/demos', response_model=DemoRead, status_code=201, dependencies=[Depends(require_admin)])
def create_demo(payload: DemoCreate, db: Session = Depends(get_db)):
    demo = Demo(
        title=payload.title.strip(),
        description=payload.description or '',
        links_json=json.dumps([item.model_dump(mode='json') for item in payload.links]),
        tags_json=json.dumps(normalize_tags(payload.tags)),
        image_path=payload.image_path,
        is_visible=payload.is_visible,
    )
    db.add(demo)
    db.commit()
    db.refresh(demo)
    return serialize_demo(demo)


@app.put('/api/demos/{demo_id}', response_model=DemoRead, dependencies=[Depends(require_admin)])
def update_demo(demo_id: int, payload: DemoUpdate, db: Session = Depends(get_db)):
    demo = db.query(Demo).filter(Demo.id == demo_id).first()
    if not demo:
        raise HTTPException(status_code=404, detail='Demo not found.')

    demo.title = payload.title.strip()
    demo.description = payload.description or ''
    demo.links_json = json.dumps([item.model_dump(mode='json') for item in payload.links])
    demo.tags_json = json.dumps(normalize_tags(payload.tags))
    demo.image_path = payload.image_path
    demo.is_visible = payload.is_visible
    db.commit()
    db.refresh(demo)
    return serialize_demo(demo)


@app.patch('/api/demos/{demo_id}/visibility', response_model=DemoRead, dependencies=[Depends(require_admin)])
def update_demo_visibility(demo_id: int, payload: VisibilityPayload, db: Session = Depends(get_db)):
    demo = db.query(Demo).filter(Demo.id == demo_id).first()
    if not demo:
        raise HTTPException(status_code=404, detail='Demo not found.')

    demo.is_visible = payload.is_visible
    db.commit()
    db.refresh(demo)
    return serialize_demo(demo)


def delete_file_if_local(path: str | None):
    if not path or not path.startswith('/uploads/'):
        return
    absolute_path = UPLOADS_DIR / path.replace('/uploads/', '', 1)
    if absolute_path.exists() and absolute_path.is_file():
        absolute_path.unlink()


@app.delete('/api/demos/{demo_id}', status_code=204, dependencies=[Depends(require_admin)])
def delete_demo(demo_id: int, db: Session = Depends(get_db)):
    demo = db.query(Demo).filter(Demo.id == demo_id).first()
    if not demo:
        raise HTTPException(status_code=404, detail='Demo not found.')

    delete_file_if_local(demo.image_path)
    db.delete(demo)
    db.commit()
    return None


@app.post('/api/upload-image', dependencies=[Depends(require_admin)])
def upload_image(file: UploadFile = File(...), current_user=Depends(require_admin)):
    del current_user
    content_type = (file.content_type or '').lower()
    if content_type not in {'image/png', 'image/jpeg', 'image/webp', 'image/gif'}:
        raise HTTPException(status_code=400, detail='Unsupported format. Use PNG, JPG, WEBP, or GIF.')

    extension = Path(file.filename or '').suffix.lower()
    if extension not in {'.png', '.jpg', '.jpeg', '.webp', '.gif'}:
        extension = '.png'

    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:10]}{extension}"
    destination = UPLOADS_DIR / filename
    with destination.open('wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {'image_path': f'/uploads/{filename}'}
