# Instruções de Instalação - Leitor de Código de Barras

## Instalação Sem Privilégios Administrativos

Este é um guia para instalar o sistema sem necessidade de privilégios de administrador.

### Pré-requisitos
- Windows 7 ou superior
- 100MB de espaço livre em disco
- Acesso à sua pasta de usuário

### Passos para Instalação

1. **Compilar o Instalador**
   - Execute o arquivo `compilar_instalador.py`
   - Aguarde a criação do instalador
   - O instalador será gerado em `dist/Instalador_LeitorCodigoBarras.exe`

2. **Executar o Instalador**
   - Execute o arquivo `Instalador_LeitorCodigoBarras.exe`
   - Escolha o diretório de instalação (recomendado: pasta do usuário)
   - Selecione as opções desejadas (atalhos)
   - Clique em "Instalar"
   - Aguarde a conclusão do processo

### Localização dos Arquivos

O sistema será instalado com a seguinte estrutura:
```
📁 [Diretório escolhido]
 ├── 📄 LeitorCodigoBarras.exe
 ├── 📁 data
 │   ├── 📁 excel_importados
 │   ├── 📁 relatorios
 │   └── 📁 backup
 └── 📁 logs
```

### Observações Importantes

1. **Diretório de Instalação**
   - Recomendamos instalar na sua pasta de usuário
   - Evite instalar em `Program Files` ou `Program Files (x86)`
   - O diretório escolhido deve ter permissões de escrita

2. **Atalhos**
   - Serão criados na área de trabalho e/ou menu iniciar
   - Se houver erro na criação dos atalhos, serão criados arquivos .bat

3. **Primeira Execução**
   - O banco de dados será inicializado automaticamente
   - As pastas necessárias serão criadas
   - O sistema estará pronto para uso

4. **Backup**
   - Os backups são salvos em `data/backup`
   - São realizados automaticamente a cada 24 horas
   - Mantém os últimos 7 backups

### Solução de Problemas

1. **Erro ao criar atalhos**
   - Use os arquivos .bat gerados como alternativa
   - Os arquivos .bat funcionam da mesma forma que os atalhos

2. **Erro de permissão**
   - Certifique-se de escolher um diretório com permissões de escrita
   - Evite diretórios do sistema

3. **Erro ao iniciar**
   - Verifique se todos os arquivos foram copiados
   - Tente executar o programa como administrador

### Suporte

Em caso de problemas:
1. Verifique os logs em `logs/instalacao.log`
2. Contate o suporte técnico
3. Forneça os logs e descrição do problema

### Desinstalação

Para desinstalar:
1. Delete a pasta de instalação
2. Remova os atalhos criados
3. (Opcional) Faça backup dos dados antes 