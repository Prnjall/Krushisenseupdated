import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  className?: string;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'default', size = 'md', className = '', ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-full font-headline font-bold transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 active:scale-95';
    
    const variants = {
      default: 'bg-primary text-on-primary hover:opacity-90 shadow-xl shadow-primary/10',
      outline: 'border-2 border-outline-variant bg-transparent hover:bg-surface-container-low text-on-surface',
      ghost: 'hover:bg-surface-container-low text-on-surface',
    };
    
    const sizes = {
      sm: 'h-9 px-4 text-xs tracking-tight',
      md: 'h-11 px-6 py-2 text-sm uppercase tracking-wide',
      lg: 'h-14 px-8 text-lg uppercase tracking-wider',
      icon: 'h-10 w-10',
    };

    const combinedStyles = `${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`;

    return (
      <button
        ref={ref}
        className={combinedStyles}
        {...props}
      />
    );
  }
);

Button.displayName = 'Button';
