import React, { createContext, useContext, useState, ReactNode } from 'react';
import { DataMode } from '../types';

interface DataModeContextType {
  dataMode: DataMode;
  setDataMode: (mode: DataMode) => void;
}

const DataModeContext = createContext<DataModeContextType | undefined>(undefined);

export const DataModeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [dataMode, setDataModeInternal] = useState<DataMode>('connected');

  const setDataMode = (mode: DataMode) => {
    setDataModeInternal(mode);
  };


  return (
    <DataModeContext.Provider value={{ dataMode, setDataMode }}>
      {children}
    </DataModeContext.Provider>
  );
};

export const useDataMode = (): DataModeContextType => {
  const context = useContext(DataModeContext);
  if (!context) {
    throw new Error('useDataMode must be used within a DataModeProvider');
  }
  return context;
};
