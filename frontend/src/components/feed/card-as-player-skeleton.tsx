import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function CardAsPlayerSkeleton() {
  return (
    <Card data-snap-target className="overflow-hidden">
      <div className="flex flex-col lg:flex-row">
        <Skeleton className="aspect-video w-full lg:flex-1" />
        <div className="hidden lg:flex flex-col gap-2 w-72 shrink-0 border-l border-border/50 p-3">
          <Skeleton className="h-3 w-24" />
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="space-y-1">
              <div className="flex gap-2">
                <Skeleton className="h-4 w-10" />
                <Skeleton className="h-4 w-16" />
              </div>
              <Skeleton className="h-3 w-full" />
            </div>
          ))}
        </div>
      </div>
      <div className="p-3 space-y-2">
        <Skeleton className="h-5 w-2/3" />
        <div className="flex items-center gap-2">
          <Skeleton className="h-7 w-7 rounded-full" />
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-4 w-12" />
        </div>
      </div>
      <div className="px-3 pb-3">
        <Skeleton className="h-16 w-full" />
      </div>
    </Card>
  );
}
