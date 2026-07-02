"use client";

import { toast } from "sonner";

import { Button } from "@/components/ui/button";

export function ToastDemo() {
  return (
    <Button
      variant="outline"
      onClick={() =>
        toast.success("저장되었습니다", {
          description: "sonner 토스트가 정상 동작합니다.",
        })
      }
    >
      토스트 띄우기
    </Button>
  );
}
