import {
  useInfiniteQuery,
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { bracketsApi } from "@/lib/api/brackets";
import { extractPageFromUrl } from "@/lib/utils";
import { toast } from "sonner";
import type { EnterBracketInput, VoteMatchupInput } from "@/types/bracket";

export function useBrackets(params?: { status?: string }) {
  return useInfiniteQuery({
    queryKey: queryKeys.brackets.list(params),
    queryFn: ({ pageParam = 1 }) =>
      bracketsApi.list({ ...params, page: pageParam }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
  });
}

export function useBracketDetail(id: number) {
  return useQuery({
    queryKey: queryKeys.brackets.detail(id),
    queryFn: () => bracketsApi.getDetail(id),
    enabled: !!id,
  });
}

export function useEnterBracket() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      bracketId,
      data,
    }: {
      bracketId: number;
      data: EnterBracketInput;
    }) => bracketsApi.enter(bracketId, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.brackets.detail(variables.bracketId),
      });
      toast.success("Iscrizione completata!");
    },
    onError: (error: any) => {
      const detail =
        error.response?.data?.detail || "Errore durante l'iscrizione.";
      toast.error(detail);
    },
  });
}

export function useVoteMatchup(bracketId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      matchupId,
      data,
    }: {
      matchupId: number;
      data: VoteMatchupInput;
    }) => bracketsApi.vote(matchupId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.brackets.detail(bracketId),
      });
      toast.success("Voto registrato!");
    },
    onError: (error: any) => {
      const detail =
        error.response?.data?.detail || "Errore durante la votazione.";
      toast.error(detail);
    },
  });
}
