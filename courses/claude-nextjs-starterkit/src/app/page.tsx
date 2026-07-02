import Link from "next/link";
import { ArrowRight, Component, Moon, Palette, Zap } from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const features = [
  {
    icon: Zap,
    title: "Next.js 16",
    description: "App Router와 Turbopack 기본 탑재로 빠른 개발 경험.",
  },
  {
    icon: Palette,
    title: "Tailwind CSS v4",
    description: "설정 파일 없이 CSS 기반으로 동작하는 최신 유틸리티 엔진.",
  },
  {
    icon: Component,
    title: "shadcn/ui",
    description: "복사해서 소유하는 접근 가능한 컴포넌트 + lucide 아이콘.",
  },
  {
    icon: Moon,
    title: "다크 모드",
    description: "next-themes로 Light / Dark / System 전환 즉시 지원.",
  },
];

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <section className="mx-auto max-w-5xl px-4 py-20 text-center sm:py-28">
          <Badge variant="secondary" className="mb-4">
            Next.js 16 · TypeScript · Tailwind v4 · shadcn/ui
          </Badge>
          <h1 className="text-4xl font-bold tracking-tight text-balance sm:text-6xl">
            웹 개발을 빠르게 시작하는 스타터 킷
          </h1>
          <p className="text-muted-foreground mx-auto mt-6 max-w-2xl text-lg text-balance">
            공식 문서 최신 버전을 준수하는 프로덕션 준비 베이스. 복제하고 바로
            빌드를 시작하세요.
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Button asChild size="lg">
              <Link href="/dashboard">
                대시보드 보기
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <a href="https://ui.shadcn.com" target="_blank" rel="noreferrer">
                shadcn/ui 문서
              </a>
            </Button>
          </div>
        </section>

        <section className="mx-auto max-w-5xl px-4 pb-24">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => (
              <Card key={feature.title}>
                <CardHeader>
                  <feature.icon className="text-primary h-8 w-8" />
                  <CardTitle className="mt-2">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </section>
      </main>
    </>
  );
}
