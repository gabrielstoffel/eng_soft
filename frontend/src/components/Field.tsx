import type { ReactNode } from "react";

type FieldProps = {
  label: string;
  required?: boolean;
  children: ReactNode;
  hint?: string;
  error?: string;
  className?: string;
};

export default function Field({
  label,
  required = false,
  children,
  hint,
  error,
  className = "",
}: FieldProps) {
  return (
    <label className={`flex min-w-0 flex-1 flex-col gap-1.5 ${className}`.trim()}>
      <span className="text-sm font-semibold leading-5 text-slate-800">
        {label}
        {required ? <span className="ml-1 font-bold text-sky-700">*</span> : null}
      </span>
      {children}
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
      {hint ? <span className="text-[0.82rem] leading-5 text-slate-500">{hint}</span> : null}
    </label>
  );
}
