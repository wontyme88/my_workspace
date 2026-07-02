import { Activity, CreditCard, DollarSign, Users } from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { ToastDemo } from "@/components/toast-demo";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const stats = [
  { title: "총 매출", value: "₩45,231,890", icon: DollarSign, delta: "+20.1%" },
  { title: "신규 고객", value: "+2,350", icon: Users, delta: "+180.1%" },
  { title: "판매", value: "+12,234", icon: CreditCard, delta: "+19%" },
  { title: "활성 사용자", value: "+573", icon: Activity, delta: "+201" },
];

export default function DashboardPage() {
  return (
    <>
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">대시보드</h1>
            <p className="text-muted-foreground text-sm">
              shadcn/ui 컴포넌트로 구성한 데모 화면입니다.
            </p>
          </div>
          <ToastDemo />
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <stat.icon className="text-muted-foreground h-4 w-4" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-muted-foreground text-xs">
                  {stat.delta} 지난달 대비
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <Tabs defaultValue="overview" className="mt-8">
          <TabsList>
            <TabsTrigger value="overview">개요</TabsTrigger>
            <TabsTrigger value="loading">로딩 예시</TabsTrigger>
          </TabsList>
          <TabsContent value="overview">
            <Card>
              <CardHeader>
                <CardTitle>개요</CardTitle>
                <CardDescription>
                  탭, 카드, 통계 위젯을 조합한 기본 레이아웃 예시입니다.
                </CardDescription>
              </CardHeader>
              <CardContent className="text-muted-foreground text-sm">
                이 스타터 킷을 복제해 실제 데이터와 차트로 교체하세요.
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="loading">
            <Card>
              <CardHeader>
                <CardTitle>Skeleton 로딩</CardTitle>
                <CardDescription>
                  데이터 로딩 중 표시할 스켈레톤 예시입니다.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-4/5" />
                <Skeleton className="h-4 w-3/5" />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </>
  );
}
