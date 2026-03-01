"use client";

import { useEffect } from "react";
import { useIntersection } from "@/lib/hooks/use-intersection";
import { GradientSpinner } from "./gradient-spinner";

interface InfiniteScrollProps {
  hasNextPage: boolean | undefined;
  isFetchingNextPage: boolean;
  fetchNextPage: () => void;
}

export function InfiniteScroll({
  hasNextPage,
  isFetchingNextPage,
  fetchNextPage,
}: InfiniteScrollProps) {
  const { ref, isIntersecting } = useIntersection({ threshold: 0 });

  useEffect(() => {
    if (isIntersecting && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [isIntersecting, hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <div ref={ref} className="flex justify-center py-4">
      {isFetchingNextPage && <GradientSpinner size={24} />}
    </div>
  );
}
