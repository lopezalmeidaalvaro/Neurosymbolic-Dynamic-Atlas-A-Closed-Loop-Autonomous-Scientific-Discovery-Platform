import { cn } from '@/lib/utils/cn';

interface FocusContainerProps {
  children: React.ReactNode;
  className?: string;
  size?: 'md' | 'lg' | 'xl';
}

const SIZE = {
  md: 'max-w-5xl',
  lg: 'max-w-6xl',
  xl: 'max-w-7xl',
};

export function FocusContainer({ children, className, size = 'lg' }: FocusContainerProps) {
  return (
    <div className={cn('mx-auto w-full px-5 py-7 sm:px-6 lg:px-8 lg:py-10', SIZE[size], className)}>
      {children}
    </div>
  );
}
