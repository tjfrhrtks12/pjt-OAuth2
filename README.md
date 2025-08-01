# Tzone - 학교 관리 시스템

학교 교사와 학생을 위한 AI 기반 관리 시스템입니다.

## 🚀 프로젝트 구조

```
last-chat/
├── back/          # FastAPI 백엔드
├── front/         # React 프론트엔드
└── README.md      # 이 파일
```

## 📋 필수 요구사항

- Python 3.8+
- Node.js 16+
- npm 또는 yarn

## 🔧 설치 및 설정

### 1. 백엔드 설정

```bash
cd back
pip install -r requirements.txt
```

### 2. 환경변수 설정

백엔드 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (if needed)
# DATABASE_URL=your_database_url_here

# JWT Secret (if needed)
# JWT_SECRET=your_jwt_secret_here
```

**⚠️ 중요**: `.env` 파일은 절대 Git에 커밋하지 마세요!

### 3. 프론트엔드 설정

```bash
cd front
npm install
```

## 🏃‍♂️ 실행 방법

### 백엔드 실행
```bash
cd back
uvicorn main:app --reload
```

### 프론트엔드 실행
```bash
cd front
npm start
```

## 🔐 보안 주의사항

1. **API 키 보호**: OpenAI API 키는 반드시 환경변수로 관리하세요
2. **환경변수 파일**: `.env` 파일은 `.gitignore`에 포함되어 있어야 합니다
3. **프로덕션 배포**: 프로덕션 환경에서는 환경변수를 서버 설정으로 관리하세요

## 📝 주요 기능

- AI 챗봇 (GPT-4o 기반)
- 교사/학생 관리
- 캘린더 기능
- OAuth 로그인

## 🤝 기여하기

1. 이 저장소를 포크하세요
2. 새로운 브랜치를 생성하세요 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성하세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 