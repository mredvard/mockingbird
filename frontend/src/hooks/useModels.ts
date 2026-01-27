import { useQuery } from '@tanstack/react-query';
import { modelsApi } from '../services/api';

export function useModels() {
  const { data: models = [], isLoading: isLoadingModels } = useQuery({
    queryKey: ['models'],
    queryFn: modelsApi.list,
  });

  const { data: info, isLoading: isLoadingInfo } = useQuery({
    queryKey: ['backend-info'],
    queryFn: modelsApi.getInfo,
  });

  return {
    models,
    backendInfo: info,
    isLoading: isLoadingModels || isLoadingInfo,
    currentModel: info?.current_model,
    platform: info?.platform,
  };
}
