
import React from 'react';
import { Icon } from './Icons';

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-20">
      <div className="mx-auto max-w-[1920px] px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div role="button" tabIndex={0} className="relative flex items-center gap-3 group">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-accent-violet to-accent-cyan ring-1 ring-white/20 grid place-items-center">
                <Icon />
            </div>
            <div className="flex items-center gap-2">
              <span className="font-black tracking-tight text-xl">
                <span className="opacity-90">LORA</span> <span className="text-violet-400">Helper</span>
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wide px-2 py-1 rounded-md bg-white/10 text-text-secondary">
                V2.2
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
