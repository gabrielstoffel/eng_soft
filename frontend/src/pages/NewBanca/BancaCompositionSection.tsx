import { useFormContext } from "react-hook-form";

import type { NewBancaFormState } from "../../types/new-banca.ts";
import { ALL_ROLES, ROLE_LABELS, ROLES_BY_TIPO } from "./config";
import MemberField from "./MemberField";

type BancaCompositionSectionProps = {
  disabled?: boolean;
};

export default function BancaCompositionSection({
  disabled = false,
}: BancaCompositionSectionProps) {
  const { watch } = useFormContext<NewBancaFormState>();
  const tipo = watch("tipo");
  const visibleRoles = ROLES_BY_TIPO[tipo];

  return (
    <section className="overflow-hidden rounded-xl bg-white shadow-[0_20px_50px_-40px_rgba(15,23,42,0.35)]">
      <div className="border-b border-slate-200 px-4 py-5 sm:px-8">
        <div className="text-xs font-semibold tracking-[0.18em] text-sky-700 uppercase">
          Etapa 2 de 2
        </div>
        <h2 className="mt-1 text-2xl font-semibold tracking-tight text-slate-950">
          Composição da banca
        </h2>
      </div>

      <div className="space-y-4 px-4 py-6 sm:px-8 sm:py-8">
        {ALL_ROLES.map((role) =>
          visibleRoles[role] === "hidden" ? null : (
            <MemberField
              key={role}
              label={ROLE_LABELS[role]}
              name={role}
              required={visibleRoles[role] === "required"}
              requireEmail={role === "orientador"}
              disabled={disabled}
            />
          ),
        )}
      </div>
    </section>
  );
}
