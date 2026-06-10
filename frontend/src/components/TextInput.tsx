import type { InputHTMLAttributes } from "react";

const baseClassName =
  "w-full rounded-xl border border-slate-300/90 bg-white px-4 py-3 font-sans text-[0.95rem] font-normal text-slate-800 shadow-[0_1px_2px_rgba(15,23,42,0.06),0_8px_24px_-22px_rgba(15,23,42,0.18)] outline-none transition placeholder:text-slate-400 hover:border-slate-400 hover:shadow-[0_1px_2px_rgba(15,23,42,0.08),0_10px_28px_-24px_rgba(15,23,42,0.22)] focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/15 focus:shadow-[0_1px_2px_rgba(15,23,42,0.08),0_10px_28px_-24px_rgba(14,116,144,0.18)] focus-visible:outline-none disabled:cursor-not-allowed disabled:border-slate-200 disabled:bg-slate-100 disabled:text-slate-500 disabled:shadow-none";

const errorClassName = "!border-red-400 hover:!border-red-500 focus:!border-red-500 focus:!ring-red-500/15";

type TextInputProps = InputHTMLAttributes<HTMLInputElement> & { hasError?: boolean };

export default function TextInput({ className = "", hasError, ...props }: TextInputProps) {
  return <input className={`${baseClassName} ${hasError ? errorClassName : ""} ${className}`.trim()} {...props} />;
}
