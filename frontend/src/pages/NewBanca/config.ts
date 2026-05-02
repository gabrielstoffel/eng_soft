import type { BancaType } from '../../types/new-banca.ts'

export type MemberRole =
  | 'orientador'
  | 'coorientador'
  | 'externo1'
  | 'externo2'
  | 'interno1'
  | 'interno2'
  | 'supl_int'
  | 'supl_ext'

export type OptionalMemberRole = Exclude<MemberRole, 'orientador'>

export type RoleMode = 'required' | 'optional' | 'hidden'

export const ALL_ROLES = [
  'orientador',
  'coorientador',
  'externo1',
  'externo2',
  'interno1',
  'interno2',
  'supl_int',
  'supl_ext',
] as const satisfies readonly MemberRole[]

export const OPTIONAL_MEMBER_ROLES = [
  'coorientador',
  'externo1',
  'externo2',
  'interno1',
  'interno2',
  'supl_int',
  'supl_ext',
] as const satisfies readonly OptionalMemberRole[]

export const ROLES_BY_TIPO: Record<BancaType, Record<MemberRole, RoleMode>> = {
  1: {
    orientador: 'required',
    coorientador: 'optional',
    externo1: 'required',
    externo2: 'hidden',
    interno1: 'required',
    interno2: 'required',
    supl_int: 'optional',
    supl_ext: 'optional',
  },
  2: {
    orientador: 'required',
    coorientador: 'optional',
    externo1: 'required',
    externo2: 'optional',
    interno1: 'required',
    interno2: 'required',
    supl_int: 'optional',
    supl_ext: 'optional',
  },
  3: {
    orientador: 'required',
    coorientador: 'optional',
    externo1: 'required',
    externo2: 'required',
    interno1: 'required',
    interno2: 'required',
    supl_int: 'optional',
    supl_ext: 'optional',
  },
}

export const ROLE_LABELS: Record<MemberRole, string> = {
  orientador: 'Orientador(a)',
  coorientador: 'Coorientador(a)',
  externo1: 'Externo 1',
  externo2: 'Externo 2',
  interno1: 'Interno 1',
  interno2: 'Interno 2',
  supl_int: 'Suplente Interno',
  supl_ext: 'Suplente Externo',
}
