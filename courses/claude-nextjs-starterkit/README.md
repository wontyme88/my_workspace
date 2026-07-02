# Next.js Starter Kit

웹 개발을 빠르게 시작할 수 있는 프로덕션 준비 스타터 킷. 각 스택은 **공식 문서 최신 설치 가이드**를 준수합니다.

## 기술 스택

| 스택 | 버전 | 비고 |
| --- | --- | --- |
| [Next.js](https://nextjs.org) | 16 (App Router) | Turbopack 기본 |
| React | 19 | Next 16 동반 |
| TypeScript | 5.x (strict) | |
| [Tailwind CSS](https://tailwindcss.com) | v4 | `tailwind.config` 없음, CSS 기반 |
| [shadcn/ui](https://ui.shadcn.com) | latest | new-york(radix) 스타일, neutral |
| [lucide-react](https://lucide.dev) | 아이콘 | |
| [next-themes](https://github.com/pacocoursey/next-themes) | 다크 모드 | Light / Dark / System |

## 시작하기

```bash
npm install
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000) 을 엽니다.

- `/` — 랜딩 페이지
- `/dashboard` — shadcn/ui 데모 대시보드

## 스크립트

| 명령 | 설명 |
| --- | --- |
| `npm run dev` | 개발 서버 (Turbopack) |
| `npm run build` | 프로덕션 빌드 |
| `npm run start` | 프로덕션 서버 |
| `npm run lint` | ESLint |
| `npm run format` | Prettier 포맷 (+ Tailwind 클래스 정렬) |

## 컴포넌트 추가

shadcn/ui 컴포넌트는 CLI로 추가합니다:

```bash
npx shadcn@latest add tooltip dialog table
```

추가된 컴포넌트는 `src/components/ui/` 에 생성되며 프로젝트가 직접 소유합니다.

## 폴더 구조

```
src/
├── app/                 # App Router 라우트
│   ├── layout.tsx       # 루트 레이아웃 (ThemeProvider + Toaster)
│   ├── page.tsx         # 랜딩 페이지
│   └── dashboard/       # 데모 대시보드
├── components/
│   ├── ui/              # shadcn/ui 컴포넌트
│   ├── site-header.tsx  # 공용 헤더
│   ├── theme-provider.tsx
│   ├── mode-toggle.tsx  # 다크 모드 토글
│   └── toast-demo.tsx
└── lib/
    └── utils.ts         # cn() 헬퍼
```

## 테마 커스터마이징

Tailwind v4는 설정 파일이 없으므로, 테마 토큰은 `src/app/globals.css` 의 `@theme` / CSS 변수에서 수정합니다. shadcn 색상 토큰(`--primary`, `--background` 등)도 같은 파일에 있습니다.
