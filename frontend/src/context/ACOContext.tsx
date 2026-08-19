import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService } from '../services/apiService';

export const SUPPORTED_YEARS = [2022, 2023, 2024];

export interface ACOItemSummary {
  id: string;
  aco_id: string;
  name: string;
  state?: string;
  track?: string;
  agreement_type?: string;
  risk_model?: string;
}

interface ACOContextType {
  selectedAcoId: string;
  setSelectedAcoId: (id: string) => void;
  selectedYear: number;
  setSelectedYear: (year: number) => void;
  supportedYears: number[];
  availableAcos: ACOItemSummary[];
  loadingAcos: boolean;
}

const ACOContext = createContext<ACOContextType | undefined>(undefined);

export const ACOProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [selectedAcoId, setSelectedAcoId] = useState<string>('A1001');
  const [selectedYear, setSelectedYearState] = useState<number>(2024);
  const [supportedYears, setSupportedYears] = useState<number[]>(SUPPORTED_YEARS);
  const [availableAcos, setAvailableAcos] = useState<ACOItemSummary[]>([]);
  const [loadingAcos, setLoadingAcos] = useState<boolean>(true);

  // Discover performance years dynamically from database API
  useEffect(() => {
    const fetchYears = async () => {
      try {
        const res = await apiService.request<number[]>('/performance-years');
        if (res.success && res.data && Array.isArray(res.data) && res.data.length > 0) {
          setSupportedYears(res.data);
        }
      } catch (err) {
        console.warn('Could not fetch performance years dynamically, using fallback:', err);
      }
    };
    fetchYears();
  }, []);

  const setSelectedYear = (year: number) => {
    setSelectedYearState(year);
  };

  // Fetch ACO list strictly for the chosen selectedYear (Cascading Filter)
  useEffect(() => {
    const fetchAcos = async () => {
      setLoadingAcos(true);
      try {
        const res = await apiService.request<ACOItemSummary[]>(`/acos?year=${selectedYear}`);
        if (res.success && res.data && Array.isArray(res.data) && res.data.length > 0) {
          setAvailableAcos(res.data);
          
          // Cascading filter validation: if current selectedAcoId is not active in this year, reset to first available ACO
          const isPresent = res.data.some(a => a.aco_id === selectedAcoId || a.id === selectedAcoId);
          if (!isPresent) {
            const defaultId = res.data[0].aco_id || res.data[0].id;
            setSelectedAcoId(defaultId);
          }
        } else {
          setAvailableAcos([]);
        }
      } catch (err) {
        console.error('Error fetching ACO list for year:', selectedYear, err);
      } finally {
        setLoadingAcos(false);
      }
    };

    fetchAcos();
  }, [selectedYear]);

  return (
    <ACOContext.Provider
      value={{
        selectedAcoId,
        setSelectedAcoId,
        selectedYear,
        setSelectedYear,
        supportedYears,
        availableAcos,
        loadingAcos,
      }}
    >
      {children}
    </ACOContext.Provider>
  );
};

export const useACO = (): ACOContextType => {
  const context = useContext(ACOContext);
  if (!context) {
    throw new Error('useACO must be used within an ACOProvider');
  }
  return context;
};
