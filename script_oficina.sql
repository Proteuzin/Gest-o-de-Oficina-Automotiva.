CREATE DATABASE oficina_automnotiva;

GO


CREATE TABLE usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL
);

CREATE TABLE clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(255) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100)
);

CREATE TABLE veiculos (
    id_veiculo INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT NOT NULL,
    placa VARCHAR(10) NOT NULL UNIQUE,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    ano INT NOT NULL,
    CONSTRAINT fk_veiculo_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

CREATE TABLE agendamentos (
    id_agendamento INT IDENTITY(1,1) PRIMARY KEY,
    id_veiculo INT NOT NULL,
    data_agendamento DATETIME NOT NULL,
    descricao_servico VARCHAR(255) NOT NULL,
    status VARCHAR(30) DEFAULT 'Agendado',
    CONSTRAINT fk_agendamento_veiculo FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
);
GO

-- População mínima exigida: 3 registros por tabela
INSERT INTO usuarios (nome, email, senha_hash) VALUES
('Eliel', 'eliel@oficina.com', '$2b$10$8K1p/a0dL1LXMIgoEDFrwOfMQ16.E1.N6F/2H3R7q9H2Z5W4K8P9e'),
('Valdenilson', 'valdenilson@oficina.com', '$2b$10$8K1p/a0dL1LXMIgoEDFrwOfMQ16.E1.N6F/2H3R7q9H2Z5W4K8P9e'),
('Mariana Costa', 'mariana@oficina.com', '$2b$10$8K1p/a0dL1LXMIgoEDFrwOfMQ16.E1.N6F/2H3R7q9H2Z5W4K8P9e');

INSERT INTO clientes (nome, cpf, telefone, email) VALUES
('João Silva', '111.222.333-44', '(79) 99999-1010', 'joao@email.com'),
('Maria Santos', '222.333.444-55', '(79) 99999-2020', 'maria@email.com'),
('Pedro Oliveira', '333.444.555-66', '(79) 99999-3030', 'pedro@email.com');

INSERT INTO veiculos (id_cliente, placa, marca, modelo, ano) VALUES
(1, 'ABC1D23', 'Fiat', 'Argo', 2021),
(2, 'DEF4G56', 'Hyundai', 'HB20', 2022),
(3, 'GHI7J89', 'Chevrolet', 'Tracker', 2023);

INSERT INTO agendamentos (id_veiculo, data_agendamento, descricao_servico, status) VALUES
(1, '2026-11-20T09:00:00', 'Troca de óleo e filtro de ar', 'Agendado'),
(2, '2026-11-21T14:30:00', 'Revisão de pastilhas de freio', 'Agendado'),
(3, '2026-11-22T10:00:00', 'Alinhamento e balanceamento', 'Agendado');
GO
