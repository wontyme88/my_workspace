# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@AGENTS.md

> 위에서 가져온 `AGENTS.md`에 가장 중요한 규칙이 담겨 있습니다: 이 프로젝트는 Next.js **16**이며 옛 버전과 API가 다릅니다. Next 관련 코드를 작성하기 전에 `node_modules/next/dist/docs/`(예: `01-app/`)의 해당 가이드를 먼저 읽으세요.

## 명령어

모든 명령은 이 디렉터리(`courses/claude-nextjs-starterkit/`)에서 실행하세요. 이 폴더는 `my_workspace` git 저장소의 하위 폴더이며 저장소 루트가 아닙니다.

| 명령 | 용도 |
| --- | --- |
| `npm run dev` | 개발 서버 :3000 (Turbopack) |
| `npm run build` | 프로덕션 빌드 |
| `npm run start` | 빌드 결과 서빙 |
| `npm run lint` | ESLint (flat config, `eslint-config-next`) |
| `npm run format` | Prettier 포맷 + Tailwind 클래스 정렬 |
| `npm run format:check` | Prettier 검사만 |
| `npx shadcn@latest add <이름>` | shadcn/ui 컴포넌트를 `src/components/ui/`에 추가 |

테스트 러너는 설정되어 있지 않습니다.

## 아키텍처

Next.js 16 App Router + React 19 + TypeScript(strict) 스타터입니다. 여러 파일을 함께 봐야 이해되는 큰 그림은 다음과 같습니다.

- **`src/` 구조와 `@/*` 별칭.** 모든 앱 코드는 `src/` 아래에 있습니다. 라우터 폴더는 저장소 루트가 아니라 `src/app/`입니다. `@/*`는 `./src/*`로 매핑되며(`tsconfig.json`), shadcn 별칭(`@/components`, `@/lib/utils`, `@/components/ui`)은 `components.json`에 정의돼 있습니다.

- **Tailwind v4는 설정 파일이 없습니다.** `tailwind.config.*` 파일이 없습니다. 테마 토큰·색상 변수·다크 모드 설정은 모두 `src/app/globals.css`에 있으며, `@import "tailwindcss"`, `@theme inline { ... }` 블록, CSS 커스텀 속성(`--primary`, `--background` 등)으로 관리합니다. 디자인 토큰을 바꾸려면 JS 설정이 아니라 이 파일을 수정하세요. `shadcn/tailwind.css`와 `tw-animate-css`도 여기서 import합니다.

- **테마는 루트 레이아웃을 통해 흐릅니다.** `src/app/layout.tsx`가 자식을 `ThemeProvider`(`src/components/theme-provider.tsx`의 얇은 `next-themes` 래퍼)로 감싸고 `attribute="class"` + `defaultTheme="system"`을 씁니다. 따라서 다크 모드는 `<html>`의 `.dark` 클래스로 동작합니다. `mode-toggle.tsx`가 테마를 전환하고, `<Toaster />`(sonner)도 여기서 마운트되므로 어떤 컴포넌트든 별도 설정 없이 `toast()`를 호출할 수 있습니다.

- **shadcn/ui 컴포넌트는 패키지가 아니라 프로젝트가 직접 소유합니다.** 스타일은 `radix-nova`, 기본 색상은 `neutral`(`components.json`). 생성된 컴포넌트는 `src/components/ui/`에 들어오며 직접 수정합니다. 클래스명은 `src/lib/utils.ts`의 `cn()` 헬퍼(clsx + tailwind-merge)로 조합하세요.

## 라우트

- `/` → `src/app/page.tsx` (랜딩)
- `/dashboard` → `src/app/dashboard/page.tsx` (shadcn/ui 데모)
