"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { Upload, X, Film, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { TagBadge } from "@/components/shared/tag-badge";
import { GradientSpinner } from "@/components/shared/gradient-spinner";
import { useUploadVideo } from "@/lib/hooks/use-videos";
import { TAG_COLORS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import type { VideoTag } from "@/types";

type Step = "dropzone" | "metadata" | "uploading" | "done";

export default function CaricaPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { mutate: uploadVideo } = useUploadVideo();

  const [step, setStep] = useState<Step>("dropzone");
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [tag, setTag] = useState<VideoTag>("clutch");
  const [progress, setProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileSelect = useCallback((selectedFile: File) => {
    if (!selectedFile.type.startsWith("video/")) {
      toast.error("Seleziona un file video valido.");
      return;
    }
    if (selectedFile.size > 100 * 1024 * 1024) {
      toast.error("Il file non può superare i 100 MB.");
      return;
    }
    setFile(selectedFile);
    setStep("metadata");
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) handleFileSelect(droppedFile);
    },
    [handleFileSelect]
  );

  const handleUpload = useCallback(() => {
    if (!file || !title.trim()) return;

    setStep("uploading");
    setProgress(0);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title.trim());
    formData.append("tag", tag);

    uploadVideo(
      { data: formData, onProgress: setProgress },
      {
        onSuccess: () => {
          setStep("done");
          toast.success("Clip caricata con successo!");
        },
        onError: () => {
          setStep("metadata");
          toast.error("Errore durante il caricamento.");
        },
      }
    );
  }, [file, title, tag, uploadVideo]);

  const handleReset = useCallback(() => {
    setFile(null);
    setTitle("");
    setTag("clutch");
    setProgress(0);
    setStep("dropzone");
  }, []);

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Carica una clip</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Condividi i tuoi momenti di gioco migliori
        </p>
      </div>

      {/* Step 1: Dropzone */}
      {step === "dropzone" && (
        <Card>
          <CardContent className="p-8">
            <div
              className={cn(
                "flex flex-col items-center justify-center gap-4 rounded-lg border-2 border-dashed p-12 transition-colors cursor-pointer",
                isDragging
                  ? "border-primary bg-primary/5"
                  : "border-border/50 hover:border-border"
              )}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="gradient-bg rounded-full p-4">
                <Upload className="h-8 w-8 text-white" />
              </div>
              <div className="text-center">
                <p className="text-sm font-medium">
                  Trascina qui il tuo video o clicca per selezionarlo
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  MP4, WebM, MOV — max 100 MB
                </p>
              </div>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFileSelect(f);
              }}
            />
          </CardContent>
        </Card>
      )}

      {/* Step 2: Metadata */}
      {step === "metadata" && file && (
        <Card>
          <CardContent className="p-6 space-y-5">
            {/* File preview */}
            <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-3">
              <Film className="h-5 w-5 text-muted-foreground shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(file.size / (1024 * 1024)).toFixed(1)} MB
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 shrink-0"
                onClick={handleReset}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title">Titolo</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Dai un titolo alla tua clip..."
                maxLength={100}
              />
            </div>

            {/* Tag selection */}
            <div className="space-y-2">
              <Label>Categoria</Label>
              <div className="flex gap-2">
                {(Object.keys(TAG_COLORS) as VideoTag[]).map((t) => (
                  <button
                    key={t}
                    type="button"
                    className={cn(
                      "rounded-full px-4 py-1.5 text-sm font-medium transition-all border-2",
                      tag === t
                        ? "border-primary scale-105"
                        : "border-transparent opacity-70 hover:opacity-100"
                    )}
                    onClick={() => setTag(t)}
                  >
                    <TagBadge tag={t} />
                  </button>
                ))}
              </div>
            </div>

            {/* Submit */}
            <Button
              className="w-full gradient-bg"
              disabled={!title.trim()}
              onClick={handleUpload}
            >
              <Upload className="h-4 w-4 mr-2" />
              Carica clip
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Uploading */}
      {step === "uploading" && (
        <Card>
          <CardContent className="p-8 flex flex-col items-center gap-4">
            <GradientSpinner size={48} />
            <div className="text-center">
              <p className="text-sm font-medium">Caricamento in corso...</p>
              <p className="text-2xl font-bold gradient-text mt-1">{progress}%</p>
            </div>
            <Progress value={progress} className="w-full max-w-xs" />
          </CardContent>
        </Card>
      )}

      {/* Step 4: Done */}
      {step === "done" && (
        <Card>
          <CardContent className="p-8 flex flex-col items-center gap-4">
            <div className="gradient-bg rounded-full p-4">
              <Check className="h-8 w-8 text-white" />
            </div>
            <div className="text-center">
              <p className="text-lg font-bold">Clip caricata!</p>
              <p className="text-sm text-muted-foreground mt-1">
                La tua clip è ora visibile a tutti
              </p>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" onClick={handleReset}>
                Carica un&apos;altra
              </Button>
              <Button className="gradient-bg" onClick={() => router.push("/home")}>
                Vai al feed
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
