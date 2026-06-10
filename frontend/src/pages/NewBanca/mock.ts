import { emptyMemberForm, type NewBancaFormState } from "../../types/new-banca.ts";

const mockMember = (overrides: Partial<typeof emptyMemberForm> = {}) => ({
  ...emptyMemberForm,
  ...overrides,
});

export const newBancaMockValues: NewBancaFormState = {
  ppg: "ppgfis",
  nome: { gender: 0, name: "João da Silva", cpf: "", birth_date: "", email: "" },
  tipo: 1,
  data: "2026-08-15",
  horario: "14:00",
  modalidade: "hibrida",
  sala_preferencia: "Sala de videoconferências",
  link: "https://mconf.ufrgs.br/ppgfis",
  titulo: "Estudo de Propriedades Quânticas em Sistemas de Baixa Dimensão",
  titulo2: "Study of Quantum Properties in Low-Dimensional Systems",
  comentario_desempenho: "Aluno com excelente desempenho acadêmico.",
  justificativa_membros: "Os membros foram escolhidos pela expertise na área.",
  orientador: mockMember({ gender: 0, name: "Carlos Eduardo Souza", institution: "UFRGS", location: "Porto Alegre, RS", email: "carlos@if.ufrgs.br" }),
  coorientador: null,
  externo1: mockMember({ gender: 1, name: "Ana Paula Costa", institution: "USP", location: "São Paulo, SP", email: "ana@usp.br" }),
  externo2: null,
  interno1: mockMember({ gender: 0, name: "Pedro Santos", institution: "UFRGS", location: "Porto Alegre, RS", email: "pedro@if.ufrgs.br" }),
  interno2: mockMember({ gender: 1, name: "Maria Oliveira", institution: "UFRGS", location: "Porto Alegre, RS", email: "maria@if.ufrgs.br" }),
  supl_int: mockMember({ gender: 0, name: "Lucas Almeida", institution: "UFRGS", location: "Porto Alegre, RS", email: "lucas@if.ufrgs.br" }),
  supl_ext: null,
};
