# Sistema de Leitura de Códigos de Barras
> Documentação completa do sistema

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Componentes do Sistema](#componentes-do-sistema)
4. [Configurações](#configurações)
5. [Guia de Uso](#guia-de-uso)
6. [Manutenção](#manutenção)
7. [Instalação](#instalação)

## 📝 Visão Geral

Sistema desenvolvido para gerenciar leitura de códigos de barras, importação de dados via Excel e monitoramento de status de produtos. O sistema oferece:

- Interface gráfica para leitura de códigos
- Monitoramento automático de arquivos Excel
- Importação dinâmica de planilhas via interface
- Feedback visual durante importações
- Geração de relatórios de importação
- Verificação automática de duplicatas na inicialização com:
  - 🔍 Detecção de duplicatas em produtos e leituras
  - 🧹 Limpeza automática de registros duplicados
  - 🔒 Adição de restrições preventivas no banco
  - ✅ Feedback visual do processo de verificação
- Visualização de resumos por status
- Remoção de leituras incorretas via interface
- Geração de relatório de controladoria por data específica
- Sistema de gerenciamento de caixas (abertura, fechamento e visualização)
- Visualização detalhada de caixas fechadas com histórico completo

## 🚀 Inicialização do Sistema

O processo de inicialização do sistema foi aprimorado para garantir maior integridade e confiabilidade dos dados:

### 1. Verificação de Integridade do Banco

```python
def verificar_integridade_banco():
    # Verifica e corrige automaticamente problemas no banco de dados
    return True
```

O sistema realiza as seguintes verificações:

1. **Detecção de Duplicatas**
   - Verifica tabela de produtos
   - Verifica tabela de leituras
   - Identifica registros duplicados

2. **Limpeza Automática**
   - Remove duplicatas encontradas
   - Mantém registro das remoções
   - Garante integridade dos dados

3. **Prevenção**
   - Adiciona restrições no banco
   - Previne futuras duplicatas
   - Otimiza estrutura do banco

### 2. Inicialização dos Componentes

```python
def main():
    # 1. Criar/verificar banco
    Database.criar_banco()
    
    # 2. Verificar integridade
    verificar_integridade_banco()
    
    # 3. Iniciar monitoramento
    monitor_thread.start()
    
    # 4. Carregar interface
    view.root.mainloop()
```

O processo segue uma sequência específica:

1. **Criação do Banco**
   - Verifica existência do banco
   - Cria tabelas necessárias
   - Configura estrutura inicial

2. **Verificação de Integridade**
   - Executa verificações automáticas
   - Corrige problemas encontrados
   - Garante consistência dos dados

3. **Monitoramento**
   - Inicia thread em background
   - Monitora pasta de importação
   - Processa arquivos novos

4. **Interface Gráfica**
   - Carrega componentes visuais
   - Configura eventos e callbacks
   - Inicia loop principal

### 3. Feedback ao Usuário

Durante a inicialização, o sistema fornece feedback visual:

- ✅ Verificações bem-sucedidas
- ⚠️ Alertas sobre problemas
- 🔄 Progresso das correções
- ❌ Erros críticos (se houver)

## 📁 Estrutura do Projeto

```
Proj/
├── 📁 app/
│   ├── 📁 assets/
│   ├── 📁 controllers/
│   ├── 📁 models/
│   ├── 📁 utils/
│   ├── 📁 views/
├── 📁 data/
│   ├── 📁 excel_importados/
│   ├── 📁 relatorios/
│   └── 📁 backup/
├── 📁 logs/
├── main.py
├── monitor_importacao_v2.py
└── verificar_duplicatas.py
```

## 🔍 Componentes do Sistema

### 1. Arquivos Principais

#### `main.py`
- **Função**: Ponto de entrada do sistema
- **Responsabilidades**:
  - Inicialização do banco de dados
  - Início do monitoramento de arquivos
  - Inicialização da interface gráfica
- **Configurações**:
  ```python
  pasta_excel = 'data/excel_importados'  # Pasta monitorada
  ```

#### `monitor_importacao_v2.py`
- **Função**: Monitoramento e processamento de arquivos Excel
- **Recursos**:
  - Monitoramento automático
  - Processamento de arquivos
  - Geração de relatórios
- **Configurações**:
  ```python
  self.PASTA_EXCEL = 'data/excel_importados'
  self.DB = 'dados.db'
  ```

#### `verificar_duplicatas.py`
- **Função**: Verificação e limpeza de duplicatas
- **Recursos**:
  - Verificação em múltiplas tabelas
  - Remoção automática
  - Adição de restrições

### 2. Módulos da Aplicação

#### Controllers (`app/controllers/`)

##### `main_controller.py`
- **Função**: Controle principal da aplicação
- **Métodos principais**:
  ```python
  def verificar_codigo(self, event):
      # Processa leitura de códigos
  
  def atualizar_dados(self):
      # Atualiza interface
  
  def atualizar_status_interface(self, serial, novo_status):
      # Atualiza status na interface
  ```

##### `resumo_controller.py`
- **Função**: Controle das telas de resumo
- **Tipos de resumo**:
  - Pendentes
  - Em Andamento
  - Concluídos

##### `caixas_fechadas_controller.py`
- **Função**: Controle de gerenciamento de caixas fechadas

#### Models (`app/models/`)

##### `database.py`
- **Função**: Gerenciamento do banco de dados
- **Configurações**:
  ```python
  DB_NAME = 'dados.db'
  ```

##### `produto.py`
- **Função**: Gerenciamento de produtos
- **Métodos principais**:
  ```python
  def buscar_por_serial(serial):
      # Busca produto por serial
  ```

##### `leitura.py`
- **Função**: Gerenciamento de leituras
- **Métodos principais**:
  ```python
  def verificar_se_ja_lido(serial):
      # Verifica duplicidade
      
  def remover_leitura(serial, data_leitura, hora_leitura):
      # Remove uma leitura específica do banco
  ```

#### Utils (`app/utils/`)

##### `excel_importer.py`
- **Função**: Importação de arquivos Excel
- **Recursos**:
  - Normalização de colunas
  - Validação de dados
  - Atualização de registros

##### `excel_handler.py`
- **Função**: Manipulação de arquivos Excel
- **Recursos**:
  - Exportação de dados
  - Formatação de planilhas

##### `db_checker.py`
- **Função**: Verificação do banco de dados
- **Recursos**:
  - Verificação de integridade
  - Limpeza de duplicatas

#### Views (`app/views/`)

##### `main_view.py`
- **Função**: Interface principal
- **Componentes**:
  - Campo de leitura
  - Tabela de dados
  - Menu de contexto para remoção de leituras
  - Status da caixa atual com:
    - 📦 Ícone de status (aberta/fechada)
    - Número da caixa
    - Total de itens
    - Data/hora de fechamento (se fechada)
  - Botões de caixa com estilos personalizados:
    - 📦 Abrir Caixa (estilo Accent - verde)
    - 🔒 Fechar Caixa (estilo Warning - vermelho)
    - 📋 Caixas Fechadas (estilo Info - contorno azul)
    - ❗ Itens Sem Caixa (estilo Alert - contorno vermelho)
  - Botões de ação:
    - 📥 Importar (importação dinâmica)
    - 🔄 Atualizar
    - 📋 Pendentes
    - 🔄 Em Andamento
    - ✅ Concluídos
    - 📊 Controladoria (relatório por data)
    - 📤 Exportar
  - Estilos de botões:
    - **Accent.TButton**: Fundo verde para ações principais
    - **Warning.TButton**: Fundo vermelho para ações de cuidado
    - **Info.TButton**: Contorno azul com hover azul claro
    - **Alert.TButton**: Contorno vermelho com hover vermelho claro

##### `resumo_view.py`
- **Função**: Telas de resumo
- **Recursos**:
  - Filtros por status
  - Exportação de dados

##### `caixas_fechadas_view.py`
- **Função**: Visualização e gerenciamento de caixas fechadas
- **Recursos**:
  - Lista completa de caixas fechadas
  - Filtros por:
    - Número da caixa
    - Data de fechamento
    - Usuário que fechou
  - Visualização detalhada por caixa com:
    - Total de itens
    - Lista completa de produtos
    - Informações de quantidade programada e enviada
  - Exportação de relatórios

## ⚙️ Configurações

### Verificação de Integridade
O sistema realiza automaticamente na inicialização:
- Verificação de duplicatas em todas as tabelas
- Limpeza automática de registros duplicados
- Adição de restrições para prevenir novas duplicatas

Se encontrar duplicatas, o sistema:
1. Exibe detalhes das duplicatas encontradas
2. Remove automaticamente os registros duplicados
3. Adiciona restrições no banco de dados
4. Só prossegue após garantir a integridade dos dados

### Banco de Dados
```python
# app/config.py
DB_NAME = 'dados.db'
EXCEL_DIR = 'data/excel_importados'
```

### Monitoramento
```python
# monitor_importacao_v2.py
PASTA_EXCEL = 'data/excel_importados'
PASTA_RELATORIOS = 'data/relatorios'
```

## 📖 Guia de Uso

### 1. Iniciando o Sistema
```bash
python main.py
```

O sistema executará automaticamente as seguintes etapas:
1. Criação/verificação do banco de dados
2. Verificação automática de duplicatas
   - Identifica duplicatas nas tabelas
   - Remove duplicatas encontradas
   - Adiciona restrições preventivas
3. Inicialização do monitoramento de arquivos
4. Carregamento da interface gráfica

### 2. Importando Arquivos
Existem duas formas de importar arquivos:

#### 2.1. Importação via Interface
1. Clique no botão "📥 Importar" na tela principal
2. Selecione o arquivo Excel desejado
3. Aguarde o processamento (uma tela de progresso será exibida)
4. O sistema mostrará um resumo da importação
5. Os dados serão atualizados automaticamente

#### 2.2. Importação via Pasta Monitorada
1. Coloque arquivos Excel em `data/excel_importados`
2. O sistema processará automaticamente
3. Relatórios serão gerados em `data/relatorios`

### 3. Gerenciamento de Caixas

#### 3.1. Abrindo uma Nova Caixa
1. Clique no botão "📦 Abrir Caixa"
2. Digite o número da nova caixa
3. A caixa será aberta e aparecerá no status

#### 3.2. Fechando uma Caixa
1. Com uma caixa aberta, clique em "🔒 Fechar Caixa"
2. O sistema registrará:
   - Data e hora do fechamento
   - Total de itens
   - Usuário que fechou

#### 3.3. Visualizando Caixas Fechadas
1. Clique no botão "📋 Caixas Fechadas"
2. Na tela de caixas fechadas você pode:
   - Ver todas as caixas fechadas
   - Filtrar por número, data ou usuário
   - Visualizar detalhes de cada caixa
   - Exportar relatórios
   - Reabrir caixas fechadas (limite de 2 reaberturas por caixa)

#### 3.4. Reabrindo uma Caixa Fechada
1. Na tela de caixas fechadas:
   - Clique com botão direito na caixa desejada
   - Selecione "🔓 Reabrir Caixa"
   - Confirme a reabertura
2. Limitações:
   - Cada caixa pode ser reaberta no máximo 2 vezes
   - O sistema mantém o histórico de reaberturas
   - A data e hora de reabertura são registradas

#### 3.5. Detalhes da Caixa
Dê um duplo clique em uma caixa para ver:
- Número da caixa
- Total de itens
- Lista completa de produtos com:
  - Serial
  - Pedido
  - Item
  - Máquina
  - Linha
  - Data/Hora da leitura

### 4. Lendo Códigos
1. Use o campo de leitura na tela principal
2. O sistema verificará duplicidades
3. Status será atualizado automaticamente

### 5. Removendo Leituras Incorretas
1. **Via Menu de Contexto**:
   - Clique com botão direito na leitura desejada
   - Selecione "🗑️ Remover Leitura"
   - Confirme a remoção

2. **Via Teclado**:
   - Selecione a leitura na tabela
   - Pressione a tecla Delete
   - Confirme a remoção

3. **Observações**:
   - A remoção é permanente e não pode ser desfeita
   - A interface é atualizada automaticamente após a remoção
   - Um feedback visual é mostrado após a operação

### 6. Verificando Duplicatas
```bash
python verificar_duplicatas.py
```

### 7. Gerando Relatório de Controladoria
1. Clique no botão "📊 Controladoria" na tela principal
2. Selecione a data desejada no calendário
3. O sistema gerará um relatório Excel com as seguintes colunas:
   - Txt.cab.doc. (vazio)
   - Tipo de Movimento (Z41)
   - Material (itens)
   - Centro De (6112)
   - Depósito De (SB01)
   - Centro Para (6112)
   - Depósito Para (SB01)
   - Ordem Cliente De (vazio)
   - Item da Ordem Cliente De (vazio)
   - Ordem Cliente Para (vazio)
   - Item da Ordem Cliente Para (vazio)
   - Quantidade (total por item)
   - Fornecedor (BP6118)
   - IVA (K1)
4. O arquivo será salvo com o nome `Relatorio_Controladoria_DD_MM_YYYY.xlsx`
5. Os dados serão consolidados por item para a data selecionada

**Observações do Relatório de Controladoria:**
- O relatório considera apenas as leituras da data selecionada
- As quantidades são somadas por item
- O nome do arquivo inclui a data selecionada
- Se não houver dados para a data, o sistema informará ao usuário

## 🔧 Manutenção

### Alterações Comuns

#### 1. Mudar Pasta de Importação
```python
# monitor_importacao_v2.py
self.PASTA_EXCEL = 'novo/caminho'
```

#### 2. Modificar Formato de Relatório
```python
# monitor_importacao_v2.py
def _gerar_relatorio(self):
    # Altere o formato aqui
```

#### 3. Adicionar Novo Status
```python
# app/models/produto.py
STATUS_CHOICES = ['PENDENTE', 'EM ANDAMENTO', 'CONCLUÍDO', 'NOVO_STATUS']
```

#### 4. Configurar Verificação de Integridade
```python
# app/utils/db_checker.py
def verificar_duplicatas():
    # Personalizar verificações aqui

def limpar_duplicatas():
    # Personalizar processo de limpeza

def adicionar_restricoes():
    # Adicionar novas restrições
```

### Boas Práticas

1. **Backup**
   - Faça backup do banco regularmente
   - Mantenha cópias dos arquivos importantes
   - Execute verificação de integridade após restaurações

2. **Logs**
   - Verifique logs de importação
   - Monitore relatórios gerados
   - Acompanhe logs de verificação de integridade

3. **Manutenção**
   - Execute verificação de duplicatas periodicamente
   - Mantenha o banco otimizado
   - Monitore o desempenho das verificações

4. **Atualizações**
   - Teste mudanças em ambiente de desenvolvimento
   - Documente alterações realizadas
   - Verifique impacto nas restrições do banco

## ⚠️ Observações Importantes

1. O sistema mantém logs detalhados em `data/relatorios`
2. Arquivos Excel são processados automaticamente
3. Duplicatas são verificadas em dois momentos:
   - Na inicialização do sistema (verificação completa)
   - Em tempo real durante as operações
4. Interface atualiza automaticamente com mudanças

## 🆘 Solução de Problemas

### Problemas Comuns

1. **Arquivo não processado**
   - Verifique formato do arquivo (.xlsx ou .xls)
   - Confirme estrutura das colunas

2. **Duplicatas não identificadas**
   - Execute `verificar_duplicatas.py`
   - Verifique restrições do banco

3. **Interface não atualiza**
   - Use botão de atualização
   - Verifique conexão com banco

### Contato e Suporte

Para suporte adicional ou dúvidas, consulte a documentação técnica ou entre em contato com Washington. 

## 📥 Instalação

### Requisitos Mínimos
- Windows 10 ou superior
- 4GB de RAM
- 100MB de espaço em disco
- Python 3.8 ou superior (apenas para desenvolvimento)

### Opções de Instalação

#### 1. Usando o Instalador Gráfico (Recomendado)
1. Execute o arquivo `Instalador_LeitorCodigoBarras.exe`
2. Siga os passos do assistente de instalação:
   
   **Passo 1: Local de Instalação**
   - Escolha onde o sistema será instalado
   - Por padrão: `C:\Users\[SEU_USUARIO]\LeitorCodigoBarras`
   
   **Passo 2: Opções de Atalhos**
   - Escolha criar atalho na área de trabalho
   - Escolha criar atalho no menu iniciar
   
   **Passo 3: Confirmação**
   - Revise as configurações escolhidas
   - Clique em "Instalar" para iniciar a instalação

3. O instalador irá:
   - Criar a estrutura de pastas necessária
   - Copiar todos os arquivos do sistema
   - Inicializar o banco de dados
   - Criar os atalhos selecionados
   - Configurar as permissões necessárias

#### 2. Instalação Manual (Para Desenvolvedores)
1. Clone o repositório ou extraia os arquivos
2. Execute `python build.py` para criar os executáveis
3. Execute `python instalador_simples.py` para instalar
4. Ou copie manualmente os arquivos da pasta `dist` para o local desejado

### Estrutura após Instalação
```
[PASTA_INSTALACAO]/
├── LeitorCodigoBarras.exe
├── data/
│   ├── excel_importados/    # Pasta monitorada para importação
│   ├── relatorios/         # Relatórios gerados
│   └── backup/            # Backups automáticos
├── logs/                 # Logs do sistema
└── app/
    └── [arquivos do sistema]
```

### Primeira Execução
1. Inicie o programa pelo atalho criado
2. O sistema realizará automaticamente:
   - Criação do banco de dados (se não existir)
   - Verificação de integridade
   - Criação das pastas necessárias
   - Inicialização do monitoramento
   - Abertura da interface principal

### Verificação da Instalação
Para garantir que a instalação foi bem-sucedida:
1. Verifique se o atalho foi criado corretamente
2. Tente abrir o programa
3. Verifique se as pastas foram criadas
4. Tente importar um arquivo Excel de teste

### Solução de Problemas na Instalação

#### Problemas Comuns
1. **Erro ao criar atalhos**
   - Verifique se tem permissões de administrador
   - Use o arquivo .bat alternativo criado

2. **Erro ao inicializar banco**
   - Verifique permissões na pasta de instalação
   - Execute o programa como administrador na primeira vez

3. **Pastas não criadas**
   - Crie manualmente as pastas necessárias
   - Verifique permissões do usuário

#### Desinstalação
Para remover o sistema:
1. Feche o programa se estiver aberto
2. Delete a pasta de instalação
3. Delete os atalhos criados
4. (Opcional) Delete a pasta de dados se não precisar mais

### Atualizações
Para atualizar o sistema:
1. Faça backup da pasta `data`
2. Desinstale a versão atual
3. Instale a nova versão
4. Restaure a pasta `data` se necessário 

## 🔄 Fluxo de Funcionamento do Sistema

### Diagrama de Fluxo Principal
```mermaid
graph TD
    A[Início do Sistema] --> B[Inicialização do Banco]
    B --> C[Iniciar Monitor de Arquivos]
    B --> D[Iniciar Interface Gráfica]
    
    C --> E{Novo Arquivo Excel?}
    E -->|Sim| F[Processar Arquivo]
    F --> G[Gerar Log]
    G --> E
    
    D --> H[Tela Principal]
    H --> I[Resumo]
    H --> J[Caixas Fechadas]
    H --> K[Itens sem Caixa]
    H --> L[Códigos não Identificados]
    
    I --> M[Atualizar Dados]
    J --> M
    K --> M
    L --> M
    
    M --> N[Salvar no Banco]
    N --> O[Gerar Relatório]
  ```

### Fluxos Detalhados

#### 1. Inicialização do Sistema
1. **Verificação Inicial**
   - Sistema inicia (`main.py`)
   - Verifica existência do banco
   - Realiza verificação de integridade
   - Inicia thread de monitoramento

2. **Preparação do Ambiente**
   - Cria diretórios necessários
   - Configura monitoramento
   - Carrega interface principal

#### 2. Fluxo de Importação de Dados
1. **Recebimento do Arquivo**
   - Arquivo Excel colocado em `data/excel_importados`
   - Monitor detecta novo arquivo automaticamente

2. **Processamento**
   - Validação do formato
   - Leitura das colunas necessárias
   - Normalização dos dados
   - Importação para o banco

3. **Finalização**
   - Geração de relatório de importação
   - Movimentação do arquivo processado
   - Atualização da interface

#### 3. Fluxo de Leitura de Códigos
1. **Entrada do Código**
   - Leitura via scanner ou digitação
   - Validação do formato do código

2. **Processamento**
   - Verificação no banco de dados
   - Validação de duplicidade
   - Registro da leitura

3. **Feedback**
   - Atualização da interface
   - Indicação visual do status
   - Som de confirmação/erro

#### 4. Fluxo de Gerenciamento de Caixas
1. **Abertura de Caixa**
   - Usuário inicia nova caixa
   - Sistema registra número e data
   - Interface atualiza status

2. **Durante Operação**
   - Leituras associadas à caixa
   - Contagem em tempo real
   - Validações automáticas

3. **Fechamento**
   - Confirmação de fechamento
   - Geração de relatório
   - Registro no histórico

#### 5. Fluxo de Geração de Relatórios
1. **Tipos de Relatórios**
   - Importação
   - Caixas fechadas
   - Controladoria
   - Status geral

2. **Processo de Geração**
   - Coleta de dados do banco
   - Formatação conforme modelo
   - Salvamento em Excel

3. **Armazenamento**
   - Pasta específica por tipo
   - Nomenclatura padronizada
   - Backup automático

### Exemplos de Uso

#### Exemplo 1: Importação e Leitura
1. Coloque planilha em `data/excel_importados`
2. Sistema processa automaticamente
3. Abra uma caixa nova
4. Comece a ler os códigos
5. Sistema valida contra planilha
6. Feche a caixa ao terminar

#### Exemplo 2: Relatório de Controladoria
1. Clique em "Controladoria"
2. Selecione a data desejada
3. Sistema gera relatório formatado
4. Arquivo salvo em `data/relatorios`

#### Exemplo 3: Gerenciamento de Caixas
1. Abra nova caixa (botão verde)
2. Faça leituras normalmente
3. Monitore quantidade na interface
4. Feche caixa quando completa
5. Acesse histórico se necessário

### Pontos de Atenção
1. **Importação**
   - Formato correto da planilha
   - Colunas necessárias
   - Dados consistentes

2. **Leitura**
   - Código válido
   - Caixa aberta
   - Status correto

3. **Relatórios**
   - Pasta com permissão
   - Espaço em disco
   - Formato correto

4. **Caixas**
   - Uma caixa por vez
   - Fechamento correto
   - Backup dos dados

