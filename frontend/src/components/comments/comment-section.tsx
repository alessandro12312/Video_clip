"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CommentList } from "./comment-list";
import type { Comment } from "@/types";

interface CommentSectionProps {
  comments: Comment[];
  onTimestampClick?: (seconds: number) => void;
}

export function CommentSection({ comments, onTimestampClick }: CommentSectionProps) {
  const timestampedCount = comments.filter((c) => c.timestamp_second > 0).length;

  return (
    <Tabs defaultValue="all" className="w-full">
      <TabsList className="w-full justify-start bg-transparent border-b border-border rounded-none h-auto p-0">
        <TabsTrigger
          value="all"
          className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent"
        >
          Tutti ({comments.length})
        </TabsTrigger>
        <TabsTrigger
          value="timestamped"
          className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent"
        >
          Nel video ({timestampedCount})
        </TabsTrigger>
      </TabsList>

      <TabsContent value="all" className="mt-2">
        <CommentList
          comments={comments}
          mode="all"
          onTimestampClick={onTimestampClick}
        />
      </TabsContent>

      <TabsContent value="timestamped" className="mt-2">
        <CommentList
          comments={comments}
          mode="timestamped"
          onTimestampClick={onTimestampClick}
        />
      </TabsContent>
    </Tabs>
  );
}
