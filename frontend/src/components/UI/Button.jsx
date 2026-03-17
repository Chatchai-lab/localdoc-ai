import React from 'react';

const Button = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  disabled = false, 
  className = '',
  type = 'button' 
}) => {
  
  // Grund-Styles für alle Buttons
  const baseStyles = "px-4 py-2 rounded-xl font-medium transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm";
  
  // Varianten-Logik
  const variants = {
    primary: "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/20",
    danger: "bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white border border-red-500/50",
    ghost: "bg-transparent hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-700",
    outline: "bg-transparent border border-blue-500/50 text-blue-400 hover:bg-blue-500/10"
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;