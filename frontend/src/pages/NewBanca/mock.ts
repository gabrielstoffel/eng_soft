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

// PPGEnFis requires extra student fields (CPF, nascimento, e-mail) and extra
// member fields (Lattes, instituição/ano de doutorado), so it needs its own mock.
const mockEnfisMember = (overrides: Partial<typeof emptyMemberForm> = {}) =>
  mockMember({
    lattes: "http://lattes.cnpq.br/1234567890",
    doctorate_institution: "UFRGS",
    doctorate_year: "2012",
    ...overrides,
  });

export const newBancaMockValuesEnfis: NewBancaFormState = {
  ppg: "ppgenfis",
  nome: { gender: 1, name: "Mariana Lopes Ferreira", cpf: "012.345.678-90", birth_date: "1996-04-22", email: "mariana.ferreira@ufrgs.br" },
  tipo: 1,
  data: "2026-08-20",
  horario: "10:00",
  modalidade: "presencial",
  sala_preferencia: "Sala de Seminários do IF",
  link: "",
  titulo: "Sequência Didática para o Ensino de Física Térmica no Ensino Médio",
  titulo2: "A Teaching Sequence for Thermal Physics in High School",
  comentario_desempenho: "Estudante com ótimo desempenho nas disciplinas do programa.",
  justificativa_membros: "Banca composta por especialistas em ensino de física.",
  orientador: mockEnfisMember({ gender: 0, name: "Paulo Roberto Nunes", institution: "UFRGS", location: "Porto Alegre, RS", email: "paulo.nunes@if.ufrgs.br" }),
  coorientador: null,
  externo1: mockEnfisMember({ gender: 1, name: "Sandra Regina Dias", institution: "PUCRS", location: "Porto Alegre, RS", email: "sandra.dias@pucrs.br" }),
  externo2: null,
  interno1: mockEnfisMember({ gender: 0, name: "Eduardo Machado", institution: "UFRGS", location: "Porto Alegre, RS", email: "eduardo.machado@if.ufrgs.br" }),
  interno2: null,
  supl_int: null,
  supl_ext: null,
};
