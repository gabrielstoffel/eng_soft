import { IconPlus } from "@tabler/icons-react";
import { IconUsersGroup } from "@tabler/icons-react";
import { useEffect, useMemo, useState } from "react";
import { useFormContext } from "react-hook-form";

import {
  emptyMemberForm,
  type NewBancaFormState,
} from "../../types/new-banca.ts";
import {
  ALL_ROLES,
  ROLE_LABELS,
  ROLES_BY_TIPO,
  type OptionalMemberRole,
} from "./config";
import MemberField from "./MemberField";

type BancaCompositionSectionProps = {
  disabled?: boolean;
};

type CompositionTab = "orientacao" | "internos" | "externos";

const TAB_LABELS: Record<CompositionTab, string> = {
  orientacao: "Orientação",
  internos: "Internos",
  externos: "Externos",
};

const ROLES_BY_TAB: Record<
  CompositionTab,
  readonly (typeof ALL_ROLES)[number][]
> = {
  orientacao: ["orientador", "coorientador"],
  internos: ["interno1", "interno2", "supl_int"],
  externos: ["externo1", "externo2", "supl_ext"],
};

export default function BancaCompositionSection({
  disabled = false,
}: BancaCompositionSectionProps) {
  const { setValue, watch } = useFormContext<NewBancaFormState>();
  const [activeTab, setActiveTab] = useState<CompositionTab>("orientacao");
  const tipo = watch("tipo");
  const visibleRoles = ROLES_BY_TIPO[tipo];

  const activeRoles = ALL_ROLES.filter((role) => {
    if (visibleRoles[role] === "required") return true;
    if (visibleRoles[role] === "optional") return watch(role) !== null;
    return false;
  });
  const visibleRolesByTab = useMemo(
    () =>
      ({
        orientacao: ROLES_BY_TAB.orientacao.filter(
          (role) => visibleRoles[role] !== "hidden",
        ),
        internos: ROLES_BY_TAB.internos.filter(
          (role) => visibleRoles[role] !== "hidden",
        ),
        externos: ROLES_BY_TAB.externos.filter(
          (role) => visibleRoles[role] !== "hidden",
        ),
      }) satisfies Record<
        CompositionTab,
        readonly (typeof ALL_ROLES)[number][]
      >,
    [visibleRoles],
  );
  const activeRolesByTab = useMemo(
    () =>
      ({
        orientacao: activeRoles.filter((role) =>
          ROLES_BY_TAB.orientacao.includes(role),
        ),
        internos: activeRoles.filter((role) =>
          ROLES_BY_TAB.internos.includes(role),
        ),
        externos: activeRoles.filter((role) =>
          ROLES_BY_TAB.externos.includes(role),
        ),
      }) satisfies Record<CompositionTab, typeof activeRoles>,
    [activeRoles],
  );
  const availableTabs = (Object.keys(TAB_LABELS) as CompositionTab[]).filter(
    (tab) => visibleRolesByTab[tab].length > 0,
  );
  const optionalRolesByTab = useMemo(
    () =>
      ({
        orientacao: ROLES_BY_TAB.orientacao.filter(
          (role): role is OptionalMemberRole =>
            visibleRoles[role] === "optional",
        ),
        internos: ROLES_BY_TAB.internos.filter(
          (role): role is OptionalMemberRole =>
            visibleRoles[role] === "optional",
        ),
        externos: ROLES_BY_TAB.externos.filter(
          (role): role is OptionalMemberRole =>
            visibleRoles[role] === "optional",
        ),
      }) satisfies Record<CompositionTab, readonly OptionalMemberRole[]>,
    [visibleRoles],
  );

  useEffect(() => {
    if (!availableTabs.includes(activeTab)) {
      setActiveTab(availableTabs[0] ?? "orientacao");
    }
  }, [activeTab, availableTabs]);

  function toggleOptionalRole(role: OptionalMemberRole) {
    const currentValue = watch(role);
    setValue(role, currentValue ? null : { ...emptyMemberForm });
  }

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

      <div className="space-y-6 px-4 py-6 sm:px-8 sm:py-8">
        <div>
          <div className="flex items-center gap-1">
            <IconUsersGroup
              aria-hidden="true"
              size={18}
              stroke={1.9}
              className="shrink-0 self-center text-sky-700"
            />
            <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">
              Participantes
            </h3>
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Informe os participantes da banca e adicione os opcionais quando
            necessário.
          </p>
        </div>

        {availableTabs.length > 1 ? (
          <div className="rounded-xl bg-slate-100 p-1">
            <div
              className="grid gap-1"
              style={{
                gridTemplateColumns: `repeat(${availableTabs.length}, minmax(0, 1fr))`,
              }}
            >
              {availableTabs.map((tab) => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveTab(tab)}
                  className={
                    activeTab === tab
                      ? "inline-flex w-full cursor-pointer items-center justify-center rounded-lg bg-white px-4 py-3 text-sm font-semibold text-slate-950 shadow-[0_1px_2px_rgba(15,23,42,0.06)] transition"
                      : "inline-flex w-full cursor-pointer items-center justify-center rounded-lg px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-white/70"
                  }
                >
                  {TAB_LABELS[tab]}
                </button>
              ))}
            </div>
          </div>
        ) : null}

        <div className="space-y-3">
          <div className="space-y-4">
            {activeRolesByTab[activeTab].map((role) => (
              <MemberField
                key={role}
                label={ROLE_LABELS[role]}
                name={role}
                required={visibleRoles[role] === "required"}
                requireEmail={role === "orientador"}
                disabled={disabled}
                onRemove={
                  visibleRoles[role] === "optional"
                    ? () => setValue(role, null)
                    : undefined
                }
              />
            ))}
          </div>

          {optionalRolesByTab[activeTab].some(
            (role) => watch(role) === null,
          ) ? (
            <div className="flex flex-wrap gap-2 pt-2">
              {optionalRolesByTab[activeTab].map((role) =>
                watch(role) === null ? (
                  <button
                    key={role}
                    type="button"
                    onClick={() => toggleOptionalRole(role)}
                    disabled={disabled}
                    className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium leading-none text-slate-700 transition hover:border-slate-400 hover:bg-slate-100 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400"
                  >
                    <IconPlus
                      aria-hidden="true"
                      size={15}
                      stroke={2}
                      className="shrink-0"
                    />
                    <span className="leading-none">{`Adicionar ${ROLE_LABELS[role]}`}</span>
                  </button>
                ) : null,
              )}
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
