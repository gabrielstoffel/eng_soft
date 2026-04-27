from dataclasses import dataclass


@dataclass
class BancaError:
    message: str


@dataclass
class DocumentGenerationError(BancaError): ...


@dataclass
class EmailError(BancaError):
    recipient: str


@dataclass
class PersistenceError(BancaError): ...


@dataclass
class BancaNotFoundError(BancaError): ...


@dataclass
class BancaAlreadyDecidedError(BancaError):
    current_status: str
