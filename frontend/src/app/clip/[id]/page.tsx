import { notFound } from "next/navigation";
import { ClipContent } from "./clip-content";
import { formatCount } from "@/lib/utils";
import type { Metadata } from "next";
import type { Video } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function getVideo(id: string): Promise<Video | null> {
  try {
    const res = await fetch(`${API_URL}/api/videos/${id}/`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const video = await getVideo(id);

  if (!video) {
    return { title: "Video non trovato" };
  }

  const ogDescription = `Clip di ${video.uploader} — ${formatCount(video.views)} views, ${video.average_rating > 0 ? video.average_rating.toFixed(1) + "★" : "non votato"}`;

  return {
    title: video.title,
    description: `Guarda "${video.title}" di ${video.uploader} su Video_clip. ${formatCount(video.views)} visualizzazioni.`,
    openGraph: {
      title: video.title,
      description: ogDescription,
      type: "video.other",
      url: `/clip/${id}`,
      ...(video.thumbnail_url && {
        images: [{ url: video.thumbnail_url }],
      }),
    },
    twitter: {
      card: video.thumbnail_url ? "summary_large_image" : "summary",
      title: video.title,
      description: `Clip di ${video.uploader} su Video_clip`,
      ...(video.thumbnail_url && { images: [video.thumbnail_url] }),
    },
  };
}

export default async function ClipPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const video = await getVideo(id);

  if (!video) notFound();

  return <ClipContent videoId={video.id} />;
}
