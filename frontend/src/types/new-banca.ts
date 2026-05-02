import { z } from 'zod'

export const genderSchema = z.union([z.literal(0), z.literal(1)])

export const genderLabelByValue = {
  0: 'Masculino',
  1: 'Feminino',
} as const

export const bancaTypeSchema = z.union([z.literal(1), z.literal(2), z.literal(3)])

export const bancaTypeLabelByValue = {
  1: 'Dissertação de Mestrado',
  2: 'Exame de Qualificação ao Doutorado',
  3: 'Tese de Doutorado',
} as const

export const studentInfoSchema = z.object({
  gender: genderSchema,
  name: z.string(),
})

export const memberInfoSchema = z.object({
  gender: genderSchema,
  name: z.string(),
  institution: z.string(),
  location: z.string(),
  lang: z.string(),
  email: z.string().nullable(),
})

export const memberFormSchema = z.object({
  gender: genderSchema,
  name: z.string(),
  institution: z.string(),
  location: z.string(),
  lang: z.string(),
  email: z.string(),
})

export const newBancaFormStateSchema = z.object({
  nome: z.object({
    gender: genderSchema,
    name: z.string(),
  }),
  tipo: bancaTypeSchema,
  data: z.string(),
  horario: z.string(),
  data_convite: z.string(),
  ata: z.string(),
  local_banca: z.string(),
  link: z.string(),
  orientador: memberFormSchema,
  coorientador: memberFormSchema.nullable(),
  externo1: memberFormSchema.nullable(),
  externo2: memberFormSchema.nullable(),
  interno1: memberFormSchema.nullable(),
  interno2: memberFormSchema.nullable(),
  supl_int: memberFormSchema.nullable(),
  supl_ext: memberFormSchema.nullable(),
  titulo: z.string(),
  titulo2: z.string(),
})

export const bancaRequestSchema = z.object({
  nome: studentInfoSchema,
  tipo: bancaTypeSchema,
  data: z.string(),
  horario: z.string(),
  data_convite: z.string().nullable(),
  ata: z.number().int(),
  local_banca: z.string().nullable(),
  link: z.string().nullable(),
  orientador: memberInfoSchema,
  coorientador: memberInfoSchema.nullable(),
  externo1: memberInfoSchema.nullable(),
  externo2: memberInfoSchema.nullable(),
  interno1: memberInfoSchema.nullable(),
  interno2: memberInfoSchema.nullable(),
  supl_int: memberInfoSchema.nullable(),
  supl_ext: memberInfoSchema.nullable(),
  titulo: z.string(),
  titulo2: z.string(),
})

export const emptyMemberForm = {
  gender: 0,
  name: '',
  institution: '',
  location: '',
  lang: 'pt',
  email: '',
} satisfies MemberForm

export const newBancaDefaultValues: NewBancaFormState = {
  nome: { gender: 0, name: '' },
  tipo: 1,
  data: '',
  horario: '',
  data_convite: '',
  ata: '',
  local_banca: '',
  link: '',
  titulo: '',
  titulo2: '',
  orientador: { ...emptyMemberForm },
  coorientador: null,
  externo1: { ...emptyMemberForm },
  externo2: null,
  interno1: { ...emptyMemberForm },
  interno2: { ...emptyMemberForm },
  supl_int: null,
  supl_ext: null,
}

function serializeMemberForm(member: MemberForm | null): MemberInfo | null {
  if (!member) return null
  return {
    ...member,
    gender: member.gender,
    email: member.email || null,
  }
}

export function serializeNewBancaForm(form: NewBancaFormState): BancaRequest {
  const payload = {
    ...form,
    tipo: form.tipo,
    ata: Number(form.ata),
    nome: {
      ...form.nome,
      gender: form.nome.gender,
    },
    data_convite: form.data_convite || null,
    local_banca: form.local_banca || null,
    link: form.link || null,
    orientador: serializeMemberForm(form.orientador),
    coorientador: serializeMemberForm(form.coorientador),
    externo1: serializeMemberForm(form.externo1),
    externo2: serializeMemberForm(form.externo2),
    interno1: serializeMemberForm(form.interno1),
    interno2: serializeMemberForm(form.interno2),
    supl_int: serializeMemberForm(form.supl_int),
    supl_ext: serializeMemberForm(form.supl_ext),
  }

  return bancaRequestSchema.parse(payload)
}

export type Gender = z.infer<typeof genderSchema>
export type BancaType = z.infer<typeof bancaTypeSchema>
export type StudentInfo = z.infer<typeof studentInfoSchema>
export type MemberForm = z.infer<typeof memberFormSchema>
export type NewBancaFormState = z.infer<typeof newBancaFormStateSchema>
export type MemberInfo = z.infer<typeof memberInfoSchema>
export type BancaRequest = z.infer<typeof bancaRequestSchema>
