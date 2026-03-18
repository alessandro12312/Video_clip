import { apiClient } from "./client";
import type { PaginatedResponse } from "@/types/api";
import type {
  BracketListItem,
  BracketDetail,
  ContestEntryNested,
  EnterBracketInput,
  VoteMatchupInput,
} from "@/types/bracket";

export const bracketsApi = {
  list: (params?: { status?: string; page?: number }) =>
    apiClient
      .get<PaginatedResponse<BracketListItem>>("/brackets/", { params })
      .then((r) => r.data),

  getDetail: (id: number) =>
    apiClient.get<BracketDetail>(`/brackets/${id}/`).then((r) => r.data),

  enter: (bracketId: number, data: EnterBracketInput) =>
    apiClient
      .post<ContestEntryNested>(`/brackets/${bracketId}/enter/`, data)
      .then((r) => r.data),

  vote: (matchupId: number, data: VoteMatchupInput) =>
    apiClient
      .post<{ detail: string }>(`/matchups/${matchupId}/vote/`, data)
      .then((r) => r.data),
};
