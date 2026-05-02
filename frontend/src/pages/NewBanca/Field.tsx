import type { ReactNode } from "react";

type FieldProps = {
  label: string;
  required?: boolean;
  children: ReactNode;
  hint?: string;
  className?: string;
};

export default function Field({
  label,
  required = false,
  children,
  hint,
  className = "",
}: FieldProps) {
  return (
    <label className={`flex min-w-0 flex-1 flex-col gap-1.5 ${className}`.trim()}>
      <span className="text-sm font-semibold leading-5 text-slate-800">
        {label}
        {required ? <span className="ml-1 font-bold text-sky-700">*</span> : null}
      </span>
      {children}
      {hint ? <span className="text-[0.82rem] leading-5 text-slate-500">{hint}</span> : null}
    </label>
  );
}
