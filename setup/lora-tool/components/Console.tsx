
import React, { useEffect, useRef } from 'react';

interface ConsoleProps {
  logs: string[];
}

export const Console: React.FC<ConsoleProps> = ({ logs }) => {
  const consoleEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="panel p-6">
      <h2 className="text-xl font-bold mb-4">Console</h2>
      <div className="bg-black/20 rounded-lg p-4 font-mono text-xs text-text-secondary h-64 overflow-y-auto">
        {logs.map((log, index) => (
          <p key={index} className={`whitespace-pre-wrap animate-fade-in ${log.toLowerCase().includes('error') ? 'text-red-400' : ''}`}>
            {log}
          </p>
        ))}
        <div ref={consoleEndRef} />
      </div>
    </div>
  );
};