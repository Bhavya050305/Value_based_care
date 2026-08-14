import { RecommendationItem } from '../../types/recommendations';
import { mockRecommendations } from '../../data/mock/recommendationsData';

export async function getRecommendations(): Promise<RecommendationItem[]> {
  return mockRecommendations;
}
