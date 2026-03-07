"use client";

import { Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDownloadVideo } from "@/lib/hooks/use-videos";
import { toast } from "sonner";

interface DownloadButtonProps {
  videoId: number;
  isOwner: boolean;
  allowDownload: boolean;
}

export function DownloadButton({ videoId, isOwner, allowDownload }: DownloadButtonProps) {
  const { mutate: download, isPending } = useDownloadVideo();

  // Visibile solo se proprietario o allow_download
  if (!isOwner && !allowDownload) return null;

  const handleClick = () => {
    download(videoId, {
      onError: (error) => {
        const message =
          (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ??
          "Errore durante il download";
        toast.error(message);
      },
    });
  };

  return (
    <Button variant="ghost" size="sm" onClick={handleClick} disabled={isPending}>
      {isPending ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <Download className="h-4 w-4" />
      )}
      <span className="ml-1.5">Scarica</span>
    </Button>
  );
}
