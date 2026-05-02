import type { ReactNode, SelectHTMLAttributes } from "react";

const baseClassName =
  "w-full appearance-none rounded-xl border border-slate-300/90 bg-white px-4 py-3 pr-11 font-sans text-[0.95rem] font-normal text-slate-800 shadow-[0_1px_2px_rgba(15,23,42,0.06),0_8px_24px_-22px_rgba(15,23,42,0.18)] outline-none transition hover:border-slate-400 hover:shadow-[0_1px_2px_rgba(15,23,42,0.08),0_10px_28px_-24px_rgba(15,23,42,0.22)] focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/15 focus:shadow-[0_1px_2px_rgba(15,23,42,0.08),0_10px_28px_-24px_rgba(14,116,144,0.18)] focus-visible:outline-none disabled:cursor-not-allowed disabled:border-slate-200 disabled:bg-slate-100 disabled:text-slate-500 disabled:shadow-none";

type SelectInputProps = SelectHTMLAttributes<HTMLSelectElement> & {
  children: ReactNode;
};

export default function SelectInput({
  className = "",
  children,
  ...props
}: SelectInputProps) {
  return (
    <div className="relative">
      <select className={`${baseClassName} ${className}`.trim()} {...props}>
        {children}
      </select>
      <span className="pointer-events-none absolute inset-y-0 right-4 flex items-center text-slate-600">
        <svg
          aria-hidden="true"
          viewBox="0 0 20 20"
          fill="none"
          className="h-4 w-4"
        >
          <path
            d="M5 7.5L10 12.5L15 7.5"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </span>
    </div>
  );
}
