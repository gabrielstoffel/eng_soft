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

export const ppgSchema = z.union([z.literal('ppgfis'), z.literal('ppgenfis')])

export const modalidadeSchema = z.union([
  z.literal('presencial'),
  z.literal('hibrida'),
  z.literal('remota'),
])

export const modalidadeLabelByValue = {
  presencial: 'Presencial',
  hibrida: 'Híbrida',
  remota: 'Remota',
} as const

export const langSchema = z.union([z.literal('pt'), z.literal('en')])

export const studentInfoSchema = z.object({
  gender: genderSchema,
  name: z.string(),
  cpf: z.string().nullable().optional(),
  birth_date: z.string().nullable().optional(),
  email: z.string().email("E-mail inválido").nullable().optional(),
})

export const memberInfoSchema = z.object({
  gender: genderSchema,
  name: z.string(),
  institution: z.string(),
  location: z.string(),
  lang: langSchema,
  email: z.string().nullable(),
  remoto: z.boolean(),
  ppg: z.string().nullable().optional(),
  bolsista_cnpq: z.boolean().nullable().optional(),
  nivel_cnpq: z.string().nullable().optional(),
  lattes: z.string().nullable().optional(),
  doctorate_institution: z.string().nullable().optional(),
  doctorate_year: z.number().nullable().optional(),
})

export const memberFormSchema = z.object({
  gender: genderSchema,
  name: z.string(),
  institution: z.string(),
  location: z.string(),
  lang: langSchema,
  email: z.string().refine((v) => v === "" || z.string().email().safeParse(v).success, { message: "E-mail inválido" }),
  remoto: z.boolean(),
  ppg: z.string(),
  bolsista_cnpq: z.boolean(),
  nivel_cnpq: z.string(),
  lattes: z.string(),
  doctorate_institution: z.string(),
  doctorate_year: z.string(),
})

export const newBancaFormStateSchema = z.object({
  ppg: ppgSchema,
  nome: z.object({
    gender: genderSchema,
    name: z.string().min(1, "Nome é obrigatório"),
    cpf: z.string(),
    birth_date: z.string(),
    email: z.string(),
  }),
  tipo: bancaTypeSchema,
  data: z.string().min(1, "Data é obrigatória"),
  horario: z.string().min(1, "Horário é obrigatório"),
  modalidade: modalidadeSchema,
  sala_preferencia: z.string(),
  link: z.string(),
  orientador: memberFormSchema,
  coorientador: memberFormSchema.nullable(),
  externo1: memberFormSchema.nullable(),
  externo2: memberFormSchema.nullable(),
  interno1: memberFormSchema.nullable(),
  interno2: memberFormSchema.nullable(),
  supl_int: memberFormSchema.nullable(),
  supl_ext: memberFormSchema.nullable(),
  titulo: z.string().min(1, "Título é obrigatório"),
  titulo2: z.string(),
  comentario_desempenho: z.string(),
  justificativa_membros: z.string(),
})

export const bancaRequestSchema = z.object({
  ppg: ppgSchema,
  nome: studentInfoSchema,
  tipo: bancaTypeSchema,
  data: z.string(),
  horario: z.string(),
  modalidade: modalidadeSchema,
  sala_preferencia: z.string().nullable(),
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
  titulo2: z.string().nullable(),
  comentario_desempenho: z.string().nullable(),
  justificativa_membros: z.string().nullable(),
})

export const emptyMemberForm: MemberForm = {
  gender: 0,
  name: '',
  institution: '',
  location: '',
  lang: 'pt',
  email: '',
  remoto: false,
  ppg: '',
  bolsista_cnpq: false,
  nivel_cnpq: '',
  lattes: '',
  doctorate_institution: '',
  doctorate_year: '',
}

export function newBancaDefaultValues(ppg: Ppg): NewBancaFormState {
  return {
    ppg,
    nome: { gender: 0, name: '', cpf: '', birth_date: '', email: '' },
    tipo: 1,
    data: '',
    horario: '',
    modalidade: 'presencial',
    sala_preferencia: '',
    link: '',
    titulo: '',
    titulo2: '',
    comentario_desempenho: '',
    justificativa_membros: '',
    orientador: { ...emptyMemberForm },
    coorientador: null,
    externo1: { ...emptyMemberForm },
    externo2: null,
    interno1: { ...emptyMemberForm },
    interno2: { ...emptyMemberForm },
    supl_int: ppg === 'ppgfis' ? { ...emptyMemberForm } : null,
    supl_ext: null,
  }
}

function serializeMemberForm(member: MemberForm | null): MemberInfo | null {
  if (!member) return null
  return {
    gender: member.gender,
    name: member.name,
    institution: member.institution,
    location: member.location,
    lang: member.lang,
    email: member.email || null,
    remoto: member.remoto,
    ppg: member.ppg || null,
    bolsista_cnpq: member.bolsista_cnpq ?? null,
    nivel_cnpq: member.nivel_cnpq || null,
    lattes: member.lattes || null,
    doctorate_institution: member.doctorate_institution || null,
    doctorate_year: member.doctorate_year ? Number(member.doctorate_year) : null,
  }
}

export function serializeNewBancaForm(form: NewBancaFormState): BancaRequest {
  return bancaRequestSchema.parse({
    ppg: form.ppg,
    nome: {
      gender: form.nome.gender,
      name: form.nome.name,
      cpf: form.nome.cpf || null,
      birth_date: form.nome.birth_date || null,
      email: form.nome.email || null,
    },
    tipo: form.tipo,
    data: form.data,
    horario: form.horario,
    modalidade: form.modalidade,
    sala_preferencia: form.sala_preferencia || null,
    link: form.link || null,
    orientador: serializeMemberForm(form.orientador),
    coorientador: serializeMemberForm(form.coorientador),
    externo1: serializeMemberForm(form.externo1),
    externo2: serializeMemberForm(form.externo2),
    interno1: serializeMemberForm(form.interno1),
    interno2: serializeMemberForm(form.interno2),
    supl_int: serializeMemberForm(form.supl_int),
    supl_ext: serializeMemberForm(form.supl_ext),
    titulo: form.titulo,
    titulo2: form.titulo2 || null,
    comentario_desempenho: form.comentario_desempenho || null,
    justificativa_membros: form.justificativa_membros || null,
  })
}

export type Ppg = z.infer<typeof ppgSchema>
export type Modalidade = z.infer<typeof modalidadeSchema>
export type Gender = z.infer<typeof genderSchema>
export type BancaType = z.infer<typeof bancaTypeSchema>
export type StudentInfo = z.infer<typeof studentInfoSchema>
export type MemberForm = z.infer<typeof memberFormSchema>
export type NewBancaFormState = z.infer<typeof newBancaFormStateSchema>
export type MemberInfo = z.infer<typeof memberInfoSchema>
export type BancaRequest = z.infer<typeof bancaRequestSchema>
