"use client";

import { useState } from "react";
import { useUpdateProfile } from "@/lib/hooks/use-users";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import type { User } from "@/types";

const BIO_MAX_LENGTH = 500;

interface ProfileEditFormProps {
  user: User;
  onClose: () => void;
}

export function ProfileEditForm({ user, onClose }: ProfileEditFormProps) {
  const [bio, setBio] = useState(user.bio || "");
  const updateProfile = useUpdateProfile();

  const handleSave = () => {
    updateProfile.mutate(
      { id: user.id, data: { bio } },
      {
        onSuccess: () => {
          toast.success("Profilo aggiornato");
          onClose();
        },
        onError: () => {
          toast.error("Errore nel salvataggio del profilo");
        },
      }
    );
  };

  return (
    <div className="mt-3 space-y-3">
      <div>
        <Label htmlFor="bio-input">Bio</Label>
        <Textarea
          id="bio-input"
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          placeholder="Scrivi qualcosa su di te..."
          maxLength={BIO_MAX_LENGTH}
          rows={3}
          className="mt-1"
          aria-describedby="bio-hint"
        />
        <p id="bio-hint" className="text-xs text-muted-foreground mt-1">
          {bio.length}/{BIO_MAX_LENGTH} caratteri
        </p>
      </div>

      <div className="flex gap-2">
        <Button
          size="sm"
          onClick={handleSave}
          disabled={updateProfile.isPending}
          aria-label={updateProfile.isPending ? "Salvataggio in corso..." : "Salva"}
        >
          {updateProfile.isPending && (
            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
          )}
          Salva
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={onClose}
          disabled={updateProfile.isPending}
        >
          Annulla
        </Button>
      </div>
    </div>
  );
}
